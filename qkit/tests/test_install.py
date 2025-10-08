import pytest

import qkit


def test_qkit_import_and_start():
    """
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