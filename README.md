# Antigravity Completion Notification Sound

Automatically plays a notification sound whenever Google Antigravity finishes a task or prompt turn.

## Features
- **Zero latency**: Plays asynchronously in the background via the native Windows multimedia API (`winmm.dll`) without blocking Antigravity or delaying responses.
- **Native & lightweight**: Uses standard Python libraries with no external packages required.
- **Flexible**: Choose between global setup (for all Antigravity projects) or local setup (scoped to this project).
- **Auto-cancellation aware**: Automatically skips playback if you cancel the turn.

## Quick Start

1. Place your desired audio file (`.mp3` or `.wav`) into this folder (or use the included `woeoeoeoe_woeoeoeoeoe_woeoeoeoe.mp3`).
2. Double-click **`setup.bat`**.
3. Choose your installation mode:
   - **`[1] Global (Recommended)`**: Installs to `~/.gemini/config/` so the sound plays for **any** Antigravity project on your PC.
   - **`[2] Local`**: Installs to `.agents/` inside this project directory only.
4. A test sound will play to confirm the setup works!

## Requirements
- Windows 10 / 11
- Python 3 added to `PATH` (`python --version`)

## Command-Line Usage
You can also run the installer non-interactively:
```bat
setup.bat --global
```
or
```bat
setup.bat --local
```
