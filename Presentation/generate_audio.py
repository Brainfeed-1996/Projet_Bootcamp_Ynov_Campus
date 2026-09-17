from pathlib import Path
import re
import shutil
import subprocess
import sys
import traceback


BASE_DIR = Path(__file__).resolve().parent.parent
PRESENTATION_DIR = BASE_DIR / "Presentation"
NARRATION_FILE = PRESENTATION_DIR / "narration.md"
AUDIO_DIR = PRESENTATION_DIR / "audio"


def clean_markdown(text):
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_narration(path):
    content = path.read_text(encoding="utf-8")
    slides = []
    for section in re.split(r"^\s*---\s*$", content, flags=re.MULTILINE):
        lines = [line.strip() for line in section.splitlines() if line.strip()]
        heading_index = next(
            (
                index
                for index, line in enumerate(lines)
                if re.match(r"^#+\s*Diapositive\s+\d+", line, re.IGNORECASE)
            ),
            None,
        )
        if heading_index is None:
            continue
        match = re.search(r"Diapositive\s+(\d+)", lines[heading_index], re.IGNORECASE)
        if not match:
            continue
        text = clean_markdown(" ".join(lines[heading_index + 1 :]))
        slides.append({"number": int(match.group(1)), "text": text})
    slides.sort(key=lambda slide: slide["number"])
    return slides


