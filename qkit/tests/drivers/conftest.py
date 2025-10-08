"""
Test configuration and fixtures for driver tests.

This module provides common test configurations, fixtures, and utilities
for testing qkit drivers.
"""

from unittest.mock import Mock, patch

import numpy as np
import pytest


@pytest.fixture
def mock_visa_instrument():
    """Fixture providing a mocked VISA instrument."""
    mock = Mock()
    mock.write = Mock()
    mock.query = Mock()
    mock.query_binary_values = Mock()
    mock.ask = Mock()
    mock.ask_for_values = Mock()
    return mock


@pytest.fixture
def sample_trace_data():
    """Fixture providing sample S21 trace data for testing."""
    # Generate realistic S21 data with a resonance dip
    freqs = np.linspace(4e9, 5e9, 1001)
    center_freq = 4.5e9
    Q = 1000
    
    # Simple resonator model
    s21 = 1.0 / (1.0 + 2j * Q * (freqs - center_freq) / center_freq)
    
    # Add some noise
    noise = 0.01 * (np.random.randn(len(freqs)) + 1j * np.random.randn(len(freqs)))
    s21 += noise
    
    return {
        'frequencies': freqs,
        's21_complex': s21,
        'amplitude': np.abs(s21),
        'phase': np.angle(s21),
        'real': s21.real,
        'imag': s21.imag
    }


@pytest.fixture
def frequency_sweep_params():
    """Fixture providing standard frequency sweep parameters."""
    return {
        'start_freq': 4e9,
        'stop_freq': 5e9,
        'center_freq': 4.5e9,
        'span': 1e9,
        'nop': 1001
    }


class MockVNAResponse:
    """Helper class for creating realistic VNA response data."""
    
    @staticmethod
    def create_s21_response(freqs, resonant_freq=4.5e9, Q=1000, noise_level=0.01):
        """Create a realistic S21 response with a resonance dip."""
        s21 = 1.0 / (1.0 + 2j * Q * (freqs - resonant_freq) / resonant_freq)
        
        if noise_level > 0:
            noise = noise_level * (np.random.randn(len(freqs)) + 1j * np.random.randn(len(freqs)))
            s21 += noise
        
        return s21
    
    @staticmethod
    def interleave_complex_data(complex_data):
        """Convert complex data to interleaved real/imag format as VNA would return."""
        real_parts = complex_data.real
        imag_parts = complex_data.imag
        
        # Interleave real and imaginary parts
        interleaved = np.empty(2 * len(complex_data))
        interleaved[0::2] = real_parts
        interleaved[1::2] = imag_parts
        
        return interleaved


# Test markers for categorizing tests
pytest_marks = {
    'unit': pytest.mark.unit,
    'integration': pytest.mark.integration,
    'hardware': pytest.mark.hardware,
    'slow': pytest.mark.slow
}


def requires_hardware(test_func):
    """Decorator to mark tests that require hardware."""
    return pytest.mark.hardware(test_func)


def skip_if_no_visa():
    """Skip test if VISA is not available."""
    try:
        import visa
        return False
    except ImportError:
        return True
