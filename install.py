import ctypes
import json
import os
import shutil
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

NOTIFY_SCRIPT_CODE = '''import ctypes
import json
import msvcrt
import os
import subprocess
import sys

def read_stdin_safe():
    try:
        h = msvcrt.get_osfhandle(sys.stdin.fileno())
        avail = ctypes.c_ulong()
        success = ctypes.windll.kernel32.PeekNamedPipe(h, None, 0, None, ctypes.byref(avail), None)
        if success and avail.value > 0:
            return sys.stdin.read(avail.value)
    except Exception:
        pass
    return ""

def find_sound_file(workspace_paths=None):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(script_dir, ".."))

    # Priority 1: Config sounds folder or script dir
    specific = [
        os.path.join(parent_dir, "sounds", "notification.mp3"),
        os.path.join(parent_dir, "sounds", "woeoeoeoe_woeoeoeoeoe_woeoeoeoe.mp3"),
        os.path.join(script_dir, "woeoeoeoe_woeoeoeoeoe_woeoeoeoe.mp3"),
        os.path.join(parent_dir, "woeoeoeoe_woeoeoeoeoe_woeoeoeoe.mp3"),
    ]
    for p in specific:
        if os.path.isfile(p):
            return p

    # Priority 2: Check active workspace if provided
    if workspace_paths:
        for ws in workspace_paths:
            for root, _, files in os.walk(ws):
                if ".git" in root or ".agents" in root:
                    continue
                for f in files:
                    if f.lower().endswith((".mp3", ".wav")):
                        return os.path.join(root, f)

    # Priority 3: Check parent dir for any mp3 or wav
    for root, _, files in os.walk(parent_dir):
        if ".git" in root or "node_modules" in root:
            continue
        for f in files:
            if f.lower().endswith((".mp3", ".wav")):
                return os.path.join(root, f)

    return None

def main():
    workspace_paths = []
    raw_input = read_stdin_safe()
    if raw_input:
        try:
            data = json.loads(raw_input)
            if data.get("terminationReason") == "USER_CANCELED":
                print(json.dumps({}))
                return
            workspace_paths = data.get("workspacePaths", [])
        except Exception:
            pass

    sound_file = find_sound_file(workspace_paths)
    if sound_file:
        escaped_path = os.path.abspath(sound_file).replace("\\\\", "\\\\\\\\")
        device_type = "mpegvideo" if sound_file.lower().endswith(".mp3") else "waveaudio"

        worker = f"""
import ctypes, time
winmm = ctypes.windll.winmm
path = r'{escaped_path}'
alias = 'agy_notify'
winmm.mciSendStringW(f'close {{alias}}', None, 0, None)
res = winmm.mciSendStringW(f'open "{{path}}" type {device_type} alias {{alias}}', None, 0, None)
if res == 0:
    winmm.mciSendStringW(f'play {{alias}} wait', None, 0, None)
    winmm.mciSendStringW(f'close {{alias}}', None, 0, None)
"""
        DETACHED_PROCESS = 0x00000008
        try:
            subprocess.Popen(
                [sys.executable, "-c", worker],
                creationflags=DETACHED_PROCESS,
                close_fds=True,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass

    print(json.dumps({}))

if __name__ == "__main__":
    main()
'''

