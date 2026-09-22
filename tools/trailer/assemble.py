#!/usr/bin/env python3
"""Cut the 12 Seedance shots into the 30s trailer. Hard cuts, no cross-fades.

12 shots x 2.5s = 30.000s exactly. Each 5s clip is trimmed to its best window
(the action lands mid-clip; the model's camera drift settles late, so the tail
is steadier than the head).

Usage: python3 tools/trailer/assemble.py
"""
import subprocess
from pathlib import Path

SCR = Path("/private/tmp/claude-501/-Users-anthonyguy-SHADOWCLASH-RECOVERED"
           "/ca56c915-b305-4845-a1ac-6d66942b0b2d/scratchpad")
CLIPS, WORK = SCR / "clips", SCR / "cut"
FONT = "/System/Library/Fonts/Avenir Next Condensed.ttc"
# (clip, start, duration, text, push)
#
# start = the MEASURED peak-motion window, not a guess. Seedance front-loads the
# action: every action clip peaks in its first second, so the old fixed 1.2-1.8s
# start was cutting the movement off and keeping the dead tail.
#
# duration is spent where motion actually is (measured mean frame delta):
# p07=19.6 p15=8.1 p22=6.4 p02=5.9 p18=4.1 get the screen time; the six clips
# that measured under 1.4 are near-still, so they get ~1.5s AND a camera push so
# the frame is never frozen even when the character is.
SHOTS = [
    ("p01", 0.8, 3.0, "THE LAST STUDENT OF A SCHOOL THAT NO LONGER EXISTS", True),
    ("p02", 0.2, 2.5, None, False),
    ("p04", 0.5, 1.6, "HE CAME DOWN CHASING SOMEONE", True),
    ("p05", 0.3, 1.4, None, True),
    ("p06", 0.5, 2.6, "THE MASK STOPPED COMING OFF BETWEEN JOBS", True),
    ("p07", 0.2, 4.5, "HE", False),
    ("p10", 0.0, 2.0, "IS", False),
    ("p12", 0.2, 1.5, "NOT", True),
    ("p15", 1.4, 3.4, "EVEN HERE", False),
    ("p16", 0.5, 1.5, "HE IS ALREADY GONE", True),
    ("p18", 2.2, 2.0, None, False),
    ("p22", 0.7, 4.0, None, False),
]

# ponytail: this ffmpeg is built without freetype, so drawtext does not exist.
# PIL is already a dependency — render the caption to a transparent PNG and let
# ffmpeg's overlay filter do the compositing. No new install.
def caption_png(txt, path):
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 46, index=1)
    x = 90
    for ch in txt:                                   # manual tracking
        d.text((x, 930), ch, font=f, fill=(238, 232, 222, 255), anchor="ls",
               stroke_width=4, stroke_fill=(0, 0, 0, 220))
        x += d.textlength(ch, font=f) + 6
    im.save(path)

def main():
    WORK.mkdir(parents=True, exist_ok=True)
    for p in list(WORK.glob("*.mp4")) + list(WORK.glob("*.png")):
        p.unlink()
    parts = []
    # The storyboard's "N 0:00" badge sat taller than the seed crop removed, so the
    # model carried it into the clips. Shave the top-left corner off every shot and
    # rescale — cheaper than regenerating 12 clips to lose one badge.
    scale = ("crop=in_w*0.95:in_h*0.88:in_w*0.05:in_h*0.12,"
             "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=24")
    for i, (clip, ss, dur, txt, push) in enumerate(SHOTS):
        out = WORK / f"{i:02d}.mp4"
        chain = scale
        if push:
            # a near-still clip still needs the FRAME to move — slow push-in
            chain += (",zoompan=z='min(zoom+0.0012,1.22)':d=1:"
                      "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=24")
        cmd = ["ffmpeg", "-y", "-v", "error", "-ss", str(ss), "-t", str(dur),
               "-i", str(CLIPS / f"{clip}.mp4")]
        scale_local, scale = scale, chain
        if txt:
            cap = WORK / f"cap{i:02d}.png"
            caption_png(txt, cap)
            cmd += ["-i", str(cap), "-filter_complex",
                    f"[0:v]{scale}[v];[v][1:v]overlay=0:0"]
        else:
            cmd += ["-vf", scale]
        cmd += ["-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-an", str(out)]
        subprocess.run(cmd, check=True)
        parts.append(out)

    lst = WORK / "list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    final = SCR / "SHADOWCLASH-TRAILER-B.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", str(lst), "-c:v", "libx264", "-crf", "16",
                    "-pix_fmt", "yuv420p", str(final)], check=True)
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", str(final)],
                       capture_output=True, text=True).stdout.strip()
    print(f"{final}  duration={d}s")

if __name__ == "__main__":
    main()
