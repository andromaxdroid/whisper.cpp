#!/usr/bin/env python
import subprocess
import os
import sys
import hashlib
import socket
from pathlib import Path

class Color:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


MODELS = {
    "1":  {"name": "tiny",                "size": "75 MiB"},
    "2":  {"name": "base",                "size": "142 MiB"},
    "3":  {"name": "small",               "size": "466 MiB"},
    "4":  {"name": "medium",              "size": "1.5 GiB"},
    "5":  {"name": "large",               "size": "2.9 GiB"},  # large-v1
    "6":  {"name": "large-v2",            "size": "2.9 GiB"},
    "7":  {"name": "large-v3",            "size": "2.9 GiB"},
    "8":  {"name": "large-v3-turbo",      "size": "1.5 GiB"},
    "9":  {"name": "large-v3-turbo-q5_0", "size": "547 MiB"},
    "10": {"name": "large-v3-turbo-q8_0", "size": "834 MiB"},
    "11": {"name": "medium-q5_0",         "size": "514 MiB"},
    "12": {"name": "medium-q8_0",         "size": "785 MiB"},
    "13": {"name": "small-q5_1",          "size": "181 MiB"},
    "14": {"name": "small-q8_0",          "size": "252 MiB"},
    "15": {"name": "tiny.en",             "size": "75 MiB"},
    "16": {"name": "base.en",             "size": "142 MiB"},
    "17": {"name": "small.en",            "size": "466 MiB"},
    "18": {"name": "medium.en",           "size": "1.5 GiB"},
    "19": {"name": "medium.en-q5_0",      "size": "514 MiB"},
    "20": {"name": "medium.en-q8_0",      "size": "785 MiB"}
}


GENERAL_KEYS = ["1","2","3","4","5","6","7","8","9","10","11","12","13","14"]
ENGLISH_KEYS = ["15","16","17","18","19","20"]

LANGUAGES = {
    "1": {"code": "en", "name": "English"},
    "2": {"code": "id", "name": "Indonesia"},
    "3": {"code": "jp", "name": "Japanese"},
    "4": {"code": "es", "name": "Spanish"},
    "5": {"code": "fr", "name": "French"}
}


EXPECTED_SHA = {
    "tiny":                "bd577a113a864445d4c299885e0cb97d4ba92b5f",
    "base":                "465707469ff3a37a2b9b8d8f89f2f99de7299dac",
    "small":               "55356645c2b361a969dfd0ef2c5a50d530afd8d5",
    "medium":              "fd9727b6e1217c2f614f9b698455c4ffd82463b4",
    "large":               "b1caaf735c4cc1429223d5a74f0f4d0b9b59a299",
    "large-v2":            "0f4c8e34f21cf1a914c59d8b3ce882345ad349d6",
    "large-v3":            "ad82bf6a9043ceed055076d0fd39f5f186ff8062",
    "large-v3-turbo":      "4af2b29d7ec73d781377bfd1758ca957a807e941",
    "large-v3-turbo-q5_0": "e050f7970618a659205450ad97eb95a18d69c9ee",
    "large-v3-turbo-q8_0": "01bf15bedffe9f39d65c1b6ff9b687ea91f59e0e",
    "medium-q5_0":         "7718d4c1ec62ca96998f058114db98236937490e",
    "medium-q8_0":         "e66645948aff4bebbec71b3485c576f3d63af5d6",
    "small-q5_1":          "6fe57ddcfdd1c6b07cdcc73aaf620810ce5fc771",
    "small-q8_0":          "bcad8a2083f4e53d648d586b7dbc0cd673d8afad",
    "tiny.en":             "c78c86eb1a8faa21b369bcd33207cc90d64ae9df",
    "base.en":             "137c40403d78fd54d454da0f9bd998f78703390c",
    "small.en":            "db8a495a91d927739e50b3fc1cc4c6b8f6c2d022",
    "medium.en":           "8c30f0e44ce9560643ebd10bbe50cd20eafd3723",
    "medium.en-q5_0":      "bb3b5281bddd61605d6fc76bc5b92d8f20284c3b",
    "medium.en-q8_0":      "b1cf48c12c807e14881f634fb7b6c6ca867f6b38"
}

