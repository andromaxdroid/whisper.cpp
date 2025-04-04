import os
import subprocess
import threading
import itertools
import sys
import signal
import time

GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RED = "\033[91m"
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

def check_storage_access():
    storage_path = os.path.expanduser("~/storage/shared")
    return os.path.isdir(storage_path)

def exit_termux():
    
    print(f"\n{CYAN}The Termux app needs to restart to make Whisper work{RED}")
    sys.stdout.flush()
    
    parent_pid = os.getppid()
    os.kill(parent_pid, signal.SIGKILL)
    sys.exit(0)

def set_fish_prompt():
    
    config_dir = os.path.expanduser("~/.config/fish")
    config_file = os.path.join(config_dir, "config.fish")

    
    os.makedirs(config_dir, exist_ok=True)

    
    fish_prompt_function = """function fish_prompt
    set current_dir (prompt_pwd)
    set last_folder (basename $current_dir)
    set parent_path (dirname $current_dir)
    
    

    if test $parent_path = "~"
        echo -n "~"
    else
        echo -n "$parent_path"
    end

    set_color cyan
    echo -n "$last_folder"
    set_color normal
    echo -n " : "
end
function fish_greeting; end\n
"""

    
    with open(config_file, "w") as f:
        f.write(fish_prompt_function)

def main():
    os.system("clear")
    print(f"{GREEN}Whisper.cpp installer{RESET}")

    
    while not check_storage_access():
        print(f"{YELLOW}Setting up storage...{RESET}")
        print(f"{YELLOW}Please allow storage access in Termux, then press Enter to continue...{RESET}")
        os.system("termux-setup-storage")
        input(f"{YELLOW}Press Enter after granting permission...{RESET}")
    
    print(f"{GREEN}Storage access granted successfully.{RESET}")

    execute_with_loading("Updating packages", "pkg update -y")
    
    execute_with_loading("Installing dependencies cmake", "pkg install cmake -y")
    
    execute_with_loading("Installing dependencies fmpeg", "pkg install ffmpeg -y")
    
    execute_with_loading("Installing dependencies git", "pkg install git -y")
    

    os.chdir(os.environ["HOME"])

    execute_with_loading("Installing Fish shell", "pkg install fish -y")
    execute_with_loading("Setting default shell to Fish", "chsh -s fish")
    
    set_fish_prompt()
    
    print(f"{GREEN}Fish shell configured{RESET}")
    
    execute_with_loading("Downloading Whisper", "git clone https://github.com/andromaxdroid/whisper.cpp.git")
    
    whisper_dir = os.path.join(os.getenv("HOME"), "whisper.cpp")
    
    execute_with_loading("Building config please wait a few minutes..", "make", cwd=whisper_dir)

    print(f"{YELLOW}Testing whisper-cli help...{RESET}")
    out, err = run_command("$PREFIX/bin/whisper-cli -h", cwd=whisper_dir)
    print(out.decode())

    print(f"{GREEN}whisper ai has been installed{RESET}")
    print(f"{GREEN}Now you can use {YELLOW}autotranscribe{GREEN} in any folder containing audio or video files to transcribe them{RESET}")
    exit_termux ()
if __name__ == "__main__":
    main()

