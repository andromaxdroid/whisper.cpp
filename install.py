import os
import subprocess
import threading
import itertools
import sys
import time

GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

loading_done = False

def run_command(command, cwd=None):
    process = subprocess.Popen(command, shell=True, cwd=cwd,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    out, err = process.communicate()
    return out, err

def loading_animation(message):
    for frame in itertools.cycle(['|', '/', '-', '\\']):
        if loading_done:
            break
        sys.stdout.write(f'\r{YELLOW}{message} {frame}{RESET}')
        sys.stdout.flush()
        time.sleep(0.1)

def execute_with_loading(message, command, cwd=None):
    global loading_done
    loading_done = False
    loading_thread = threading.Thread(target=loading_animation, args=(message,))
    loading_thread.start()
    
    run_command(command, cwd)
    
    loading_done = True
    loading_thread.join()
    sys.stdout.write(f'\r{GREEN}{message} Done!{RESET}\n')

def main():
    os.system("clear")
    print(f"{GREEN}Whisper.cpp installer{RESET}")
    
    print(f"{YELLOW}Setting up storage...{RESET}")
    print(f"{YELLOW}Please allow storage access in Termux, then press Enter to continue...{RESET}")
    os.system("termux-setup-storage")
    input(f"{YELLOW}Press Enter after granting permission...{RESET}")
    
    execute_with_loading("Updating packages", "pkg update -y")
    execute_with_loading("Installing dependencies (cmake, ffmpeg, git)", "pkg install cmake ffmpeg git -y")
    
    os.chdir(os.environ["HOME"])
    
    execute_with_loading("Installing Fish shell", "pkg install fish -y")
    execute_with_loading("Setting default shell to Fish", "chsh -s fish")
    config_path = os.path.expanduser("~/.config/fish/config.fish")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as f:
        f.write("function fish_greeting; end\n")
    print(f"{GREEN}Fish shell configured{RESET}")
    
    execute_with_loading("Downloading Whisper", "git clone https://github.com/ggerganov/whisper.cpp.git")
    
    whisper_dir = os.path.join(os.environ["HOME"], "whisper.cpp")
    execute_with_loading("Running cmake build", "cmake -B build", cwd=whisper_dir)
    execute_with_loading("Building config please wait", "cmake --build build --config Release", cwd=whisper_dir)
    
    print(f"{YELLOW}Testing whisper-cli help...{RESET}")
    out, err = run_command("./build/bin/whisper-cli -h", cwd=whisper_dir)
    print(out.decode())
    
    print(f"{GREEN}whisper ai has been installed{RESET}")
    
    if os.path.exists("autofinal.py"):
        execute_with_loading("Making autofinal.py executable", "chmod +x autofinal.py")
        prefix_bin = os.path.join(os.environ["PREFIX"], "bin")
        destination = os.path.join(prefix_bin, "autotrancribe")
        try:
            os.rename("autofinal.py", destination)
            print(f"{GREEN}Moved autofinal.py to {destination}{RESET}")
        except Exception as e:
            print(f"{YELLOW}Failed to move autofinal.py: {e}{RESET}")
    else:
        print(f"{YELLOW}autofinal.py not found in current directory{RESET}")
    
    print(f"{GREEN}Now you can use \"autotrancribe\" in any folder containing audio or video files to transcribe them{RESET}")

if __name__ == "__main__":
    main()