def find_source_sound():
    candidates = [
        os.path.join(SCRIPT_DIR, "woeoeoeoe_woeoeoeoeoe_woeoeoeoe.mp3"),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    for f in os.listdir(SCRIPT_DIR):
        if f.lower().endswith((".mp3", ".wav")):
            return os.path.join(SCRIPT_DIR, f)
    return None

def update_hooks_json(hooks_file_path, command_str):
    hooks = {}
    if os.path.isfile(hooks_file_path):
        try:
            with open(hooks_file_path, "r", encoding="utf-8") as f:
                hooks = json.load(f)
        except Exception:
            hooks = {}

    hooks["completion-sound"] = {
        "Stop": [
            {
                "type": "command",
                "command": command_str,
                "timeout": 10
            }
        ]
    }

    with open(hooks_file_path, "w", encoding="utf-8") as f:
        json.dump(hooks, f, indent=2)

def test_playback(sound_path):
    print("\nPlaying test sound...")
    escaped_path = os.path.abspath(sound_path).replace("\\", "\\\\")
    device_type = "mpegvideo" if sound_path.lower().endswith(".mp3") else "waveaudio"
    worker = f"""
import ctypes, time
winmm = ctypes.windll.winmm
path = r'{escaped_path}'
alias = 'agy_test'
winmm.mciSendStringW(f'close {{alias}}', None, 0, None)
res = winmm.mciSendStringW(f'open "{{path}}" type {device_type} alias {{alias}}', None, 0, None)
if res == 0:
    winmm.mciSendStringW(f'play {{alias}} wait', None, 0, None)
    winmm.mciSendStringW(f'close {{alias}}', None, 0, None)
"""
    DETACHED_PROCESS = 0x00000008
    try:
        subprocess.Popen(
            [sys.executable, "-c", worker],
            creationflags=DETACHED_PROCESS,
            close_fds=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        print(f"Error during test playback: {e}")

def setup_global(sound_source):
    user_home = os.path.expanduser("~")
    config_dir = os.path.join(user_home, ".gemini", "config")
    sounds_dir = os.path.join(config_dir, "sounds")
    scripts_dir = os.path.join(config_dir, "scripts")

    os.makedirs(sounds_dir, exist_ok=True)
    os.makedirs(scripts_dir, exist_ok=True)

    dest_sound = os.path.join(sounds_dir, "notification.mp3")
    if sound_source:
        shutil.copy2(sound_source, dest_sound)
        print(f"-> Sound copied to: {dest_sound}")

    dest_script = os.path.join(scripts_dir, "notify_done.py")
    with open(dest_script, "w", encoding="utf-8") as f:
        f.write(NOTIFY_SCRIPT_CODE)
    print(f"-> Script installed at: {dest_script}")

    hooks_file = os.path.join(config_dir, "hooks.json")
    update_hooks_json(hooks_file, "python scripts/notify_done.py")
    print(f"-> Hooks updated at: {hooks_file}")

    print("\n[SUCCESS] Global setup complete! Sound will play for ALL Antigravity projects on this PC.")
    if sound_source:
        test_playback(dest_sound)

def setup_local(sound_source):
    agents_dir = os.path.join(SCRIPT_DIR, ".agents")
    os.makedirs(agents_dir, exist_ok=True)

    dest_script = os.path.join(agents_dir, "notify_done.py")
    with open(dest_script, "w", encoding="utf-8") as f:
        f.write(NOTIFY_SCRIPT_CODE)
    print(f"-> Script installed at: {dest_script}")

    hooks_file = os.path.join(agents_dir, "hooks.json")
    update_hooks_json(hooks_file, "python notify_done.py")
    print(f"-> Hooks updated at: {hooks_file}")

    git_dir = os.path.join(SCRIPT_DIR, ".git")
    if not os.path.isdir(git_dir):
        try:
            subprocess.run(["git", "init"], cwd=SCRIPT_DIR, capture_output=True)
            print("-> Initialized Git repository for Antigravity discovery.")
        except Exception:
            pass

    print("\n[SUCCESS] Local setup complete! Sound will play in this project directory.")
    if sound_source:
        test_playback(sound_source)

def main():
    print("=" * 60)
    print("   Antigravity Completion Notification Sound Installer")
    print("=" * 60)

    sound_source = find_source_sound()
    if sound_source:
        print(f"Sound file detected: {os.path.basename(sound_source)}")
    else:
        print("[WARNING] No .mp3 or .wav file found in the folder.")

    mode = None
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower().strip("-")
        if arg in ("global", "g", "1"):
            mode = "1"
        elif arg in ("local", "l", "2"):
            mode = "2"

    if not mode:
        print("\nWhere would you like to set up the notification sound?")
        print("  [1] Global (Recommended: Plays for ALL projects on this PC)")
        print("  [2] Local only (Plays only for this project folder)")
        print()
        choice = input("Enter choice [1/2, Default: 1]: ").strip()
        mode = "2" if choice == "2" else "1"

    if mode == "1":
        setup_global(sound_source)
    else:
        setup_local(sound_source)

if __name__ == "__main__":
    main()
