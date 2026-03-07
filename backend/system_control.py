"""
FRIDAY System Control — Windows PC Control
Controls: apps, browser, files, volume, screenshots, processes
"""

import os
import subprocess
import time
import datetime
import platform


class SystemControl:
    def __init__(self):
        if platform.system() != "Windows":
            print("[SYSTEM] ⚠️  Warning: SystemControl optimized for Windows.")
        print("[SYSTEM] System Control initialized.")

    
    BROWSERS = {
        "chrome":  [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ],
        "brave":   [
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"),
        ],
        "firefox": [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
        ],
        "edge":    [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ],
        "opera":   [
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Opera\launcher.exe"),
        ],
    }

    def _find_browser_exe(self, browser_name: str) -> str | None:
        """Find the actual .exe path for a browser."""
        paths = self.BROWSERS.get(browser_name.lower(), [])
        for path in paths:
            if os.path.exists(path):
                return path
        return None

    def open_url_in_browser(self, url: str, browser: str = "default") -> str:
        """Open a URL in a specific browser or default browser."""
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        if browser == "default":
            import webbrowser
            webbrowser.open(url)
            return f"Opening {url} in your default browser, Jackson."

        exe = self._find_browser_exe(browser)
        if exe:
            subprocess.Popen([exe, url])
            return f"Opening {url} in {browser.capitalize()}, Boss."
        else:
            
            import webbrowser
            webbrowser.open(url)
            return (f"Couldn't find {browser.capitalize()} installed, Jackson. "
                    f"Opening in your default browser instead.")

    def open_browser(self, url: str = "https://www.google.com", browser: str = "default") -> str:
        return self.open_url_in_browser(url, browser)

    def search_web(self, query: str, browser: str = "default") -> str:
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        result = self.open_url_in_browser(url, browser)
        return f"Searching for '{query}'. {result}"

    def open_website(self, site: str, browser: str = "default") -> str:
        """Open a specific website like Instagram, YouTube, etc."""
        site_map = {
            "instagram":  "https://www.instagram.com",
            "youtube":    "https://www.youtube.com",
            "facebook":   "https://www.facebook.com",
            "twitter":    "https://www.twitter.com",
            "x":          "https://www.x.com",
            "reddit":     "https://www.reddit.com",
            "github":     "https://www.github.com",
            "gmail":      "https://mail.google.com",
            "google":     "https://www.google.com",
            "netflix":    "https://www.netflix.com",
            "whatsapp":   "https://web.whatsapp.com",
            "linkedin":   "https://www.linkedin.com",
            "amazon":     "https://www.amazon.com",
            "chatgpt":    "https://chat.openai.com",
            "spotify":    "https://open.spotify.com",
        }
        url = site_map.get(site.lower(), f"https://www.{site}.com")
        return self.open_url_in_browser(url, browser)

    def open_youtube(self, query: str = "", browser: str = "default") -> str:
        if query:
            url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        else:
            url = "https://www.youtube.com"
        return self.open_url_in_browser(url, browser)

    

    APP_MAP = {
        "notepad":       "notepad.exe",
        "calculator":    "calc.exe",
        "paint":         "mspaint.exe",
        "explorer":      "explorer.exe",
        "task manager":  "taskmgr.exe",
        "cmd":           "cmd.exe",
        "command prompt":"cmd.exe",
        "powershell":    "powershell.exe",
        "settings":      "ms-settings:",
        "control panel": "control.exe",
        "snipping tool": "snippingtool.exe",
        "discord":       "discord.exe",
        "vscode":        "code",
        "visual studio code": "code",
        "word":          "winword.exe",
        "excel":         "excel.exe",
        "powerpoint":    "powerpnt.exe",
        "outlook":       "outlook.exe",
        "teams":         "teams.exe",
        "zoom":          "zoom.exe",
        "vlc":           "vlc.exe",
        "file explorer": "explorer.exe",
    }

    def open_app(self, app_name: str) -> str:
        app_lower = app_name.lower().strip()
        exe = self.APP_MAP.get(app_lower, app_name)
        try:
            if exe.startswith("ms-"):
                subprocess.Popen(["start", exe], shell=True)
            else:
                subprocess.Popen(exe, shell=True)
            return f"Opening {app_name}, Jackson."
        except Exception as e:
            return f"Could not open {app_name}: {e}"

    def close_app(self, app_name: str) -> str:
        try:
            subprocess.run(["taskkill", "/F", "/IM", f"{app_name}.exe"], capture_output=True)
            return f"{app_name} has been closed, Jackson."
        except Exception as e:
            return f"Failed to close {app_name}: {e}"

    

    def open_folder(self, path: str) -> str:
        if not os.path.exists(path):
            return f"Path does not exist: {path}"
        subprocess.Popen(["explorer", path])
        return f"Opening folder: {path}"

    def create_folder(self, path: str) -> str:
        try:
            os.makedirs(path, exist_ok=True)
            return f"Folder created at: {path}"
        except Exception as e:
            return f"Could not create folder: {e}"

    def list_files(self, path: str = ".") -> list[str]:
        try:
            return os.listdir(path)
        except Exception as e:
            return [f"Error: {e}"]

    

    def take_screenshot(self, save_path: str = None) -> str:
        try:
            import pyautogui
            if not save_path:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = os.path.join(
                    os.path.expanduser("~"), "Desktop", f"FRIDAY_screenshot_{timestamp}.png"
                )
            screenshot = pyautogui.screenshot()
            screenshot.save(save_path)
            return f"Screenshot saved to your Desktop, Jackson."
        except ImportError:
            return "pyautogui not installed. Run: pip install pyautogui pillow"
        except Exception as e:
            return f"Screenshot failed: {e}"

    def get_battery_status(self) -> str:
        try:
            import psutil
            battery = psutil.sensors_battery()
            if battery:
                pct = battery.percent
                charging = "charging" if battery.power_plugged else "on battery"
                return f"Battery at {pct:.0f}%, {charging}, Jackson."
            return "No battery detected — this appears to be a desktop system."
        except ImportError:
            return "psutil not installed. Run: pip install psutil"

    def get_system_info(self) -> dict:
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            return {
                "cpu_usage":    f"{cpu}%",
                "ram_used":     f"{ram.used // (1024**3):.1f} GB",
                "ram_total":    f"{ram.total // (1024**3):.1f} GB",
                "ram_percent":  f"{ram.percent}%",
                "disk_used":    f"{disk.used // (1024**3):.1f} GB",
                "disk_total":   f"{disk.total // (1024**3):.1f} GB",
                "disk_percent": f"{disk.percent}%",
            }
        except ImportError:
            return {"error": "Install psutil: pip install psutil"}

    def shutdown(self, delay: int = 30) -> str:
        subprocess.run(["shutdown", "/s", "/t", str(delay)])
        return f"System will shut down in {delay} seconds, Jackson."

    def cancel_shutdown(self) -> str:
        subprocess.run(["shutdown", "/a"])
        return "Shutdown cancelled, Jackson."

    def restart(self, delay: int = 30) -> str:
        subprocess.run(["shutdown", "/r", "/t", str(delay)])
        return f"System will restart in {delay} seconds, Jackson."

    def lock_screen(self) -> str:
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
        return "Screen locked, Jackson."

    def get_time(self) -> str:
        return datetime.datetime.now().strftime("It's %I:%M %p, Jackson.")

    def get_date(self) -> str:
        return datetime.datetime.now().strftime("Today is %A, %B %d, %Y.")

    

    def parse_and_execute(self, command: str) -> str | None:
        """
        Parse natural language → execute real system command.
        Returns result string if handled, None if AI should handle it.
        """
        cmd = command.lower().strip()

        
        browser = "default"
        for b in ["brave", "chrome", "firefox", "edge", "opera"]:
            if b in cmd:
                browser = b
                break

        
        if any(w in cmd for w in ["what time", "current time", "tell me the time", "what's the time"]):
            return self.get_time()
        if any(w in cmd for w in ["what day", "what date", "today's date", "what's today"]):
            return self.get_date()

        
        websites = [
            "instagram", "youtube", "facebook", "twitter", "reddit",
            "github", "gmail", "netflix", "whatsapp", "linkedin",
            "amazon", "chatgpt", "spotify", "google", "x"
        ]
        for site in websites:
            if site in cmd and "open" in cmd:
                return self.open_website(site, browser)
            
            if site in cmd and any(w in cmd for w in ["go to", "show me", "launch", "start"]):
                return self.open_website(site, browser)

       
        if "youtube" in cmd:
            q = cmd.replace("open youtube", "").replace("youtube", "").replace("search", "").strip()
            return self.open_youtube(q, browser)

        
        if "search" in cmd and any(w in cmd for w in ["google", "web", "for", "look up", "find"]):
            q = (cmd.replace("search google for", "")
                    .replace("search for", "")
                    .replace("google", "")
                    .replace("search", "")
                    .replace("web", "")
                    .strip())
            if q:
                return self.search_web(q, browser)

        
        if "open" in cmd and any(x in cmd for x in ["browser", "chrome", "edge", "firefox", "brave", "opera"]):
            return self.open_browser("https://www.google.com", browser)

        
        for app in self.APP_MAP.keys():
            if f"open {app}" in cmd or f"launch {app}" in cmd or f"start {app}" in cmd:
                return self.open_app(app)

        
        if "screenshot" in cmd or "screen capture" in cmd or "capture screen" in cmd:
            return self.take_screenshot()

    
        if "battery" in cmd or "charging" in cmd:
            return self.get_battery_status()
        if any(w in cmd for w in ["system info", "system status", "cpu", "ram usage", "memory usage"]):
            info = self.get_system_info()
            return (f"CPU at {info.get('cpu_usage', 'N/A')}, "
                    f"RAM {info.get('ram_percent', 'N/A')} used, "
                    f"Disk {info.get('disk_percent', 'N/A')} used, Jackson.")

        
        if "lock" in cmd and any(w in cmd for w in ["screen", "computer", "pc", "windows"]):
            return self.lock_screen()

        
        if "shutdown" in cmd or "shut down" in cmd:
            return self.shutdown()
        if "restart" in cmd or "reboot" in cmd:
            return self.restart()

        return None  


if __name__ == "__main__":
    ctrl = SystemControl()
    print(ctrl.get_time())
    print(ctrl.get_date())
    
    tests = ["open instagram in brave", "open youtube", "system status", "what time is it"]
    for t in tests:
        r = ctrl.parse_and_execute(t)
        print(f"'{t}' → {r}")
