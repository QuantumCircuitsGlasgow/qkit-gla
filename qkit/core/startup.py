# This file brings QKIT around: init
# YS@KIT/2017
# HR@kit/2017
# Completely rewritten and modernized for pip installation compatibility

"""
This file sets up the logger and loads the core modules of the Qkit framework.
All initialization functionality has been consolidated into this single file
using a class-based approach for better maintainability and pip compatibility.

This start() function is called by the qkit/__init__.py file.
Based on the environment file variables in qkit/config/environment.py,
it loads the core modules of the Qkit framework.
"""
import logging
import os
import sys
import tempfile
from distutils.version import LooseVersion
from os.path import join
from pkgutil import find_loader
from time import strftime, time

import qkit


class CustomFormatter(logging.Formatter):
    """Custom colored logging formatter for console output."""
    purple = "\x1b[35;1m"
    blue = "\x1b[34;1m"
    yellow = "\x1b[43;34;1m"
    red = "\x1b[31;1m"
    bold_red = "\x1b[31;43;1m"
    reset = "\x1b[0m"

    log_format = "%(asctime)s [ %(levelname)-4s ]|: %(message)s <%(filename)s :%(funcName)s:%(lineno)d>"

    FORMATS = {
        logging.DEBUG: purple + log_format + reset,
        logging.INFO: blue + log_format + reset,
        logging.WARNING: yellow + log_format + reset,
        logging.ERROR: red + log_format + reset,
        logging.CRITICAL: bold_red + log_format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


class LoggingInitializer:
    """Handles logging setup and configuration (S10_logging)."""
    
    @staticmethod
    def cleanup_logfiles():
        """Clean up old log files, keeping only the latest 10."""
        if qkit.cfg.get("maintain_logfiles", True):
            logdir = qkit.cfg.get("logdir")
            if not logdir or not os.path.exists(logdir):
                return  # Skip cleanup if log directory doesn't exist or isn't accessible
            
            try:
                ld = [
                    filename
                    for filename in os.listdir(logdir)
                    if filename.startswith("qkit") and filename.endswith(".log")
                ]
                ld.sort()
                for f in ld[:-10]:
                    try:
                        os.remove(os.path.join(logdir, f))
                    except Exception:
                        pass  # Ignore cleanup errors
            except Exception:
                pass  # Skip cleanup if directory isn't readable    @staticmethod
    def setup():
        """Set up logging system."""
        debug_level = qkit.cfg.get("debug", "WARNING")
        file_log_level = qkit.cfg.get("file_log_level", "WARNING") 
        stdout_log_level = qkit.cfg.get("stdout_log_level", "WARNING")
        
        level = getattr(logging, debug_level or "WARNING")
        fileLogLevel = getattr(logging, file_log_level or "WARNING")
        stdoutLogLevel = getattr(logging, stdout_log_level or "WARNING")

        rootLogger = logging.getLogger()

        # Try to set up file logging, but handle cases where log directory isn't writable
        logdir = qkit.cfg.get("logdir")
        file_handler_created = False
        
        if logdir:
            try:
                # Ensure log directory exists and is writable
                os.makedirs(logdir, exist_ok=True)
                log_filename = os.path.join(logdir, strftime("qkit_%Y%m%d_%H%M%S.log"))
                
                fileLogger = logging.FileHandler(
                    filename=log_filename,
                    mode="a+",
                )
                fileLogger.setFormatter(
                    logging.Formatter(
                        "%(asctime)s %(levelname)-4s: %(message)s <%(pathname)s -> %(module)s->%(funcName)s:%(lineno)d>",
                        datefmt="%Y-%m-%d %H:%M:%S",
                    )
                )
                fileLogger.setLevel(min(level, fileLogLevel))
                rootLogger.addHandler(fileLogger)
                file_handler_created = True
                
            except (OSError, PermissionError) as e:
                # If we can't write to the log directory, just use console logging
                print(f"Warning: Could not set up file logging (directory not writable): {e}")
                print(f"Continuing with console logging only")

        jupyterLogger = logging.StreamHandler(sys.stdout)
        jupyterLogger.setFormatter(CustomFormatter())
        jupyterLogger.setLevel(level)

        rootLogger.addHandler(jupyterLogger)
        rootLogger.setLevel(min(level, fileLogLevel if file_handler_created else stdoutLogLevel))

        logging.info(" ---------- LOGGING STARTED ---------- ")

        if file_handler_created:
            logging.debug("Set logging level for file to: %s " % fileLogLevel)
        logging.debug("Set logging level for stdout to: %s " % stdoutLogLevel)

        if file_handler_created:
            LoggingInitializer.cleanup_logfiles()


class DirectorySetup:
    """Handles directory setup and path management (S14_setup_directories)."""
    
    @staticmethod
    def setup():
        """Set up instrument directories and add them to sys.path."""
        # Set up main instruments directory
        instdir = qkit.cfg.get("instruments_dir", None)
        if instdir and os.path.exists(instdir):
            if instdir not in sys.path:
                sys.path.append(instdir)
            qkit.cfg["instruments_dir"] = instdir
            logging.info("Set instruments dir to %s" % instdir)
        else:
            qkit.cfg["instruments_dir"] = None
            if instdir:
                logging.warning(
                    'DirectorySetup: "%s" is not a valid path for instruments_dir, setting to None' % instdir
                )

        # Set up user instruments directory
        user_instdir = qkit.cfg.get("user_instruments_dir", None)
        if user_instdir and os.path.exists(user_instdir):
            absdir = os.path.abspath(user_instdir)
            qkit.cfg["user_instruments_dir"] = absdir
            if absdir not in sys.path:
                sys.path.append(absdir)
            logging.info("Set user instruments dir to %s" % absdir)
        else:
            qkit.cfg["user_instruments_dir"] = None
            if user_instdir:
                logging.info(
                    'DirectorySetup: "%s" is not a valid path for user_instruments_dir, setting to None' % user_instdir
                )


class ModuleAvailabilityChecker:
    """Checks for available modules and provides module availability information (S16_available_modules)."""
    
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

    def setup(self):
        """Initialize module availability checker and assign to qkit."""
        # The module_available is already created in __init__.py, so we just ensure it's complete
        if not hasattr(qkit, 'module_available') or qkit.module_available is None:
            qkit.module_available = self
        logging.debug("Module availability checker initialized")


class UpdateChecker:
    """Checks for git updates and repository information (S20_check_for_updates)."""
    
    @staticmethod
    def setup():
        """Check git repository status and warn about outdated versions."""
        if qkit.cfg.get("check_for_updates", False):
            try:
                git_head_path = join(qkit.cfg["qkitdir"], "../.git/logs/HEAD")
                with open(git_head_path, "rb") as f:
                    f.seek(-1024, 2)
                    last_commit = (
                        f.readlines()[-1].decode().split("\t")[0]
                    )
                    setattr(qkit, 'git', {
                        "timestamp": float(last_commit.split(" ")[-2]),
                        "commit_id": last_commit.split(" ")[1],
                    })
                    git_obj = getattr(qkit, 'git')
                    if (time() - git_obj["timestamp"]) / 3600 / 24 > 21:
                        logging.warning(
                            "Your qkit version is older than 3 weeks. Please consider the 'git pull' command. We are usually trying to get better."
                        )
            except Exception:
                qkit.git = {"timestamp": None, "commit_id": "UNTRACKED-NO_GIT_FOUND"}
                logging.info(
                    "You are not operating qkit from a git repository. You do not need to do so, but this is the easiest way to get always the latest version."
                )


class InfoService:
    """Initializes the info service for communication (S25_info_service)."""
    
    @staticmethod
    def setup():
        """Set up info service for inter-process communication."""
        if qkit.cfg.get("load_info_service", True):
            qkit.cfg["load_info_service"] = True
            try:
                from qkit.core.lib.com.info_service import info_service
                qkit.info = info_service()
                logging.debug("Info service loaded successfully")
            except ImportError:
                logging.warning("Could not load info service - zmq package may not be installed")
                # Create dummy info service
                def dummy_info_service(msg):
                    pass
                qkit.info = dummy_info_service
        else:
            # Dummy info service
            def dummy_info_service(msg):
                pass
            qkit.info = dummy_info_service


class QkitCore:
    """Initializes core qkit objects and functionality (S30_qkit_start)."""
    
    @staticmethod
    def setup():
        """Set up core qkit objects - instruments, flow control, etc."""
        # Set up temp directory
        from qkit.core.lib import temp
        temp.File.set_temp_dir(qkit.cfg["tempdir"])

        # Initialize instrument tools
        from qkit.core.instrument_tools import Insttools
        qkit.instruments = Insttools()
        logging.debug("Instrument tools initialized")        # Initialize flow control
        import qkit.core.flow as flow
        qkit.flow = flow.FlowControl()
        # Aliases are already set in FlowControl.__init__
        
        # Check for legacy qtlab compatibility (should be disabled)
        if qkit.cfg.get("qt_compatible", False):
            raise ValueError(
                "We do no longer provide legacy qtlab support. Please set qkit.cfg['qt_compatible']=False and clean up your code."
            )

        # Register exit handlers
        from qkit.core.lib.misc import register_exit
        register_exit(flow.qtlab_exit)
        logging.debug("Flow control initialized")


class RemoteInterfaceService:
    """Loads remote interface service if enabled (S65_load_RI_service)."""
    
    @staticmethod
    def setup():
        """Load remote interface service if enabled."""
        if qkit.cfg.get("load_ri_service", False):
            qkit.cfg["load_ri_service"] = True
            try:
                logging.info("Loading remote interface service")
                from qkit.core.lib.com.ri_service import RISThread
                qkit.ris = RISThread()
                logging.debug("Remote interface service loaded successfully")
            except ImportError as e:
                logging.warning(f"Could not load remote interface service: {e}")
        else:
            qkit.cfg["load_ri_service"] = False


class DummyVisa:
    """Dummy VISA class that raises errors when VISA is not loaded."""
    def __getattr__(self, name):
        from qkit import QkitCfgError
        raise QkitCfgError("Please set qkit.cfg['load_visa'] = True if you need visa.")


class VisaLoader:
    """Loads VISA library for instrument communication (S70_load_visa)."""
    
    @staticmethod
    def setup():
        """Load VISA library if enabled."""
        if qkit.cfg.get("load_visa", True):
            try:
                try:
                    import pyvisa as visa
                except ImportError:
                    import visa
                
                # Check version and handle compatibility
                try:
                    from pkg_resources import get_distribution
                    pyvisa_version = get_distribution('pyvisa').version
                    
                    if LooseVersion(pyvisa_version) < LooseVersion("1.5.0"):
                        logging.warning("Old pyvisa version loaded. Please update to a version > 1.5.x")
                        # Compatibility with old visa lib
                        qkit.visa = visa
                        qkit.visa.__version__ = pyvisa_version
                        qkit.visa.qkit_visa_version = 1  # Makes it easier to distinguish between versions
                        
                    else:
                        # Modern pyvisa version
                        logging.info("Modern pyvisa version loaded. Version %s" % visa.__version__)
                        try:
                            rm = visa.ResourceManager(qkit.cfg.get('visa_backend', ""))
                            qkit.visa = rm
                            qkit.visa.__version__ = visa.__version__
                            qkit.visa.qkit_visa_version = 2
                            qkit.visa.VisaIOError = visa.VisaIOError
                            
                            # Add instrument function for compatibility
                            def instrument(resource_name, **kwargs):
                                return rm.open_resource(resource_name, **kwargs)
                            qkit.visa.instrument = instrument
                            
                            # Define data types for compatibility
                            qkit.visa.double = "d"
                            qkit.visa.single = "f"
                            qkit.visa.dtypes = {
                                1: qkit.visa.single,
                                3: qkit.visa.double,
                                "d": "d", 
                                "f": "f"
                            }
                            
                        except OSError as e:
                            raise OSError('Failed creating ResourceManager. Check if you have NI VISA or pyvisa-py installed.') from e
                        
                except Exception as e:
                    # Fallback if pkg_resources fails
                    logging.warning(f"Could not determine pyvisa version: {e}")
                    qkit.visa = visa
                    qkit.visa.qkit_visa_version = getattr(visa, '__version__', 'unknown')
                
                logging.debug("VISA library loaded successfully")
                
            except Exception as e:
                qkit.cfg["load_visa"] = False
                logging.warning(
                    f"Failed loading visa. Check if you have NI VISA or pyvisa-py installed. Original error: {e}"
                )
                # Set dummy visa when loading fails
                qkit.visa = DummyVisa()
        else:
            # VISA loading disabled
            qkit.visa = DummyVisa()


class FileService:
    """Loads file information database service (S80_load_file_service)."""
    
    @staticmethod
    def setup():
        """Load file information database service."""
        if qkit.cfg.get("fid_scan_datadir", True):
            try:
                logging.info("Loading service: file info database (fid)")
                from qkit.core.lib.file_service.file_info_database import fid
                qkit.fid = fid()
                logging.debug("File info database service loaded successfully")
            except ImportError as e:
                logging.warning(f"Could not load file info database service: {e}")


class MeasurementInitializer:
    """Initializes measurement configuration and data structure (S85_init_measurement)."""
    
    @staticmethod
    def setup():
        """Initialize measurement configuration."""
        # Check for deprecated configuration
        if "new_data_structure" in qkit.cfg:
            raise ValueError(
                "MeasurementInitializer: Please use qkit.cfg['datafolder_structure'] = 1 instead of qkit.cfg['new_data_structure'] in your config."
            )
        
        # Handle datafolder structure configuration
        if qkit.cfg.get("datafolder_structure", 1) == 2:
            try:
                # Try to use Jupyter widgets for interactive configuration
                import ipywidgets as widgets
                from IPython.display import display

                # Create interactive widgets for run_id and user configuration
                button = widgets.Button(
                    description="Please Check!",
                    disabled=False,
                    button_style="info",
                )

                run_id_widget = widgets.Text(
                    value=str(qkit.cfg.get("run_id", "")).upper(),
                    placeholder="***RUN_ID IS EMPTY***",
                    description="Please check: Run ID",
                    disabled=False,
                    style={"description_width": "initial"},
                )

                user_widget = widgets.Text(
                    value=str(qkit.cfg.get("user", "")),
                    placeholder="***USER IS EMPTY***",
                    description="user name",
                    disabled=False,
                    style={"description_width": "initial"},
                )

                # Validate current values
                if not qkit.cfg.get("run_id", False):
                    run_id_widget.border_color = "red"
                    button.button_style = "danger"

                if not qkit.cfg.get("user", False):
                    user_widget.border_color = "red"
                    button.button_style = "danger"

                def on_button_click(btn):
                    if not run_id_widget.value:
                        raise ValueError("RUN_ID is still empty!")
                    if not user_widget.value:
                        raise ValueError("USER is still empty!")
                    qkit.cfg["run_id"] = run_id_widget.value.upper()
                    qkit.cfg["user"] = user_widget.value
                    run_id_widget.disabled = True
                    run_id_widget.border_color = "#cccccc"
                    user_widget.border_color = "#cccccc"
                    user_widget.disabled = True
                    btn.disabled = True
                    btn.button_style = "success"
                    btn.description = "Done."

                button.on_click(on_button_click)
                display(widgets.HBox([run_id_widget, user_widget, button]))
                
            except ImportError:
                # Fallback to logging warnings if Jupyter widgets not available
                if "run_id" not in qkit.cfg:
                    logging.error(
                        'You are using the new data structure, but you did not specify a run ID. Please set qkit.cfg["run_id"] NOW to avoid searching your data.'
                    )
                if "user" not in qkit.cfg:
                    logging.error(
                        'You are using the new data structure, but you did not specify a username. Please set qkit.cfg["user"] NOW to avoid searching your data.'
                    )


class StartupFinalizer:
    """Finalizes startup process and registers exit handlers (S98_started)."""
    
    @staticmethod
    def setup():
        """Finalize startup process."""
        from qkit.core.lib import temp
        
        # Register exit handlers (only if flow is available)
        flow_obj = getattr(qkit, 'flow', None)
        if flow_obj:
            flow_obj.register_exit_handler(temp.File.remove_all)
            # Clear "starting" status
            flow_obj.finished_starting()
        
        logging.debug("Startup finalization completed")


class UserInitializer:
    """Handles user-specific initialization scripts and settings (S99_init_user)."""
    
    @staticmethod
    def setup():
        """Execute user initialization scripts and settings."""
        # Change to start directory if specified
        startdir = qkit.cfg.get("startdir")
        if startdir:
            try:
                os.chdir(startdir)
                logging.debug(f"Changed to start directory: {startdir}")
            except Exception as e:
                logging.warning(f"Could not change to start directory: {e}")

        # Execute start scripts
        startscripts = qkit.cfg.get("startscript")
        if startscripts:
            if not isinstance(startscripts, (list, tuple)):
                startscripts = [startscripts]
            
            for script in startscripts:
                if script and os.path.isfile(script):
                    try:
                        print(f"Executing (user startscript): {script}")
                        # Use exec instead of execfile (Python 3 compatibility)
                        with open(script, 'r') as f:
                            exec(f.read(), globals())
                        logging.debug(f"Successfully executed start script: {script}")
                    except Exception as e:
                        logging.error(f"Error executing start script {script}: {e}")
                else:
                    logging.warning(f'Did not find startscript "{script}", skipping')

        # Register exit scripts
        exitscripts = qkit.cfg.get("exitscript")
        if exitscripts:
            if not isinstance(exitscripts, (list, tuple)):
                exitscripts = [exitscripts]
            
            for script in exitscripts:
                if script and os.path.isfile(script):
                    def exit_script_handler(script_path=script):
                        try:
                            with open(script_path, 'r') as f:
                                exec(f.read(), globals())
                        except Exception as e:
                            logging.error(f"Error executing exit script {script_path}: {e}")
                    
                    # Access qkit.flow using getattr to avoid type checking issues
                    flow_obj = getattr(qkit, 'flow', None)
                    if flow_obj:
                        flow_obj.register_exit_handler(exit_script_handler)
                        logging.debug(f"Registered exit script: {script}")


def start(silent=False):
    """Start the Qkit framework by initializing all components in order."""
    if not silent:
        print('Starting the core of the Qkit framework...')
    
    # List of initialization classes in order (matching S10, S14, S16, etc.)
    initializers = [
        ("Logging", LoggingInitializer),
        ("Directory Setup", DirectorySetup),
        ("Module Availability", ModuleAvailabilityChecker()),
        ("Update Checker", UpdateChecker),
        ("Info Service", InfoService),
        ("Qkit Core", QkitCore),
        ("Remote Interface Service", RemoteInterfaceService),
        ("VISA Loader", VisaLoader),
        ("File Service", FileService),
        ("Measurement Initializer", MeasurementInitializer),
        ("Startup Finalizer", StartupFinalizer),
        ("User Initializer", UserInitializer),
    ]
    
    # Execute all initializers
    success_count = 0
    for name, initializer in initializers:
        start_time = time()
        if not silent:
            print(f"Loading {name}...")
        
        try:
            initializer.setup()
            elapsed_time = time() - start_time
            logging.debug(f"Loading {name} took {elapsed_time:.1f}s.")
            success_count += 1
            
        except Exception as e:
            logging.error(f"Failed to load {name}: {e}")
            if not silent:
                print(f"Warning: Failed to load {name}: {e}")
    
    if not silent:
        print(f"Successfully loaded {success_count}/{len(initializers)} initialization components")
        print("Qkit framework startup completed")
