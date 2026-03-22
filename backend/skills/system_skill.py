import os
import subprocess
import datetime
from typing import Dict, Any

from skills.base_skill import BaseSkill
from system_control import SystemControl

sys_ctrl = SystemControl()

class BatteryStatusSkill(BaseSkill):
    name = "get_battery_status"
    description = "Check the current battery level and charging status."
    parameters = {
        "type": "object",
        "properties": {},
        "required": []
    }

    def execute(self, **kwargs) -> str:
        return sys_ctrl.get_battery_status()

class SystemInfoSkill(BaseSkill):
    name = "get_system_info"
    description = "Get CPU usage, RAM utilization, and Disk storage capacity."
    parameters = {
        "type": "object",
        "properties": {},
        "required": []
    }

    def execute(self, **kwargs) -> str:
        info = sys_ctrl.get_system_info()
        if "error" in info: return info["error"]
        return f"CPU: {info['cpu_usage']}, RAM: {info['ram_percent']} used ({info['ram_used']}), Disk: {info['disk_percent']} used."

class OpenAppSkill(BaseSkill):
    name = "open_application"
    description = "Open an application or program installed on the local Windows PC (e.g., notepad, vscode, chrome, calc)."
    parameters = {
        "type": "object",
        "properties": {
            "app_name": {
                "type": "string",
                "description": "Name of the application or process to open"
            }
        },
        "required": ["app_name"]
    }

    def execute(self, app_name: str, **kwargs) -> str:
        return sys_ctrl.open_app(app_name)

class OpenWebsiteSkill(BaseSkill):
    name = "open_website"
    description = "Open a specific website by URL or common name in the browser."
    parameters = {
        "type": "object",
        "properties": {
            "site": {
                "type": "string", 
                "description": "The site name (youtube, facebook) or URL (https://...)"
            }
        },
        "required": ["site"]
    }

    def execute(self, site: str, **kwargs) -> str:
        if site.startswith("http"):
            return sys_ctrl.open_browser(url=site)
        return sys_ctrl.open_website(site)

class SearchWebSkill(BaseSkill):
    name = "search_web"
    description = "Perform a Google search for the specified query in the default browser."
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search term to look up"
            }
        },
        "required": ["query"]
    }

    def execute(self, query: str, **kwargs) -> str:
        return sys_ctrl.search_web(query)

class TakeScreenshotSkill(BaseSkill):
    name = "take_screenshot"
    description = "Capture an image of the current screen and save to Desktop."
    parameters = {
        "type": "object",
        "properties": {},
        "required": []
    }

    def execute(self, **kwargs) -> str:
        return sys_ctrl.take_screenshot()

class GetTimeSkill(BaseSkill):
    name = "get_time"
    description = "Get the current operating system local time and date."
    parameters = {
        "type": "object",
        "properties": {},
        "required": []
    }

    def execute(self, **kwargs) -> str:
        d = sys_ctrl.get_date()
        t = sys_ctrl.get_time()
        return f"{d} {t}"

# Export them so brain.py can dynamically load them
AVAILABLE_SKILLS = [
    BatteryStatusSkill(),
    SystemInfoSkill(),
    OpenAppSkill(),
    OpenWebsiteSkill(),
    SearchWebSkill(),
    TakeScreenshotSkill(),
    GetTimeSkill()
]
