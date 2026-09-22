#!/usr/bin/env python3
"""Regression check: a clean Shodō atlas can bootstrap without legacy idle art."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw


PACKER = Path(__file__).with_name("pack_shodo_row.py")


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        scripts = root / "tools" / "sprites"
        sprites = root / "web" / "assets" / "sprites"
        board = root / "board"
        scripts.mkdir(parents=True)
        sprites.mkdir(parents=True)
        board.mkdir()
        shutil.copy2(PACKER, scripts / PACKER.name)

        manifest = {"frameW": 100, "frameH": 100, "footY": 90, "cols": 1, "frames": {}}
        (sprites / "test.json").write_text(json.dumps(manifest))
        Image.new("RGBA", (100, 100), (0, 0, 0, 0)).save(sprites / "test.png")
        for beat in range(1, 9):
            frame = Image.new("RGBA", (80, 80), "white")
            draw = ImageDraw.Draw(frame)
            top = 20 if beat == 4 else 40
            draw.rectangle((30, top, 49, 69), fill="black")
            frame.save(board / f"frame-{beat:02d}.png")

        env = dict(os.environ, TARGET_H="50", TARGET_BEAT="4")
        result = subprocess.run(
            ["python3", str(scripts / PACKER.name), "test", str(board), "idle"],
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr or result.stdout
        packed = Image.open(sprites / "test.png").convert("RGBA")
        saved = json.loads((sprites / "test.json").read_text())
        cell = saved["frames"]["idle"]
        bounds = packed.crop((cell * 100, 0, (cell + 1) * 100, 100)).getchannel("A").getbbox()
        assert bounds is not None
        assert abs((bounds[3] - bounds[1]) - 30) <= 1, bounds
        assert bounds[3] == 90, bounds
        anchor_bounds = packed.crop((4 * 100, 0, 5 * 100, 100)).getchannel("A").getbbox()
        assert anchor_bounds is not None
        assert abs((anchor_bounds[3] - anchor_bounds[1]) - 50) <= 1, anchor_bounds
        assert anchor_bounds[3] == 90, anchor_bounds

    print("PACK SHODO ROW BOOTSTRAP: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
