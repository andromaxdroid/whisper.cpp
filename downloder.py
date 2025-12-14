#!/usr/bin/env python3
import subprocess
import sys
import os

def get_formats(url):
    result = subprocess.run(
        ["yt-dlp", "-F", url],
        capture_output=True,
        text=True
    )

    lines = result.stdout.splitlines()
    formats = []

    for line in lines:
        if line.startswith("ID") or line.startswith("─"):
            continue

        parts = line.split()
        if len(parts) < 3:
            continue

        fmt_id = parts[0]
        ext = parts[1]
        res = parts[2]

        if ext in ("mp4", "webm") and "audio" not in line.lower():
            formats.append((fmt_id, res))

    return formats

def show_formats(formats):
    print("\n📋 Pilih resolusi:\n")
    for i, f in enumerate(formats, start=1):
        print(f"{i}. {f[0]}  →  {f[1]}")

def download(url, fmt_id):
    print("\n⬇️  Download dimulai...\n")
    subprocess.run([
        "yt-dlp",
        "-f", fmt_id,
        "--merge-output-format", "mp4",
        "-o", "%(title)s.%(ext)s",
        url
    ])

def find_last_mp4():
    mp4_files = [f for f in os.listdir('.') if f.endswith('.mp4')]
    if not mp4_files:
        return None
    mp4_files.sort(key=os.path.getmtime)
    return mp4_files[-1]

def convert_audio(video_file):
    print("\n🎧 Konversi audio?")
    print("1. WAV (16kHz, mono)")
    print("2. MP3")
    print("0. Tidak")

    choice = input("👉 Pilihan: ").strip()

    name = os.path.splitext(video_file)[0]

    if choice == "1":
        out = name + ".wav"
        subprocess.run([
            "ffmpeg", "-y",
            "-i", video_file,
            "-ar", "16000",
            "-ac", "1",
            "-c:a", "pcm_s16le",
            out
        ])
        print(f"✅ Audio WAV tersimpan: {out}")

    elif choice == "2":
        out = name + ".mp3"
        subprocess.run([
            "ffmpeg", "-y",
            "-i", video_file,
            out
        ])
        print(f"✅ Audio MP3 tersimpan: {out}")

    else:
        print("⏭️  Konversi dilewati")

def main():
    if len(sys.argv) < 2:
        print("Usage: python vidm.py <URL>")
        sys.exit(1)

    url = sys.argv[1]

    formats = get_formats(url)
    if not formats:
        print("❌ Format tidak ditemukan")
        return

    show_formats(formats)

    choice = input("\n👉 Masukkan nomor pilihan: ").strip()
    if not choice.isdigit():
        print("❌ Harus angka")
        return

    choice = int(choice)
    if choice < 1 or choice > len(formats):
        print("❌ Nomor tidak valid")
        return

    fmt_id = formats[choice - 1][0]
    download(url, fmt_id)

    video = find_last_mp4()
    if video:
        convert_audio(video)

    print("\n🎉 Semua proses selesai!")

if __name__ == "__main__":
    main()
