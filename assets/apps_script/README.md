# Apps Script source (mirrored)

The file `Code.gs` next to this README is a verbatim snapshot of the upstream script you deploy in your own Google Apps Script project:

- Upstream: <https://github.com/masterking32/MasterHttpRelayVPN/blob/python_testing/apps_script/Code.gs>
- Raw link: <https://raw.githubusercontent.com/masterking32/MasterHttpRelayVPN/refs/heads/python_testing/apps_script/Code.gs>

This copy lives in our repo for two reasons:

1. **Survives upstream outages**: if the user is on a network where raw.githubusercontent.com is temporarily unreachable but they can clone or ZIP this repo, they still have the deploy-ready file.
2. **Pins what we tested against**: the relay protocol between `mhrv-rs` and the script is informal; upstream changes can silently break us. Keeping a snapshot here lets us diff and see if a spec drift is responsible for any reported breakage.

All credit for `Code.gs` goes to [@masterking32](https://github.com/masterking32) — we do not modify it. If you're using mhrv-rs, follow the upstream deploy instructions in the script's header comment. The only edit **you** must make is the `AUTH_KEY` constant — set it to a strong secret and reuse that exact string in your `mhrv-rs` config.
