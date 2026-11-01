# 5-minute demo video

The demo is generated, not screen-recorded, so it can be re-made whenever the API or the narration changes.

| File | What it is |
| --- | --- |
| `scenes.yaml` | The script: nine scenes, the narration for each beat, and the commands and requests shown on screen |
| `app/main.py` | The app in the video: the [FastAPI quickstart](../docs/getting-started/fastapi.md) on a tiny shop |
| `app/tamper.py` | The "insider" edit that the ledger check catches |
| `demo.py` | `record` runs the script for real; `render` draws it into a video |

## Make the video

```bash
# 1. Record, in the shared dev virtualenv (needs dpdpkit[fastapi], uvicorn, httpx)
../.venv/Scripts/python demo/demo.py record      # Windows; ../.venv/bin/python elsewhere

# 2. Render, with any Python that has Pillow, plus ffmpeg on PATH
pip install pillow
python demo/demo.py render
```

`record` starts from an empty folder (`build/demo/work`), runs `dpdpkit init`, starts the app on a free
port, and runs every step. It stops with an error if any `expect`, `status` or `exit` check in
`scenes.yaml` fails, so a clean recording also tells you the quickstart still works. Every response and
command output on screen is real. Two things are adjusted for the viewer: the app's port is shown as
8000, and `pip install` is only typed, not run, because the packages are already installed.

`render` writes:

- `build/demo/dpdpkit-demo.mp4`: 1920×1080, 30 fps, H.264, captions burned in, no audio, about 4:53
- `build/demo/dpdpkit-demo.srt`: the same captions as subtitles

Rendering takes about two minutes. Pass `--keep-frames` to inspect the PNG frames, and `--mono-font` and
`--sans-font` if the default fonts are missing (Cascadia Mono or Consolas and Segoe UI on Windows; DejaVu
on Linux; Menlo and Helvetica on macOS).

## Changing it

Edit the narration or steps in `scenes.yaml`, then record and render again. Captions run at about 140
words a minute, and `render` warns if the video falls outside 4:30–5:30. Keep the claims in the
narration to things dpdpkit actually does. The recording checks the commands, but nothing checks the
words.

## Publishing (done by a maintainer)

1. Watch the whole render once.
2. Optionally record a voice-over from the `.srt` and mux it in:
   `ffmpeg -i dpdpkit-demo.mp4 -i voice.wav -c:v copy -c:a aac -shortest dpdpkit-demo-voiced.mp4`.
3. Upload the video (YouTube or similar) with the `.srt` as captions, and attach the MP4 to the v0.3
   GitHub release.
4. Link it from the docs home page and the launch posts.

The end card points at `dpdpkit-dev.github.io/dpdpkit-docs`. Switch it to `dpdpkit.dev` in `scenes.yaml`
once that domain is live.
