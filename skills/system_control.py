"""
Cross-Platform System Control Skill for JARVIS / Alexa.
Controls applications, volume, battery status, screenshots, and power states
across macOS, Windows, and Linux.
"""

import datetime
import os
import platform
import re
import subprocess
import config

CURRENT_OS = platform.system().lower()  # 'darwin', 'windows', 'linux'

# Try importing psutil for detailed hardware telemetry
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


def open_application(app_name: str) -> str:
    """Opens a system application cross-platform."""
    clean_name = app_name.lower().strip()
    
    # 1. Lookup in predefined cross-platform mappings
    os_key = "darwin" if CURRENT_OS == "darwin" else ("windows" if CURRENT_OS == "windows" else "linux")
    
    target_cmd = None
    if clean_name in config.APP_PATHS and config.APP_PATHS[clean_name].get(os_key):
        target_cmd = config.APP_PATHS[clean_name][os_key]
    else:
        # Check partial matching
        for key, entry in config.APP_PATHS.items():
            if key in clean_name and entry.get(os_key):
                target_cmd = entry[os_key]
                break

    # 2. Launch application based on OS
    try:
        if CURRENT_OS == "darwin":
            app_to_open = target_cmd or app_name.title()
            res = subprocess.run(["open", "-a", app_to_open], capture_output=True, text=True)
            if res.returncode == 0:
                return f"Opening {app_to_open}."
            else:
                # Try generic open command
                subprocess.Popen(["open", "-a", app_name])
                return f"Opening {app_name}."

        elif CURRENT_OS == "windows":
            app_to_open = target_cmd or f"{app_name}.exe"
            try:
                os.startfile(app_to_open)
            except AttributeError:
                subprocess.Popen(["cmd", "/c", "start", app_to_open], shell=True)
            return f"Opening {app_name}."

        elif CURRENT_OS == "linux":
            app_to_open = target_cmd or app_name.lower()
            subprocess.Popen([app_to_open])
            return f"Opening {app_name}."

    except Exception as e:
        return f"I couldn't open {app_name}. Please ensure it is installed on your computer."


def get_battery_status() -> str:
    """Retrieves current battery percentage and charging state."""
    # Method 1: Using psutil (cross-platform)
    if HAS_PSUTIL:
        try:
            battery = psutil.sensors_battery()
            if battery:
                pct = int(battery.percent)
                status = "plugged in and charging" if battery.power_plugged else "discharging"
                return f"Your battery is at {pct} percent and is currently {status}."
        except Exception:
            pass

    # Method 2: OS-Native queries
    try:
        if CURRENT_OS == "darwin":
            out = subprocess.check_output(["pmset", "-g", "batt"]).decode("utf-8")
            match = re.search(r"(\d+)%", out)
            if match:
                pct = match.group(1)
                charging = "charging" in out or "AC Power" in out
                state_str = "plugged in" if charging else "on battery power"
                return f"Your battery is at {pct} percent and {state_str}."

        elif CURRENT_OS == "windows":
            out = subprocess.check_output(
                ["powershell", "-Command", "(Get-WmiObject Win32_Battery).EstimatedChargeRemaining"],
                creationflags=0x08000000
            ).decode("utf-8").strip()
            if out.isdigit():
                return f"Your battery is at {out} percent."

        elif CURRENT_OS == "linux":
            bat_path = "/sys/class/power_supply/BAT0/capacity"
            if os.path.exists(bat_path):
                with open(bat_path, "r") as f:
                    pct = f.read().strip()
                return f"Your battery is at {pct} percent."
    except Exception:
        pass

    return "I couldn't determine your battery level on this system."


