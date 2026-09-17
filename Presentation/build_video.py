from pathlib import Path
import subprocess
import sys
import shutil
import os
import re


BASE_DIR = Path(__file__).resolve().parent.parent
PRESENTATION_DIR = BASE_DIR / "Presentation"
AUDIO_DIR = PRESENTATION_DIR / "audio"
FRAMES_DIR = BASE_DIR / "output" / "frames"
WORK_DIR = PRESENTATION_DIR / "video_work"
OUTPUT_FILE = PRESENTATION_DIR / "presentation.mp4"
TARGET_RESOLUTION = (1280, 720)
TARGET_FPS = 25
NARRATION_FILE = AUDIO_DIR / "narration.mp3"


def get_duration(path):
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise RuntimeError("ffprobe introuvable")
    command = [
        ffprobe,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr.strip()}")
    return float(result.stdout.strip())


def find_pngs():
    pngs = []
    if FRAMES_DIR.is_dir():
        for i in range(1, 18):
            png = FRAMES_DIR / f"slide_{i:02d}.png"
            if png.is_file():
                pngs.append(png)
    if len(pngs) == 17:
        return pngs
    for subdir_name in ["png", "slides_png"]:
        subdir = PRESENTATION_DIR / subdir_name
        if subdir.is_dir():
            pngs = []
            for i in range(1, 18):
                png = subdir / f"slide_{i:02d}.png"
                if png.is_file():
                    pngs.append(png)
            if len(pngs) == 17:
                return pngs
    raise RuntimeError("17 PNGs introuvables")


def main():
    WORK_DIR.mkdir(parents=True, exist_ok=True)

    narration_duration = get_duration(NARRATION_FILE)
    print(f"Durée narration: {narration_duration:.3f}s")

    pngs = find_pngs()
    print(f"PNG trouvés: {len(pngs)}")

    slide_durations = []
    for i in range(1, 18):
        slide_mp3 = AUDIO_DIR / f"slide_{i:02d}.mp3"
        if slide_mp3.is_file():
            dur = get_duration(slide_mp3)
            slide_durations.append(dur)
            print(f"  slide_{i:02d}.mp3: {dur:.3f}s")
        else:
            slide_durations.append(0.0)

    total_slide_dur = sum(slide_durations)
    print(f"Total slide durations: {total_slide_dur:.3f}s")

    proportional_durations = []
    for i, sd in enumerate(slide_durations):
        if total_slide_dur > 0:
            pd = (sd / total_slide_dur) * narration_duration
        else:
            pd = narration_duration / 17.0
        proportional_durations.append(pd)
        print(f"  slide {i+1}: {sd:.3f}s -> proportionnel: {pd:.3f}s")

    total_prop = sum(proportional_durations)
    print(f"Total proportionnel: {total_prop:.3f}s (cible: {narration_duration:.3f}s)")

    concat_list = WORK_DIR / "concat_list.txt"
    with concat_list.open("w", encoding="utf-8") as f:
        for i, png in enumerate(pngs):
            duration = proportional_durations[i]
            segment_file = WORK_DIR / f"segment_{i+1:02d}.mp4"
            command = [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-loop",
                "1",
                "-i",
                str(png),
                "-t",
                f"{duration:.6f}",
                "-vf",
                f"scale={TARGET_RESOLUTION[0]}:{TARGET_RESOLUTION[1]},fps={TARGET_FPS}",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-an",
                str(segment_file),
            ]
            print(f"Segment {i+1}: {duration:.3f}s - {png.name}")
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"ffmpeg segment {i+1} failed: {result.stderr.strip()}")
            f.write(f"file '{segment_file.resolve()}'\n")

    print("\nConcaténation des segments vidéo...")
    temp_video = WORK_DIR / "presentation_video.mp4"
    command = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_list),
        "-c",
        "copy",
        str(temp_video),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg concat failed: {result.stderr.strip()}")

    print("Ajout de l'audio narration...")
    command = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(temp_video),
        "-i",
        str(NARRATION_FILE),
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-shortest",
        str(OUTPUT_FILE),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg audio merge failed: {result.stderr.strip()}")

    print(f"\nLivrable: {OUTPUT_FILE}")

    if WORK_DIR.is_dir():
        import shutil as sh
        sh.rmtree(WORK_DIR)


if __name__ == "__main__":
    main()
