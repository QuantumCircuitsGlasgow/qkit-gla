# root init for QKIT
# these directories are treated as modules
# HR@KIT/2017/2018
__all__ = [
    "config",
    "gui",
    "measure",
    "tools",
    "analysis",
    "core",
    "instruments",
    "services",
    "storage",
    "logs",
]

import os.path


class QkitCfgError(Exception):
    """
    If something with qkit.cfg does not fit to what the user wants to do, this is the error to throw.
    """



class ConfClass(dict):
    def __init__(self, *args):
        dict.__init__(self, args)

    def preset_analyse(self, verbose=False):
        """Sets basic settings, most of the services are not loaded (default)
        The file index service is run and the UUID registry is populated.
        """
        self["debug"] = False

        self["load_info_service"] = False
        self["load_ri_service"] = False
        self["load_visa"] = False
        if verbose:
            print("Not starting the info_service, ri_service and visa.")

    def preset_measure(self, verbose=False):
        """Setup of the measurement settings, services are loaded or initialized."""
        self["load_info_service"] = True
        self["load_ri_service"] = True
        self["load_visa"] = True

        if self["datadir"] == os.path.join(self["qkitdir"], "data"):
            print("Please set a valid data directory! (datadir)")
        if verbose:
            print("Starting the info_service, ri_service and visa.")

    def get(self, item, default=None):
        try:
            return self[item]
        except KeyError:
            if default is not None:
                self[item] = default
            return default


cfg = ConfClass()

# load configuration from $QKITDIR/config/*

try:
    from qkit.config.environment import cfg as cfg_local

    cfg.update(cfg_local)
except ImportError:
    pass

# if a local.py file is defined, load cfg dict and overwrite environment entries.
try:
    from qkit.config.local import cfg_local

    cfg.update(cfg_local)
except ImportError:
    pass

try:
    from qkit.config.local import cfg as cfg_local

    cfg.update(cfg_local)
except ImportError:
    pass

# clean up
del cfg_local
# init message
print("QKIT configuration initialized -> available as qkit.cfg[...]")

"""
Initialize module availability checker early so it's available for imports
"""
from pkgutil import find_loader

class ModuleAvailabilityChecker:
    """Checks for available modules and provides module availability information."""
    
    def __init__(self):
        self.available_modules = {}

    def module_available(self, module_name):
        """Check if a module is available for import."""
        if module_name not in self.available_modules:
            self.available_modules[module_name] = bool(find_loader(module_name))
        return self.available_modules[module_name]

    def __call__(self, module_name):
        return self.module_available(module_name)

    def __getitem__(self, module_name):
        return self.module_available(module_name)

    def __str__(self):
        return str(self.available_modules)

# Make module_available available immediately
module_available = ModuleAvailabilityChecker()

"""
startup functions
"""


# start initialization (qkit/core/init)
def start(silent=False):
    if not silent:
        print("Starting QKIT framework ... -> qkit.core.startup")
    import qkit.core.startup

    qkit.core.startup.start(silent=silent)


"""
add a few convenience shortcuts 
"""
# remote interface client after qkit.start_ric() -> qkit.ric
