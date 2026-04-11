from jarvis.tools.registry import registry
from datetime import datetime

@registry.register(name="get_time", description="Returns the current local time. ALWAYS call this tool when the user asks for the time to ensure accuracy, as the time changes every second.")
def get_time() -> str:
    return datetime.now().strftime("%H:%M:%S")

@registry.register(name="get_date", description="Returns the current local date. ALWAYS call this tool when the user asks for the date to ensure accuracy, as it changes daily.")
def get_date() -> str:
    return datetime.now().strftime("%Y-%m-%d")