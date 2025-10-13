import os
import tempfile
import pytest
import logging

import qkit


@pytest.mark.integration
class TestQkitInstallation:
    """Test suite to verify qkit installation and startup functionality."""

    def test_qkit_import(self):
        """Test if qkit can be imported successfully."""
        assert qkit is not None, "qkit was not imported correctly"

    def test_qkit_configuration(self):
        """Test if qkit configuration is properly initialized."""
        # Check that basic configuration keys exist
        assert 'qkitdir' in qkit.cfg, "qkitdir not found in qkit.cfg"
        assert 'logdir' in qkit.cfg, "logdir not found in qkit.cfg"
        assert 'datadir' in qkit.cfg, "datadir not found in qkit.cfg"
        assert 'tempdir' in qkit.cfg, "tempdir not found in qkit.cfg"
        
        # Check that paths are valid strings
        assert isinstance(qkit.cfg['qkitdir'], str), "qkitdir should be a string"
        assert isinstance(qkit.cfg['tempdir'], str), "tempdir should be a string"

    def test_log_directory_setup(self):
        """Test if log directory is properly set up and writable."""
        logdir = qkit.cfg.get('logdir')
        if logdir:
            # Try to create the directory if it doesn't exist
            try:
                os.makedirs(logdir, exist_ok=True)
                # Test if we can write to it
                test_file = os.path.join(logdir, 'test_write_pytest.tmp')
                with open(test_file, 'w') as f:
                    f.write('pytest test')
                # Clean up
                if os.path.exists(test_file):
                    os.remove(test_file)
            except (OSError, PermissionError):
                # It's okay if we can't write to the log directory
                # (e.g., in pip-installed environments)
                pytest.skip("Log directory not writable - this is expected in pip installations")

    @pytest.mark.slow
    def test_qkit_start_silent(self):
        """Test qkit.start() in silent mode."""
        try:
            qkit.start(silent=True)
        except Exception as e:
            pytest.fail(f"qkit.start(silent=True) failed with error: {str(e)}")

    @pytest.mark.slow
    def test_qkit_start_verbose(self):
        """Test qkit.start() in verbose mode."""
        try:
            qkit.start(silent=False)
        except Exception as e:
            pytest.fail(f"qkit.start(silent=False) failed with error: {str(e)}")

    def test_qkit_core_objects_initialized(self):
        """Test if core qkit objects are properly initialized after startup."""
        # Ensure qkit has been started
        qkit.start(silent=True)
        
        # Check for instruments
        assert hasattr(qkit, 'instruments'), "qkit.instruments not found after startup"
        assert qkit.instruments is not None, "qkit.instruments is None"
        
        # Check for flow control
        assert hasattr(qkit, 'flow'), "qkit.flow not found after startup"
        assert qkit.flow is not None, "qkit.flow is None"
        
        # Check for module availability checker
        assert hasattr(qkit, 'module_available'), "qkit.module_available not found after startup"
        assert qkit.module_available is not None, "qkit.module_available is None"
        
        # Check for info service
        assert hasattr(qkit, 'info'), "qkit.info not found after startup"
        assert qkit.info is not None, "qkit.info is None"

    def test_module_availability_checker(self):
        """Test the module availability checker functionality."""
        # Ensure qkit has been started
        qkit.start(silent=True)
        
        # Test with a module that should always be available
        assert qkit.module_available('os') == True, "os module should be available"
        
        # Test with a module that likely doesn't exist
        assert qkit.module_available('nonexistent_module_xyz123') == False, "nonexistent module should not be available"
        
        # Test callable interface
        assert qkit.module_available('sys') == True, "sys module should be available via callable interface"

    def test_flow_control_methods(self):
        """Test that flow control methods are properly set up."""
        # Ensure qkit has been started
        qkit.start(silent=True)
        
        # Check that flow control methods exist
        assert hasattr(qkit.flow, 'sleep'), "qkit.flow.sleep not found"
        assert hasattr(qkit.flow, 'start'), "qkit.flow.start not found"
        assert hasattr(qkit.flow, 'end'), "qkit.flow.end not found"
        assert hasattr(qkit.flow, 'measurement_idle'), "qkit.flow.measurement_idle not found"
        assert hasattr(qkit.flow, 'measurement_start'), "qkit.flow.measurement_start not found"
        assert hasattr(qkit.flow, 'measurement_end'), "qkit.flow.measurement_end not found"

    def test_logging_setup(self):
        """Test that logging is properly configured."""
        # Ensure qkit has been started
        qkit.start(silent=True)
        
        # Get the root logger
        root_logger = logging.getLogger()
        
        # Check that handlers have been added
        assert len(root_logger.handlers) > 0, "No logging handlers found"
        
        # Test that we can log a message without errors
        try:
            logging.info("Test log message from pytest")
            logging.debug("Test debug message from pytest")
        except Exception as e:
            pytest.fail(f"Logging failed with error: {str(e)}")

    def test_git_info_handling(self):
        """Test that git information is handled properly (if available)."""
        # Ensure qkit has been started
        qkit.start(silent=True)
        
        # Check that git info exists (should be set even if no git repo)
        assert hasattr(qkit, 'git'), "qkit.git not found after startup"
        assert isinstance(qkit.git, dict), "qkit.git should be a dictionary"
        assert 'timestamp' in qkit.git, "git timestamp not found"
        assert 'commit_id' in qkit.git, "git commit_id not found"

    def test_visa_configuration(self):
        """Test VISA configuration (if VISA is available)."""
        # Ensure qkit has been started
        qkit.start(silent=True)
        
        # Check VISA loading configuration
        visa_config = qkit.cfg.get('load_visa', True)
        assert isinstance(visa_config, bool), "load_visa config should be boolean"
        
        # If VISA was successfully loaded, check that it's available
        if hasattr(qkit, 'visa') and qkit.visa is not None:
            # VISA is available, test basic functionality
            assert qkit.visa is not None, "qkit.visa should not be None if loaded"

    def test_file_service_configuration(self):
        """Test file service configuration."""
        # Ensure qkit has been started
        qkit.start(silent=True)
        
        # Check file service configuration
        fid_config = qkit.cfg.get('fid_scan_datadir', True)
        assert isinstance(fid_config, bool), "fid_scan_datadir config should be boolean"

    def test_startup_idempotency(self):
        """Test that calling qkit.start() multiple times doesn't cause issues."""
        try:
            # Start qkit multiple times
            qkit.start(silent=True)
            qkit.start(silent=True)
            qkit.start(silent=False)
            qkit.start(silent=True)
        except Exception as e:
            pytest.fail(f"Multiple qkit.start() calls failed with error: {str(e)}")

    def test_temp_directory_configuration(self):
        """Test that temp directory is properly configured."""
        # Ensure qkit has been started
        qkit.start(silent=True)
        
        tempdir = qkit.cfg.get('tempdir')
        assert tempdir is not None, "tempdir should be configured"
        assert os.path.exists(tempdir), f"tempdir {tempdir} should exist"
        
        # Test that we can write to temp directory
        try:
            test_file = os.path.join(tempdir, 'qkit_pytest_temp_test.tmp')
            with open(test_file, 'w') as f:
                f.write('pytest temp test')
            assert os.path.exists(test_file), "Could not create file in temp directory"
            # Clean up
            os.remove(test_file)
        except Exception as e:
            pytest.fail(f"Could not write to temp directory: {str(e)}")


def test_qkit_import_and_start():
    """
    Legacy test function to ensure backward compatibility.
    Test if qkit can be imported and started successfully.
    This ensures the package has been installed correctly.
    """
    try:
        assert qkit is not None, "qkit was not imported correctly"
        
        # Try to start qkit
        qkit.start()
        
        # If we've made it here without exceptions, the test passes
        assert True
    except ImportError:
        pytest.fail("Failed to import qkit. The package may not be installed correctly.")
    except Exception as e:
        pytest.fail(f"qkit.start() failed with error: {str(e)}")