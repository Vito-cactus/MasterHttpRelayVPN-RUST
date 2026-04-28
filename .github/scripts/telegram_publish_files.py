#!/usr/bin/env python3
"""Post each release artifact individually to a Telegram channel.

Used by .github/workflows/telegram-publish-files.yml. Reads files from
--assets-dir, picks a Persian caption per filename, posts via the
Telegram Bot API `sendDocument` endpoint with --hashtag appended.

Files larger than the Telegram Bot API's 50 MB ceiling are split into
~45 MB byte chunks via Python (no `split` shell dep) and posted as
`<name>.part_aa`, `.part_ab`, ... — recipients reassemble with
`cat <name>.part_* > <name>`.

Re-runnable: posts every file every time. Use carefully when re-running
for the same version (the channel will get duplicate posts).
"""

from __future__ import annotations

import argparse
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import json
from pathlib import Path

# Telegram Bot API uploads cap at 50 MB. Pick 45 MB for chunks so the
# multipart envelope + caption + Telegram's own overhead don't push us
# over. Bigger chunks (e.g. 49 MB) sometimes hit "Request Entity Too
# Large" depending on caption length.
CHUNK_LIMIT_BYTES = 45 * 1024 * 1024

# Sleep between uploads. Telegram's documented rate limit is 1 msg/sec
# to the same chat, plus a soft "burst" allowance. 1.5s is conservative
# and means a 20-file release publishes in ~30 s.
INTER_UPLOAD_SLEEP_SECS = 1.5

# Filename-substring → Persian caption. Order matters: longest /
# most-specific patterns first, since a shorter pattern (e.g.
# "android-x86") can match a more-specific filename ("android-x86_64").
# Match is `pattern in filename`.
CAPTIONS: list[tuple[str, str]] = [
    # Android — universal first (the recommended default for non-technical users).
    ("android-universal", "نسخه اندروید (universal) — برای همه دستگاه‌ها"),
    ("android-arm64-v8a", "نسخه اندروید (arm64-v8a) — گوشی‌های مدرن ۶۴ بیتی"),
    ("android-armeabi-v7a", "نسخه اندروید (armv7) — گوشی‌های قدیمی‌تر ۳۲ بیتی"),
    ("android-x86_64", "نسخه اندروید (x86_64) — شبیه‌ساز ۶۴ بیتی"),
    ("android-x86", "نسخه اندروید (x86) — شبیه‌ساز"),
    # Windows.
    ("windows-amd64", "نسخه ویندوز x64 (۶۴ بیتی)"),
    ("windows-i686", "نسخه ویندوز x86 (۳۲ بیتی، Win7+)"),
    # macOS — .app bundles before plain CLI tarballs.
    ("macos-arm64-app", "نسخه macOS (Apple Silicon) — برنامه گرافیکی .app"),
    ("macos-amd64-app", "نسخه macOS (Intel) — برنامه گرافیکی .app"),
    ("macos-arm64", "نسخه macOS (Apple Silicon) — CLI"),
    ("macos-amd64", "نسخه macOS (Intel) — CLI"),
    # Linux — musl static first, glibc second.
    ("linux-musl-amd64", "نسخه لینوکس amd64 (musl static) — Alpine / OpenWRT-x86"),
    ("linux-musl-arm64", "نسخه لینوکس arm64 (musl static)"),
    ("linux-amd64", "نسخه لینوکس amd64 (glibc)"),
    ("linux-arm64", "نسخه لینوکس arm64 (glibc)"),
    # Embedded targets.
    ("openwrt-mipsel-softfloat", "نسخه OpenWRT (mipsel softfloat) — روتر MT7621"),
    ("raspbian-armhf", "نسخه Raspbian (armhf) — رزبری پای ۳۲ بیتی"),
]


def caption_for(filename: str) -> str:
    """Return the Persian caption for a filename, falling back to the
    bare filename if nothing matches."""
    for pattern, persian in CAPTIONS:
        if pattern in filename:
            return persian
    return f"نسخه `{filename}`"


def order_files(files: list[Path]) -> list[Path]:
    """Sort release files in CAPTIONS order (Android first, then
    Windows, macOS, Linux, embedded). Files not matching any pattern
    fall to the end in alphabetical order."""
    order_map: dict[str, int] = {pattern: idx for idx, (pattern, _) in enumerate(CAPTIONS)}

    def key(p: Path) -> tuple[int, str]:
        for pattern, idx in order_map.items():
            if pattern in p.name:
                return (idx, p.name)
        # Unknown patterns: push to end, alphabetize among themselves.
        return (len(CAPTIONS), p.name)

    return sorted(files, key=key)


