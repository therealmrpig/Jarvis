from jarvis.tools.registry import registry as registry
from . import system_tools as system_tools
from . import system_info as system_info
from . import weather_tools as weather_tools


# Each time a new tool file is added (e.g., file_ops.py), 
# it MUST be imported here to self-register.
