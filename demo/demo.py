"""Record and render the 5-minute dpdpkit demo described in demo/scenes.yaml.

  python demo/demo.py record   run every step against demo/app; writes build/demo/transcript.json
  python demo/demo.py render   draw the transcript into build/demo/dpdpkit-demo.mp4 and .srt

`record` needs dpdpkit[fastapi], uvicorn and httpx (the shared dev virtualenv has them). It fails if any
`expect`, `status` or `exit` check in scenes.yaml does not hold, so a passing recording is also a smoke test
of the quickstart. `render` needs Pillow and ffmpeg, and nothing from dpdpkit.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shlex
import shutil
import socket
import subprocess
import sys
import time
from http import HTTPStatus
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SCENES = HERE / "scenes.yaml"
APP = HERE / "app"
OUT = HERE.parent / "build" / "demo"
SHOWN_PORT = 8000  # the port viewers see; the recording uses a free one


# ---------------------------------------------------------------------------------------------- record


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def _executable(name: str) -> str:
    if name == "python":
        return sys.executable
    local = Path(sys.executable).parent / (f"{name}.exe" if os.name == "nt" else name)
    found = str(local) if local.is_file() else shutil.which(name)
    if not found:
        raise SystemExit(f"error: {name} is not installed next to {sys.executable}")
    return found


def _check(step: dict[str, Any], text: str, code: int, want_code: int, what: str) -> None:
    if code != want_code:
        raise SystemExit(f"error: `{what}` returned {code}, expected {want_code}:\n{text}")
    if "expect" in step and step["expect"] not in text:
        raise SystemExit(f"error: `{what}` output lacks {step['expect']!r}:\n{text}")


def _record_run(step: dict[str, Any], work: Path, env: dict[str, str]) -> dict[str, Any]:
    argv = shlex.split(step["run"])
    argv[0] = _executable(argv[0])
    proc = subprocess.run(  # noqa: S603 - commands come from scenes.yaml in this repo
        argv,
        cwd=work,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        timeout=180,
        check=False,
    )
    text = proc.stdout.rstrip()
    _check(step, text, proc.returncode, step.get("exit", 0), step["run"])
    lines = text.splitlines()
    if "only" in step:
        lines = [line for line in lines if any(re.search(p, line) for p in step["only"])]
    return {"kind": "term", "command": [step["run"]], "output": lines, "error": proc.returncode != 0}


def _curl(method: str, path: str, user: str | None, body: Any) -> list[str]:
    parts = ["curl"] + ([] if method == "GET" else ["-X", method]) + [f"localhost:{SHOWN_PORT}{path}"]
    if user:
        parts.append(f'-H "X-User: {user}"')
    lines = [" ".join(parts)]
    if body is not None:
        lines.append(f"""     -H "content-type: application/json" -d '{json.dumps(body, ensure_ascii=False)}'""")
    return [line + " \\" for line in lines[:-1]] + lines[-1:]


def _record_http(step: dict[str, Any], base: str, saved: dict[str, str]) -> dict[str, Any]:
    import httpx

    method, path = step["http"].split(maxsplit=1)
    path = path.format(**saved)
    headers = {"X-User": step["user"]} if "user" in step else {}
    response = httpx.request(method, base + path, headers=headers, json=step.get("json"), timeout=30)
    _check(step, response.text, response.status_code, step.get("status", 200), step["http"])
    data = response.json()
    for name, key in step.get("save", {}).items():
        saved[name] = str(data[key])
    if "fields" in step and isinstance(data, dict):
        data = {key: data[key] for key in step["fields"] if key in data}
    status = f"HTTP/1.1 {response.status_code} {HTTPStatus(response.status_code).phrase}"
    return {
        "kind": "term",
        "command": _curl(method, path, step.get("user"), step.get("json")),
        "output": [status, *json.dumps(data, indent=2, ensure_ascii=False).splitlines()],
        "error": response.status_code >= 400,
    }


def _record_show(step: dict[str, Any], work: Path) -> dict[str, Any]:
    lines = (work / step["show"]).read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if re.search(step["from"], line)) if "from" in step else 0
    end = len(lines)
    if "to" in step:
        end = next((i for i in range(start + 1, len(lines)) if re.search(step["to"], lines[i])), end)
    excerpt = lines[start:end]
    while excerpt and not excerpt[-1].strip():
        excerpt.pop()
    return {"kind": "file", "file": step["show"], "first_line": start + 1, "lines": excerpt}


def _start_server(work: Path, env: dict[str, str], port: int) -> tuple[subprocess.Popen[bytes], dict[str, Any]]:
    import httpx

    log = (work / "uvicorn.log").open("wb")
    proc = subprocess.Popen(  # noqa: S603
        [sys.executable, "-m", "uvicorn", "main:app", "--port", str(port)],
        cwd=work,
        env=env,
        stdout=log,
        stderr=subprocess.STDOUT,
    )
    deadline = time.monotonic() + 60
    while True:
        if proc.poll() is not None:
            raise SystemExit(f"error: uvicorn exited:\n{(work / 'uvicorn.log').read_text(encoding='utf-8')}")
        try:
            httpx.get(f"http://127.0.0.1:{port}/dpdp/notices/current", timeout=2)
            break
        except httpx.TransportError:
            if time.monotonic() > deadline:
                raise SystemExit("error: uvicorn did not start within 60 s") from None
            time.sleep(0.3)
    text = (work / "uvicorn.log").read_text(encoding="utf-8").replace(f":{port}", f":{SHOWN_PORT}")
    output = [line for line in text.splitlines() if ' - "' not in line]  # drop the readiness probe's access log
    return proc, {"kind": "term", "command": ["uvicorn main:app"], "output": output, "error": False}


def record(_: argparse.Namespace) -> None:
    import yaml

    scenes = yaml.safe_load(SCENES.read_text(encoding="utf-8"))["scenes"]
    work = OUT / "work"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    for source in APP.glob("*.py"):
        shutil.copy(source, work)
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    port = _free_port()
    server: subprocess.Popen[bytes] | None = None
    saved: dict[str, str] = {}
    recorded = []
    try:
        for scene in scenes:
            steps = []
            for step in scene["steps"]:
                if "run" in step:
                    rec = _record_run(step, work, env)
                elif "http" in step:
                    rec = _record_http(step, f"http://127.0.0.1:{port}", saved)
                elif "show" in step:
                    rec = _record_show(step, work)
                elif "type" in step:
                    rec = {"kind": "term", "command": [step["type"]], "output": [], "error": False}
                elif step.get("server") == "start":
                    server, rec = _start_server(work, env, port)
                else:
                    rec = {"kind": "say"}
                rec["say"] = " ".join(step.get("say", "").split())
                steps.append(rec)
                print(f"  ok  {scene['title']}: {(rec.get('command') or [rec.get('file', '')])[0]}")
            recorded.append({"title": scene["title"], "card": scene.get("card"), "steps": steps})
    finally:
        if server is not None:
            server.terminate()
            server.wait(timeout=30)
    packages = {}
    for name in ("dpdpkit-core", "dpdpkit-fastapi", "dpdpkit-policies"):
        try:
            packages[name] = version(name)
        except PackageNotFoundError:
            packages[name] = "not installed"
    transcript = {"recorded_at": dt.datetime.now(dt.timezone.utc).isoformat(), "packages": packages, "scenes": recorded}
    out = OUT / "transcript.json"
    out.write_text(json.dumps(transcript, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {out} ({', '.join(f'{k} {v}' for k, v in packages.items())})")


# ---------------------------------------------------------------------------------------------- render

W, H = 1920, 1080
WORDS_PER_SECOND = 2.3  # about 140 words a minute: time to read the caption and glance at the screen
BG, PANEL, BAR = "#0b1220", "#111827", "#1f2937"
TEXT, MUTED, ACCENT, GOOD, BAD, COMMENT = "#f1f5f9", "#94a3b8", "#38bdf8", "#4ade80", "#f87171", "#6b8f71"
TERM = (60, 110, 1860, 840)  # left, top, right, bottom
FONTS = {
    "mono": [
        "C:/Windows/Fonts/CascadiaMono.ttf",
        "C:/Windows/Fonts/consola.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/System/Library/Fonts/Menlo.ttc",
    ],
    "sans": [
        "C:/Windows/Fonts/segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ],
    "bold": [
        "C:/Windows/Fonts/segoeuib.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ],
}


class Painter:
    """Draws one 1920×1080 frame of the demo from the current scene state."""

    def __init__(self, fonts: dict[str, str | None], total: float, scenes: int) -> None:
        from PIL import ImageFont

        def font(kind: str, size: int) -> Any:
            path = fonts[kind]
            return ImageFont.truetype(path, size) if path else ImageFont.load_default(size)

        self.mono, self.sans, self.caption = font("mono", 26), font("sans", 28), font("sans", 40)
        self.title, self.card_big, self.card = font("bold", 36), font("bold", 120), font("sans", 46)
        self.card_mono = font("mono", 40)
        self.total, self.scenes = total, scenes
        self.char_w = self.mono.getlength("M")
        self.line_h = 32
        self.cols = int((TERM[2] - TERM[0] - 48) / self.char_w)
        self.rows = (TERM[3] - TERM[1] - 70) // self.line_h

    def frame(self, state: dict[str, Any], caption: str, at: float) -> Any:
        from PIL import Image, ImageDraw

        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        d.rectangle((0, 0, W, 80), fill=PANEL)
        d.text((60, 40), state["title"], font=self.title, fill=TEXT, anchor="lm")
        d.text((W - 60, 40), f"dpdpkit  ·  {state['index']}/{self.scenes}", font=self.sans, fill=MUTED, anchor="rm")
        d.rectangle((0, 80, int(W * min(at / self.total, 1)), 84), fill=ACCENT)
        if state.get("card"):
            self._card(d, state["card"])
        elif state.get("file"):
            self._window(d, state["file"]["file"], self._file_lines(state["file"]))
        else:
            self._window(d, "bash — chai-shop", self._term_lines(state["term"]))
        if caption:
            self._caption(d, caption)
        return img

    def _card(self, d: Any, lines: list[str]) -> None:
        d.text((W / 2, 380), lines[0], font=self.card_big, fill=TEXT, anchor="mm")
        y = 520
        for line in lines[1:]:
            mono = line.startswith("pip ")
            d.text(
                (W / 2, y),
                line,
                font=self.card_mono if mono else self.card,
                fill=ACCENT if mono else MUTED,
                anchor="mm",
            )
            y += 72

    def _window(self, d: Any, label: str, lines: list[tuple[str, str]]) -> None:
        left, top, right, _ = TERM
        d.rounded_rectangle(TERM, radius=14, fill=PANEL, outline=BAR, width=2)
        d.rounded_rectangle((left, top, right, top + 44), radius=14, fill=BAR)
        d.rectangle((left, top + 30, right, top + 44), fill=BAR)
        for i, colour in enumerate(("#f87171", "#fbbf24", "#4ade80")):
            d.ellipse((left + 20 + i * 26, top + 15, left + 34 + i * 26, top + 29), fill=colour)
        d.text(((left + right) / 2, top + 22), label, font=self.sans, fill=MUTED, anchor="mm")
        y = top + 64
        for text, colour in lines[-self.rows :]:
            d.text((left + 24, y), text, font=self.mono, fill=colour)
            y += self.line_h

    def _wrap(self, text: str, colour: str, indent: str = "") -> list[tuple[str, str]]:
        """Soft-wrap to the terminal width, at a space when there is one in the second half of the line."""
        out, width = [], self.cols
        while len(text) > width:
            cut = text.rfind(" ", width // 2, width)
            cut = cut + 1 if cut > 0 else width
            out.append((text[:cut].rstrip(), colour))
            text, width = indent + text[cut:], self.cols
        return [*out, (text, colour)]

    def _term_lines(self, entries: list[dict[str, Any]]) -> list[tuple[str, str]]:
        """The newest commands that fit, each with its output; the current command always stays on screen."""
        lines: list[tuple[str, str]] = []
        for n, entry in enumerate(reversed(entries)):
            block: list[tuple[str, str]] = []
            for i, cmd in enumerate(entry["command"]):
                block += self._wrap(("$ " if i == 0 else "  ") + cmd, TEXT, "    ")
            for out in entry.get("output", []):
                colour = BAD if entry["error"] else (GOOD if out.startswith(("ok:", "HTTP/1.1 2")) else MUTED)
                block += self._wrap(out, colour)
            if n == 0 and len(block) > self.rows:
                return [*block[: self.rows - 1], ("…", MUTED)]
            if len(lines) + len(block) + (1 if lines else 0) > self.rows:
                break
            lines = block + ([("", TEXT)] if lines else []) + lines
        return lines

    def _file_lines(self, shown: dict[str, Any]) -> list[tuple[str, str]]:
        lines: list[tuple[str, str]] = []
        for i, line in enumerate(shown["lines"]):
            colour = COMMENT if line.lstrip().startswith("#") else TEXT
            lines += self._wrap(f"{shown['first_line'] + i:>3}  {line}", colour, "     ")
        return lines[: self.rows]

    def caption_lines(self, text: str) -> list[str]:
        lines, current = [], ""
        for word in text.split():
            trial = f"{current} {word}".strip()
            if current and self.caption.getlength(trial) > W - 320:
                lines.append(current)
                current = word
            else:
                current = trial
        return [*lines, current] if current else lines

    def _caption(self, d: Any, text: str) -> None:
        lines = self.caption_lines(text)
        height = 56 * len(lines) + 28
        top = 960 - height / 2
        width = max(self.caption.getlength(line) for line in lines) + 60
        d.rounded_rectangle(((W - width) / 2, top, (W + width) / 2, top + height), radius=12, fill="#000000")
        for i, line in enumerate(lines):
            d.text((W / 2, top + 14 + 28 + 56 * i), line, font=self.caption, fill=TEXT, anchor="mm")


def _chunks(painter: Painter, say: str) -> list[str]:
    """Split narration into captions of at most two lines, breaking at sentences, then commas, then words."""
    if not say:
        return []
    pieces = []
    for sentence in re.split(r"(?<=[.!?])\s+", say):
        if len(painter.caption_lines(sentence)) <= 2:
            pieces.append(sentence)
            continue
        current = ""
        for part in re.split(r"(?<=,)\s+|\s+", sentence):
            trial = f"{current} {part}".strip()
            if current and len(painter.caption_lines(trial)) > 2:
                pieces.append(current)
                current = part
            else:
                current = trial
        pieces.append(current)
    chunks: list[str] = []
    for piece in pieces:
        if chunks and len(painter.caption_lines(f"{chunks[-1]} {piece}")) <= 2:
            chunks[-1] = f"{chunks[-1]} {piece}"
        else:
            chunks.append(piece)
    return chunks


def _seconds(text: str) -> float:
    return max(1.8, len(text.split()) / WORDS_PER_SECOND + 0.8)


def _timeline(painter: Painter, scenes: list[dict[str, Any]]) -> list[tuple[dict[str, Any], str, float]]:
    """Every distinct frame as (screen state, caption, duration)."""
    frames: list[tuple[dict[str, Any], str, float]] = []
    for index, scene in enumerate(scenes, 1):
        term: list[dict[str, Any]] = []
        state: dict[str, Any] = {"title": scene["title"], "index": index, "card": scene.get("card"), "term": term}
        for step in scene["steps"]:
            chunks = _chunks(painter, step["say"]) or [""]
            durations = [_seconds(c) if c else 1.2 for c in chunks]
            if step["kind"] == "term":
                typed = "\n".join(step["command"])
                ticks = min(14, max(4, len(typed) // 8))
                lead = 0.0
                for t in range(1, ticks + 1):
                    partial = typed[: round(len(typed) * t / ticks)].split("\n")
                    snap = {**state, "file": None, "term": [*term, {**step, "command": partial, "output": []}]}
                    frames.append((snap, chunks[0], 0.05))
                    lead += 0.05
                frames.append(({**state, "file": None, "term": [*term, {**step, "output": []}]}, chunks[0], 0.35))
                durations[0] = max(1.0, durations[0] - lead - 0.35)
                term.append(step)
                state = {**state, "file": None, "term": list(term)}
            elif step["kind"] == "file":
                state = {**state, "file": step}
            for chunk, seconds in zip(chunks, durations, strict=True):
                frames.append((state, chunk, seconds))
        frames.append((state, "", 0.6))
    return frames


def _srt_time(seconds: float) -> str:
    ms = round(seconds * 1000)
    return f"{ms // 3_600_000:02}:{ms // 60_000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def render(args: argparse.Namespace) -> None:
    transcript_path = OUT / "transcript.json"
    if not transcript_path.is_file():
        raise SystemExit(f"error: no {transcript_path}; run `python demo/demo.py record` first")
    ffmpeg = args.ffmpeg or shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("error: ffmpeg not found; install it or pass --ffmpeg PATH")
    scenes = json.loads(transcript_path.read_text(encoding="utf-8"))["scenes"]
    fonts = {kind: next((p for p in paths if Path(p).is_file()), None) for kind, paths in FONTS.items()}
    if args.mono_font:
        fonts["mono"] = args.mono_font
    if args.sans_font:
        fonts["sans"] = fonts["bold"] = args.sans_font
    painter = Painter(fonts, total=1, scenes=len(scenes))
    frames = _timeline(painter, scenes)
    painter.total = sum(seconds for _, _, seconds in frames)

    frame_dir = OUT / "frames"
    frame_dir.mkdir(parents=True, exist_ok=True)
    for old in frame_dir.iterdir():
        old.unlink()
    concat, srt, at = [], [], 0.0
    caption_start, current_caption = 0.0, ""
    for n, (state, caption, seconds) in enumerate(frames):
        name = f"{n:05}.png"
        painter.frame(state, caption, at).save(frame_dir / name)
        concat += [f"file '{name}'", f"duration {seconds:.3f}"]
        if caption != current_caption:
            if current_caption:
                srt.append((caption_start, at, current_caption))
            caption_start, current_caption = at, caption
        at += seconds
    if current_caption:
        srt.append((caption_start, at, current_caption))
    concat.append(f"file '{len(frames) - 1:05}.png'")  # the concat demuxer ignores the last duration otherwise
    (frame_dir / "frames.txt").write_text("\n".join(concat) + "\n", encoding="utf-8")

    video = OUT / "dpdpkit-demo.mp4"
    subprocess.run(  # noqa: S603
        [
            ffmpeg,
            "-y",
            "-loglevel",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(frame_dir / "frames.txt"),
            "-vf",
            "fps=30,format=yuv420p",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "20",
            "-movflags",
            "+faststart",
            str(video),
        ],
        check=True,
    )
    subtitles = video.with_suffix(".srt")
    subtitles.write_text(
        "\n".join(f"{i}\n{_srt_time(a)} --> {_srt_time(b)}\n{text}\n" for i, (a, b, text) in enumerate(srt, 1)),
        encoding="utf-8",
    )
    if not args.keep_frames:
        shutil.rmtree(frame_dir, ignore_errors=True)
    minutes, seconds = divmod(round(at), 60)
    print(f"wrote {video} ({minutes}:{seconds:02}, {len(frames)} frames) and {subtitles}")
    if not 270 <= at <= 330:
        print("warning: aim for 4:30 to 5:30; adjust the narration in demo/scenes.yaml", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("record", help="run the demo steps and write build/demo/transcript.json").set_defaults(func=record)
    r = sub.add_parser("render", help="render build/demo/transcript.json to MP4 and SRT")
    r.add_argument("--ffmpeg", help="path to ffmpeg (default: from PATH)")
    r.add_argument("--mono-font", help="TTF for the terminal (default: Cascadia Mono, Consolas, DejaVu Sans Mono)")
    r.add_argument("--sans-font", help="TTF for titles and captions (default: Segoe UI, DejaVu Sans)")
    r.add_argument("--keep-frames", action="store_true", help="keep the PNG frames in build/demo/frames")
    r.set_defaults(func=render)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