def find_ffmpeg():
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return ffmpeg
    candidates = [
        Path(r"C:\Users\Scott_Adams\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-full_build\bin\ffmpeg.exe"),
        Path(r"C:\Program Files\ffmpeg\bin\ffmpeg.exe"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    raise RuntimeError("ffmpeg introuvable")


def convert_wav_to_mp3(wav_path, mp3_path):
    ffmpeg = find_ffmpeg()
    command = [
        ffmpeg,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(wav_path),
        "-ar",
        "22050",
        "-ac",
        "1",
        str(mp3_path),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr.strip()}")


def generate_with_pyttsx3(text, slide_number):
    import pyttsx3

    padded = f"{slide_number:02d}"
    wav_path = AUDIO_DIR / f"slide_{padded}.wav"
    mp3_path = AUDIO_DIR / f"slide_{padded}.mp3"
    engine = pyttsx3.init("sapi5")
    voices = engine.getProperty("voices") or []
    french_voices = [
        voice
        for voice in voices
        if "fr" in (voice.id + " " + voice.name).lower()
        or "french" in voice.name.lower()
    ]
    voice = next(
        (item for item in french_voices if "hortense" in item.name.lower()),
        french_voices[0] if french_voices else None,
    )
    if voice is None:
        raise RuntimeError("aucune voix française SAPI5 disponible")
    engine.setProperty("voice", voice.id)
    engine.setProperty("rate", 150)
    engine.setProperty("volume", 1.0)
    engine.save_to_file(text, str(wav_path))
    engine.runAndWait()
    engine.stop()
    convert_wav_to_mp3(wav_path, mp3_path)
    wav_path.unlink(missing_ok=True)
    return mp3_path, voice.name


def generate_with_espeakng(text, slide_number):
    try:
        import espeakng
    except ImportError as error:
        raise RuntimeError("espeakng non installé") from error

    padded = f"{slide_number:02d}"
    wav_path = AUDIO_DIR / f"slide_{padded}.wav"
    mp3_path = AUDIO_DIR / f"slide_{padded}.mp3"
    speaker = espeakng.Speaker()
    speaker.voice = "fr"
    speaker.wpm = 150
    speaker.say(text, export_path=str(wav_path))
    speaker.wait()
    convert_wav_to_mp3(wav_path, mp3_path)
    wav_path.unlink(missing_ok=True)
    return mp3_path, "espeakng-fr"


TARGET_DURATION = 660.0
TEMPO_FACTOR = 1.9747


def get_audio_duration(path):
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return None
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
        return None
    try:
        return float(result.stdout.strip())
    except ValueError:
        return None


def concatenate_segments(mp3_files, concat_wav):
    ffmpeg = find_ffmpeg()
    list_file = AUDIO_DIR / "concat_list.txt"
    with list_file.open("w", encoding="utf-8") as handle:
        for mp3 in mp3_files:
            handle.write(f"file '{mp3.resolve()}'\n")
    command = [
        ffmpeg,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_file),
        "-c",
        "copy",
        str(concat_wav),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    list_file.unlink(missing_ok=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg concat failed: {result.stderr.strip()}")


def apply_tempo_and_encode(concat_wav, output_mp3, tempo):
    ffmpeg = find_ffmpeg()
    command = [
        ffmpeg,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(concat_wav),
        "-filter:a",
        f"atempo={tempo}",
        "-ar",
        "22050",
        "-ac",
        "1",
        str(output_mp3),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg atempo failed: {result.stderr.strip()}")


def main():
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    print("=== Génération audio Narration française ===")
    print(f"Fichier narration: {NARRATION_FILE}")
    if not NARRATION_FILE.is_file():
        print(f"ERREUR: {NARRATION_FILE} introuvable")
        sys.exit(1)

    slides = parse_narration(NARRATION_FILE)
    print(f"Diapositives trouvées: {len(slides)}")
    if len(slides) != 17:
        print(f"ERREUR: 17 diapositives attendues, {len(slides)} trouvées")
        sys.exit(1)

    for slide in slides:
        slide_number = slide["number"]
        text = slide["text"]
        padded = f"{slide_number:02d}"
        print(f"\n[Slide {padded}] {len(text)} caractères - Début...")
        try:
            output_path, voice_name = generate_with_pyttsx3(text, slide_number)
            print(f"  [OK] Généré: {output_path} ({voice_name}, 22050 Hz, mono)")
        except Exception as error:
            print(f"  [ERR] pyttsx3: {error}")
            traceback.print_exc()
            try:
                output_path, voice_name = generate_with_espeakng(text, slide_number)
                print(f"  [OK] Fallback: {output_path} ({voice_name}, 22050 Hz, mono)")
            except Exception as fallback_error:
                print(f"  [ERR] Fallback espeakng: {fallback_error}")
                traceback.print_exc()
                sys.exit(1)

    mp3_files = sorted(AUDIO_DIR.glob("slide_*.mp3"))
    print(f"\nTotal MP3 par diapositive: {len(mp3_files)}")
    if len(mp3_files) != 17:
        print(f"ERREUR: 17 MP3 attendus, {len(mp3_files)} présents")
        sys.exit(1)

    concat_wav = AUDIO_DIR / "concat_temp.wav"
    output_mp3 = AUDIO_DIR / "narration.mp3"
    print("\n=== Concaténation des segments ===")
    concatenate_segments(mp3_files, concat_wav)
    base_duration = get_audio_duration(concat_wav)
    if base_duration:
        print(f"Durée de la concaténation (brute): {base_duration:.2f}s")
    else:
        print("Durée de la concaténation inconnue")

    print(f"\n=== Application atempo (cible {TARGET_DURATION}s) ===")
    if base_duration:
        tempo = base_duration / TARGET_DURATION
        # atempo est borné à [0.5, 2.0] ; chaîner si nécessaire
        if tempo > 2.0:
            tempo = 2.0
        elif tempo < 0.5:
            tempo = 0.5
        print(f"Facteur atempo calculé: {tempo:.4f} (brute {base_duration:.2f}s / cible {TARGET_DURATION}s)")
    else:
        tempo = TEMPO_FACTOR
        print(f"Facteur atempo par défaut: {tempo}")
    apply_tempo_and_encode(concat_wav, output_mp3, tempo)
    concat_wav.unlink(missing_ok=True)

    measured = get_audio_duration(output_mp3)
    print("\n=== Livrable final ===")
    print(f"Fichier: {output_mp3}")
    if measured is not None:
        print(f"Durée mesurée: {measured:.2f}s (cible: {TARGET_DURATION}s, écart: {measured - TARGET_DURATION:+.2f}s)")
    else:
        print("Durée: impossible à mesurer avec ffprobe")
    print("Codec: MP3, 22050 Hz, mono")


if __name__ == "__main__":
    main()