def check_internet(host="8.8.8.8", port=53, timeout=3):
    
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False

def color_print(text, color, bold=False, underline=False):
    style = ""
    if bold:
        style += Color.BOLD
    if underline:
        style += Color.UNDERLINE
    print(f"{style}{color}{text}{Color.END}")

def find_whisper_dir():
    possible_paths = [
        os.path.join(os.getenv("PREFIX", ""), "lib/gnome/.lib"),
        "/root/.lib",
        os.path.expanduser("~/.lib"),
        os.path.join(os.path.dirname(os.path.abspath(__file__))),
        "/usr/local/share/.lib",
        "/opt/.lib"
    ]
    for path in possible_paths:
        if os.path.exists(os.path.join(path, "models/download-ggml-model.sh")):
            return path
    return None

def check_model_availability(model_name):
    
    whisper_dir = find_whisper_dir()
    if not whisper_dir:
        return False, "not downloaded"
    model_file = os.path.join(whisper_dir, "models", f"ggml-{model_name}.bin")
    if not os.path.exists(model_file):
        return False, "not downloaded"
    expected = EXPECTED_SHA.get(model_name)
    
    if not expected:
        return True, "available"
    sha1 = hashlib.sha1()
    try:
        with open(model_file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha1.update(chunk)
    except Exception as e:
        return False, "not downloaded"
    file_sha1 = sha1.hexdigest()
    
    
    if file_sha1 == expected:
        return True, "available"
    else:
        return False, "corrupted"

def download_model(model_name):
    whisper_dir = find_whisper_dir()
    if not whisper_dir:
        color_print("✗ Could not find whisper.cpp installation!", Color.RED)
        return False
    color_print(f"\nDownloading model {model_name}...", Color.CYAN)
    try:
        cmd = f"cd {whisper_dir} && ./models/download-ggml-model.sh {model_name}"
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        for line in process.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
        process.wait()
        if process.returncode == 0:
            color_print(f"✓ Model {model_name} downloaded successfully", Color.GREEN)
            return True
        else:
            color_print(f"✗ Failed to download model {model_name}", Color.RED)
            return False
    except Exception as e:
        color_print(f"✗ Error during download: {str(e)}", Color.RED)
        return False

def scan_media_files():
    media_files = []
    extensions = ('.mp3', '.mp4', '.wav')
    color_print("\nScanning for media files in the current directory...", Color.CYAN)
    for file in Path('.').iterdir():
        if file.suffix.lower() in extensions:
            media_files.append(file.name)
    if not media_files:
        color_print("No media files found (MP3/MP4/WAV)", Color.YELLOW)
        return None
    return sorted(media_files)

def select_from_menu(title, options):
    color_print(f"\n{title}:", Color.GREEN)
    for num, option in options.items():
        color_print(f"{num}. {option}", Color.CYAN)
    while True:
        color_print("\nSelect number: ", Color.BLUE, bold=True)
        selection = input().strip()
        if selection in options:
            return options[selection]
        color_print("Invalid number!", Color.RED)

def show_model_menu():
    
    color_print("\n=== Select Model ===", Color.MAGENTA, bold=True)
    color_print("\n=== General Models ===", Color.CYAN, bold=True)
    for key in GENERAL_KEYS:
        model = MODELS[key]
        available, status = check_model_availability(model["name"])
        if status == "available":
            status_disp = f"{Color.CYAN}({model['size']}, available){Color.END}"
        elif status == "not downloaded":
            status_disp = f"{Color.RED}({model['size']}, not downloaded){Color.END}"
        elif status == "corrupted":
            status_disp = f"{Color.BLUE}({model['size']}, corrupted){Color.END}"
        model_display = f"{Color.YELLOW}{model['name'].ljust(20)}{Color.END}"
        print(f"{key}. {model_display} {status_disp}")

    
    color_print("\n=== English Specific Models ===", Color.BLUE, bold=True)
    for key in ENGLISH_KEYS:
        model = MODELS[key]
        available, status = check_model_availability(model["name"])
        if status == "available":
            status_disp = f"{Color.CYAN}({model['size']}, available){Color.END}"
        elif status == "not downloaded":
            status_disp = f"{Color.RED}({model['size']}, not downloaded){Color.END}"
        elif status == "corrupted":
            status_disp = f"{Color.BLUE}({model['size']}, corrupted){Color.END}"
        model_display = f"{Color.YELLOW}{model['name'].ljust(20)}{Color.END}"
        print(f"{key}. {model_display} {status_disp}")

    
    while True:
        color_print("\nSelect model number: ", Color.BLUE, bold=True)
        selection = input().strip()
        if selection in MODELS:
            selected_model = MODELS[selection]["name"]
            available, status = check_model_availability(selected_model)
            if available:
                return selected_model
            else:
                color_print(f"\nModel {selected_model} is {status}!", Color.YELLOW)
                color_print("Do you want to download it now? (y/n): ", Color.BLUE, bold=True)
                choice = input().strip().lower()
                if choice == 'y':
                    # Jika status corrupted, hapus file model yang corrupt terlebih dahulu
                    if status == "corrupted":
                        whisper_dir = find_whisper_dir()
                        model_file = os.path.join(whisper_dir, "models", f"ggml-{selected_model}.bin")
                        try:
                            os.remove(model_file)
                            color_print(f"Corrupted file {model_file} has been removed.", Color.YELLOW)
                        except Exception as e:
                            color_print(f"Failed to remove corrupted file: {str(e)}", Color.RED)
                    if download_model(selected_model):
                        return selected_model
        else:
            color_print("Invalid number!", Color.RED)

def select_language(selected_model):
    if selected_model.endswith(('.en', '.en-q5_0', '.en-q8_0')):
        color_print("\nEnglish model (.en) detected, automatically selecting English", Color.GREEN)
        return "en"
    color_print("\n=== Select Language ===", Color.MAGENTA, bold=True)
    for num, lang in LANGUAGES.items():
        color_print(f"{num}. {lang['name']}", Color.CYAN)
    while True:
        color_print("\nSelect language number: ", Color.BLUE, bold=True)
        selection = input().strip()
        if selection in LANGUAGES:
            return LANGUAGES[selection]["code"]
        color_print("Invalid number!", Color.RED)

def convert_to_wav(input_file):
    output_file = os.path.splitext(input_file)[0] + ".wav"
    if Path(output_file).exists():
        color_print(f"WAV file already exists: {output_file}", Color.YELLOW)
        return output_file
    cmd = [
        "ffmpeg",
        "-i", input_file,
        "-ar", "16000",
        "-ac", "1",
        "-c:a", "pcm_s16le",
        output_file
    ]
    color_print(f"\nConverting {input_file} to WAV...", Color.CYAN)
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        for line in process.stdout:
            print(line.strip())
        process.wait()
        color_print("✓ Conversion successful!", Color.GREEN)
        return output_file
    except Exception as e:
        color_print(f"✗ Conversion error: {str(e)}", Color.RED)
        return None

def get_clean_base_name(file_path):
    base = os.path.basename(file_path)
    return os.path.splitext(base)[0]

def run_whisper_with_progress(cmd, original_file):
    color_print("\nStarting transcription process...", Color.MAGENTA, bold=True)
    color_print("="*50, Color.BLUE)
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                if "%" in output:
                    sys.stdout.write(f"{Color.YELLOW}{output}{Color.END}")
                else:
                    sys.stdout.write(output)
                sys.stdout.flush()
        color_print("="*50, Color.BLUE)
        base_name = get_clean_base_name(original_file)
        srt_file = f"{base_name}.srt"
        input_for_whisper = cmd[cmd.index('-f')+1]
        working_basename = os.path.basename(input_for_whisper)
        temp_srt = working_basename + ".srt"
        if os.path.exists(temp_srt) and temp_srt != srt_file:
            os.rename(temp_srt, srt_file)
        return process.returncode == 0
    except Exception as e:
        color_print(f"\n✗ Error: {str(e)}", Color.RED)
        return False

def main():
    # Cek koneksi internet terlebih dahulu
    if not check_internet():
        color_print("sorry\nInternet is needed to run this script\nInternet is required to download models", Color.YELLOW)
        color_print("press enter to exit", Color.RED)
        input()
        sys.exit(1)

    color_print("\n=== Auto Transcription ===", Color.MAGENTA, bold=True)
    whisper_dir = find_whisper_dir()
    if not whisper_dir:
        color_print("✗ Error: Could not find whisper.cpp installation!", Color.RED)
        color_print("Make sure whisper.cpp is installed in one of the following locations:", Color.YELLOW)
        color_print("- /root/whisper.cpp", Color.YELLOW)
        color_print("- ~/whisper.cpp", Color.YELLOW)
        color_print("- This script's directory", Color.YELLOW)
        color_print("- /usr/local/share/whisper.cpp", Color.YELLOW)
        color_print("- /opt/whisper.cpp", Color.YELLOW)
        return
    files = scan_media_files()
    if not files:
        return
    file_options = {str(i+1): file for i, file in enumerate(files)}
    input_file = select_from_menu("Media files list", file_options)
    model = show_model_menu()
    language = select_language(model)
    color_print("\nEnter number of CPU threads (default 4): ", Color.BLUE, bold=True, underline=True)
    threads = input().strip() or "4"
    whisper_bin = os.path.join(whisper_dir, "build/bin/whisper-cli")
    model_path = os.path.join(whisper_dir, "models", f"ggml-{model}.bin")
    original_file = os.path.abspath(input_file)
    base_name = get_clean_base_name(original_file)
    temp_wav = None
    if not Path(whisper_bin).exists():
        color_print(f"✗ Error: {whisper_bin} not found!", Color.RED)
        color_print("Make sure whisper.cpp is built", Color.YELLOW)
        return
    working_file = original_file
    # Jika input adalah MP4, convert ke WAV
    if original_file.lower().endswith('.mp4'):
        temp_wav = convert_to_wav(original_file)
        if not temp_wav:
            return
        working_file = temp_wav

    
    cmd = [
        whisper_bin,
        "-m", model_path,
        "-f", working_file,
        "-osrt",
        "-t", threads,
        "--output-file", base_name,
        "--print-progress"
    ]
    
    if not model.endswith(('.en', '.en-q5_0', '.en-q8_0')):
        cmd.extend(["-l", language])

    
    color_print("\n=== Configuration ===", Color.MAGENTA, bold=True)
    color_print(f"File: {original_file}", Color.CYAN)
    color_print(f"Model: {model_path}", Color.CYAN)
    color_print(f"Language: {language}", Color.CYAN)
    color_print(f"Threads: {threads}", Color.CYAN)
    color_print("\nCommand:", Color.BLUE)
    color_print(" ".join(cmd), Color.YELLOW)
    color_print("\nStarting process...\n", Color.GREEN, bold=True)

    
    success = run_whisper_with_progress(cmd, original_file)

    
    if temp_wav and os.path.exists(temp_wav):
        os.remove(temp_wav)

    
    if success:
        base_name = get_clean_base_name(original_file)
        srt_file = f"{base_name}.srt"
        color_print(f"\n✓ SRT file created: {srt_file}", Color.GREEN, bold=True)
    else:
        color_print("\n✗ Transcription process encountered an error", Color.RED, bold=True)

if __name__ == "__main__":
    main()
    color_print("\nProgram finished", Color.MAGENTA, bold=True)