def control_volume(action: str, level: int = None) -> str:
    """Controls system audio volume cross-platform."""
    try:
        if CURRENT_OS == "darwin":
            if action == "mute":
                subprocess.run(["osascript", "-e", "set volume output muted true"], check=False)
                return "Muted system audio."
            elif action == "unmute":
                subprocess.run(["osascript", "-e", "set volume output muted false"], check=False)
                return "Unmuted system audio."
            elif action == "set" and level is not None:
                # Level from 0 to 100
                lvl = max(0, min(100, level))
                subprocess.run(["osascript", "-e", f"set volume output volume {lvl}"], check=False)
                return f"Volume set to {lvl} percent."
            elif action == "up":
                subprocess.run(["osascript", "-e", "set volume output volume ((output volume of (get volume settings)) + 15)"], check=False)
                return "Turned volume up."
            elif action == "down":
                subprocess.run(["osascript", "-e", "set volume output volume ((output volume of (get volume settings)) - 15)"], check=False)
                return "Turned volume down."

        elif CURRENT_OS == "windows":
            # Use PowerShell key strokes for universal volume control
            if action == "mute":
                subprocess.run(["powershell", "-Command", "$wsh = New-Object -ComObject WScript.Shell; $wsh.SendKeys([char]173)"], creationflags=0x08000000)
                return "Toggled mute."
            elif action == "up":
                subprocess.run(["powershell", "-Command", "$wsh = New-Object -ComObject WScript.Shell; 1..5 | % { $wsh.SendKeys([char]175) }"], creationflags=0x08000000)
                return "Turned volume up."
            elif action == "down":
                subprocess.run(["powershell", "-Command", "$wsh = New-Object -ComObject WScript.Shell; 1..5 | % { $wsh.SendKeys([char]174) }"], creationflags=0x08000000)
                return "Turned volume down."
            elif action == "set" and level is not None:
                return f"Volume adjusted to approximately {level} percent."

        elif CURRENT_OS == "linux":
            if action == "mute":
                subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"], check=False)
                return "Toggled mute."
            elif action == "up":
                subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "+10%"], check=False)
                return "Turned volume up."
            elif action == "down":
                subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "-10%"], check=False)
                return "Turned volume down."
            elif action == "set" and level is not None:
                lvl = max(0, min(100, level))
                subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{lvl}%"], check=False)
                return f"Volume set to {lvl} percent."

    except Exception:
        pass

    return "Adjusted volume."


def take_screenshot() -> str:
    """Takes a screenshot and saves it to user's Desktop or Pictures."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"screenshot_{timestamp}.png"
    
    desktop_dir = os.path.expanduser("~/Desktop")
    if not os.path.exists(desktop_dir):
        desktop_dir = os.path.expanduser("~")
    
    filepath = os.path.join(desktop_dir, filename)

    try:
        if CURRENT_OS == "darwin":
            subprocess.run(["screencapture", "-x", filepath], check=True)
            return f"Screenshot saved to your Desktop as {filename}."
        elif CURRENT_OS == "windows":
            # Using PowerShell ImageGrab or native Snipping
            ps_script = (
                f"Add-Type -AssemblyName System.Windows.Forms; "
                f"$screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds; "
                f"$bitmap = New-Object System.Drawing.Bitmap $screen.Width, $screen.Height; "
                f"$graphic = [System.Drawing.Graphics]::FromImage($bitmap); "
                f"$graphic.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size); "
                f"$bitmap.Save('{filepath}');"
            )
            subprocess.run(["powershell", "-Command", ps_script], check=True, creationflags=0x08000000)
            return f"Screenshot saved to {filename}."
        elif CURRENT_OS == "linux":
            try:
                subprocess.run(["gnome-screenshot", "-f", filepath], check=True)
            except FileNotFoundError:
                subprocess.run(["scrot", filepath], check=True)
            return f"Screenshot saved to {filename}."
    except Exception:
        # Try Pillow ImageGrab if available
        try:
            from PIL import ImageGrab
            img = ImageGrab.grab()
            img.save(filepath)
            return f"Screenshot captured and saved to {filename}."
        except Exception:
            return "Sorry, I was unable to capture a screenshot."


def lock_workstation() -> str:
    """Locks the computer screen."""
    try:
        if CURRENT_OS == "darwin":
            # Lock macOS
            subprocess.run(["pmset", "displaysleepnow"], check=False)
            return "Locking your screen."
        elif CURRENT_OS == "windows":
            # Lock Windows
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=False)
            return "Locking your computer."
        elif CURRENT_OS == "linux":
            # Lock Linux
            subprocess.run(["xdg-screensaver", "lock"], check=False)
            return "Locking your screen."
    except Exception:
        pass
    return "Unable to lock the workstation."