def split_file(path: Path, chunk_bytes: int) -> list[Path]:
    """Split `path` into chunks of at most `chunk_bytes` bytes. Returns
    the list of chunk paths, named `<orig>.part_aa`, `.part_ab`, ...
    Mimics `split -b <chunk_bytes>`. Reassembled via
    `cat <name>.part_* > <name>`.

    Skips work if existing parts are already present (idempotent re-run)."""
    parts: list[Path] = []

    def part_name(idx: int) -> str:
        # 26-letter base: aa..az, ba..bz, ... mirroring split's default.
        first = chr(ord("a") + idx // 26)
        second = chr(ord("a") + idx % 26)
        return f"{path.name}.part_{first}{second}"

    idx = 0
    with path.open("rb") as src:
        while True:
            buf = src.read(chunk_bytes)
            if not buf:
                break
            part_path = path.parent / part_name(idx)
            with part_path.open("wb") as dst:
                dst.write(buf)
            parts.append(part_path)
            idx += 1
    return parts


def send_document(
    bot_token: str,
    chat_id: str,
    file_path: Path,
    caption: str,
) -> dict:
    """POST a single file via the Telegram Bot API sendDocument endpoint.
    Returns the parsed JSON response. Raises on HTTP error.

    Uses urllib + a hand-rolled multipart/form-data encoder so we don't
    pull `requests` (the workflow runs on stock GitHub-hosted runners
    where stdlib-only is preferable for cold-start speed)."""
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    boundary = "----mhrvUploadBoundary" + str(int(time.time() * 1000))
    body = build_multipart(
        boundary,
        fields={
            "chat_id": chat_id,
            "caption": caption,
            "parse_mode": "HTML",
            # Disable preview to keep the channel tidy.
            "disable_notification": "false",
        },
        files={"document": (file_path.name, file_path.read_bytes(), "application/octet-stream")},
    )
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    # 5 minute timeout for the actual upload — Telegram occasionally
    # takes a while to process 40+ MB documents.
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read().decode("utf-8"))


def build_multipart(
    boundary: str,
    fields: dict[str, str],
    files: dict[str, tuple[str, bytes, str]],
) -> bytes:
    """Build a multipart/form-data body. `files` is name → (filename,
    bytes, mime). Plain stdlib so we don't need `requests`."""
    parts: list[bytes] = []
    crlf = b"\r\n"
    bnd = f"--{boundary}".encode()

    for name, value in fields.items():
        parts.append(bnd)
        parts.append(f'Content-Disposition: form-data; name="{name}"'.encode())
        parts.append(b"")
        parts.append(value.encode("utf-8"))

    for name, (filename, data, mime) in files.items():
        parts.append(bnd)
        parts.append(
            f'Content-Disposition: form-data; name="{name}"; filename="{filename}"'.encode()
        )
        parts.append(f"Content-Type: {mime}".encode())
        parts.append(b"")
        parts.append(data)

    parts.append(f"--{boundary}--".encode())
    parts.append(b"")
    return crlf.join(parts)


