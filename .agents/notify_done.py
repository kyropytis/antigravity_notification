import ctypes
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

    # Antigravity hook contract: return JSON object on stdout
    print(json.dumps({}))

if __name__ == "__main__":
    main()