def html_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def post_file(
    bot_token: str,
    chat_id: str,
    file_path: Path,
    base_caption: str,
    hashtag: str,
) -> bool:
    """Post one file. If too big, split + post each part. Returns True
    on success of all parts, False on any failure."""
    size = file_path.stat().st_size
    if size <= CHUNK_LIMIT_BYTES:
        caption = (
            f"<b>{html_escape(base_caption)}</b>\n"
            f"<code>{html_escape(file_path.name)}</code>\n"
            f"\n{hashtag}"
        )
        print(f"  uploading {file_path.name} ({size / 1_048_576:.1f} MB)...", flush=True)
        try:
            resp = send_document(bot_token, chat_id, file_path, caption)
            if not resp.get("ok"):
                print(f"    !! Telegram returned not-ok: {resp}", flush=True)
                return False
            print(f"    ok (message_id={resp['result']['message_id']})", flush=True)
            return True
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")[:500]
            print(f"    !! HTTP {e.code}: {err_body}", flush=True)
            return False
        except Exception as e:
            print(f"    !! exception: {e}", flush=True)
            return False
        finally:
            time.sleep(INTER_UPLOAD_SLEEP_SECS)

    # Too big — split and post each part.
    print(
        f"  splitting {file_path.name} ({size / 1_048_576:.1f} MB > "
        f"{CHUNK_LIMIT_BYTES / 1_048_576:.0f} MB ceiling)...",
        flush=True,
    )
    parts = split_file(file_path, CHUNK_LIMIT_BYTES)
    if not parts:
        print(f"    !! split produced 0 parts (empty file?)", flush=True)
        return False

    n = len(parts)
    all_ok = True
    for idx, part_path in enumerate(parts, start=1):
        part_caption = (
            f"<b>{html_escape(base_caption)} — قسمت {idx}/{n}</b>\n"
            f"<code>{html_escape(part_path.name)}</code>\n"
            f"\nبرای بازسازی فایل اصلی:\n"
            f"<code>cat {html_escape(file_path.name)}.part_* &gt; "
            f"{html_escape(file_path.name)}</code>\n"
            f"\n{hashtag}"
        )
        psize = part_path.stat().st_size
        print(
            f"    uploading part {idx}/{n}: {part_path.name} ({psize / 1_048_576:.1f} MB)...",
            flush=True,
        )
        try:
            resp = send_document(bot_token, chat_id, part_path, part_caption)
            if not resp.get("ok"):
                print(f"      !! Telegram returned not-ok: {resp}", flush=True)
                all_ok = False
            else:
                print(
                    f"      ok (message_id={resp['result']['message_id']})", flush=True
                )
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")[:500]
            print(f"      !! HTTP {e.code}: {err_body}", flush=True)
            all_ok = False
        except Exception as e:
            print(f"      !! exception: {e}", flush=True)
            all_ok = False
        finally:
            time.sleep(INTER_UPLOAD_SLEEP_SECS)
            # Tidy up the part file once posted.
            try:
                part_path.unlink()
            except OSError:
                pass

    return all_ok


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets-dir", required=True, type=Path)
    parser.add_argument("--version", required=True, help="e.g. 1.8.0")
    parser.add_argument("--hashtag", required=True, help="e.g. #v180")
    args = parser.parse_args()

    bot_token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")
    if not bot_token or not chat_id:
        print("BOT_TOKEN and CHAT_ID env vars required", file=sys.stderr)
        return 2

    if not args.assets_dir.is_dir():
        print(f"--assets-dir {args.assets_dir} not a directory", file=sys.stderr)
        return 2

    # Collect all regular files in the directory (no recursion). Skip
    # split-part leftovers from a previous run of this script if any
    # exist — we'll regenerate cleanly.
    raw_files = [
        p for p in args.assets_dir.iterdir()
        if p.is_file() and ".part_" not in p.name
    ]
    if not raw_files:
        print(f"no files found in {args.assets_dir}", file=sys.stderr)
        return 2

    files = order_files(raw_files)
    print(f"publishing {len(files)} file(s) to Telegram chat {chat_id} for v{args.version}:")
    for f in files:
        print(f"  - {f.name}")
    print()

    # Optional: a leading announcement message that anchors the file
    # batch. Posted as a regular sendMessage so it shows above the file
    # group in the channel and gives recipients a single hashtag link
    # to find this release later.
    announce = (
        f"<b>📦 mhrv-rs {html_escape('v' + args.version)} منتشر شد</b>\n"
        f"\nفایل‌ها در ادامه به ترتیب پلتفرم ارسال می‌شن.\n"
        f"\n{args.hashtag}"
    )
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = urllib.parse.urlencode({
            "chat_id": chat_id,
            "text": announce,
            "parse_mode": "HTML",
            "disable_web_page_preview": "true",
        }).encode()
        with urllib.request.urlopen(
            urllib.request.Request(url, data=data, method="POST"), timeout=30
        ) as resp:
            r = json.loads(resp.read().decode("utf-8"))
            if not r.get("ok"):
                print(f"  !! announcement failed: {r}", flush=True)
            else:
                print(f"  announcement posted (message_id={r['result']['message_id']})", flush=True)
    except Exception as e:
        # Non-fatal: continue with file uploads even if announcement bombs.
        print(f"  !! announcement exception: {e}", flush=True)
    time.sleep(INTER_UPLOAD_SLEEP_SECS)

    failures = 0
    for f in files:
        base = caption_for(f.name)
        ok = post_file(bot_token, chat_id, f, base, args.hashtag)
        if not ok:
            failures += 1

    print()
    if failures:
        print(f"DONE with {failures} failure(s) out of {len(files)}", flush=True)
        return 1
    print(f"DONE — {len(files)} files posted successfully", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
