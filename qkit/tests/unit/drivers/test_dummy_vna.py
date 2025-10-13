"""
Test suite for DummyVNA driver.

This module contains comprehensive tests for the DummyVNA class,
which is a virtual VNA instrument for testing purposes.
"""

import numpy as np
import pytest

from qkit.core.instrument_base import Instrument
from qkit.drivers.DummyVNA import DummyVNA


class TestDummyVNA:
    """Test class for DummyVNA driver."""

    def setup_method(self):
        """Set up test fixture before each test method."""
        self.vna = DummyVNA("test_dummy_vna")

    def teardown_method(self):
        """Clean up after each test method."""
        if hasattr(self, 'vna'):
            del self.vna

    def test_initialization(self):
        """Test that DummyVNA initializes correctly."""
        assert self.vna.get_name() == "test_dummy_vna"
        assert "virtual" in self.vna.get_tags()
        assert isinstance(self.vna, Instrument)
        
        # Check default values
        assert self.vna.nop == 1001
        assert self.vna.startfreq == 4e9
        assert self.vna.stopfreq == 5e9
        assert self.vna.sweeptime_averages == 1
        assert self.vna.power == 0
        assert not self.vna._ready

    def test_power_parameter(self):
        """Test power parameter get/set functionality."""
        # Test initial power
        assert self.vna.get_power() == 0
        
        # Test setting power within valid range
        self.vna.set_power(-10)
        assert self.vna.get_power() == -10
        
        self.vna.set_power(5)
        assert self.vna.get_power() == 5
        
        # Test boundary values
        self.vna.set_power(-85)  # Min value
        assert self.vna.get_power() == -85
        
        self.vna.set_power(10)   # Max value
        assert self.vna.get_power() == 10

    def test_frequency_parameters(self):
        """Test frequency-related parameters and their relationships."""
        # Test initial values
        assert self.vna.get_startfreq() == 4e9
        assert self.vna.get_stopfreq() == 5e9
        assert self.vna.get_centerfreq() == 4.5e9
        assert self.vna.get_span() == 1e9

    def test_startfreq_setting(self):
        """Test setting start frequency updates other parameters correctly."""
        self.vna.set_startfreq(3e9)
        
        assert self.vna.get_startfreq() == 3e9
        assert self.vna.get_stopfreq() == 5e9  # Should remain unchanged
        assert self.vna.get_span() == 2e9      # Should update
        assert self.vna.get_centerfreq() == 4e9  # Should update

    def test_stopfreq_setting(self):
        """Test setting stop frequency updates other parameters correctly."""
        self.vna.set_stopfreq(6e9)
        
        assert self.vna.get_startfreq() == 4e9  # Should remain unchanged
        assert self.vna.get_stopfreq() == 6e9
        assert self.vna.get_span() == 2e9       # Should update
        assert self.vna.get_centerfreq() == 5e9 # Should update

    def test_centerfreq_setting(self):
        """Test setting center frequency updates start/stop frequencies correctly."""
        self.vna.set_centerfreq(5e9)
        
        assert self.vna.get_centerfreq() == 5e9
        assert self.vna.get_span() == 1e9        # Should remain unchanged
        assert self.vna.get_startfreq() == 4.5e9 # Should update
        assert self.vna.get_stopfreq() == 5.5e9  # Should update

    def test_span_setting(self):
        """Test setting span updates start/stop frequencies correctly."""
        self.vna.set_span(2e9)
        
        assert self.vna.get_span() == 2e9
        assert self.vna.get_centerfreq() == 4.5e9  # Should remain unchanged
        assert self.vna.get_startfreq() == 3.5e9   # Should update
        assert self.vna.get_stopfreq() == 5.5e9    # Should update

    def test_nop_parameter(self):
        """Test number of points parameter."""
        assert self.vna.get_nop() == 1001
        
        self.vna.set_nop(501)
        assert self.vna.get_nop() == 501
        
        self.vna.set_nop(2001)
        assert self.vna.get_nop() == 2001

    def test_freqpoints_generation(self):
        """Test frequency points generation."""
        freqpoints = self.vna.get_freqpoints()
        
        # Check array properties
        assert isinstance(freqpoints, np.ndarray)
        assert len(freqpoints) == self.vna.nop
        assert freqpoints[0] == self.vna.startfreq
        assert freqpoints[-1] == self.vna.stopfreq
        
        # Check linearity
        expected_freqpoints = np.linspace(self.vna.startfreq, self.vna.stopfreq, self.vna.nop)
        np.testing.assert_array_equal(freqpoints, expected_freqpoints)

    def test_freqpoints_with_different_nop(self):
        """Test frequency points generation with different number of points."""
        self.vna.set_nop(101)
        freqpoints = self.vna.get_freqpoints()
        
        assert len(freqpoints) == 101
        assert freqpoints[0] == self.vna.startfreq
        assert freqpoints[-1] == self.vna.stopfreq

    def test_tracedata_amplitude_phase_format(self):
        """Test trace data generation in amplitude/phase format."""
        amp, pha = self.vna.get_tracedata(RealImag=False)
        
        # Check return types and shapes
        assert isinstance(amp, np.ndarray)
        assert isinstance(pha, np.ndarray)
        assert len(amp) == self.vna.nop
        assert len(pha) == self.vna.nop
        
        # Check physical properties
        assert np.all(amp >= 0)  # Amplitude should be positive
        assert np.all(np.abs(pha) <= np.pi)  # Phase should be within [-π, π]
        
        # Check for resonance dip (amplitude should have a minimum)
        assert np.min(amp) < np.max(amp)

    def test_tracedata_real_imag_format(self):
        """Test trace data generation in real/imaginary format."""
        real, imag = self.vna.get_tracedata(RealImag=True)
        
        # Check return types and shapes
        assert isinstance(real, np.ndarray)
        assert isinstance(imag, np.ndarray)
        assert len(real) == self.vna.nop
        assert len(imag) == self.vna.nop
        
        # Check that they are reasonable values
        assert np.all(np.isfinite(real))
        assert np.all(np.isfinite(imag))

    def test_tracedata_consistency(self):
        """Test consistency between amplitude/phase and real/imaginary formats."""
        amp, pha = self.vna.get_tracedata(RealImag=False)
        real, imag = self.vna.get_tracedata(RealImag=True)
        
        # Convert amp/pha to real/imag
        calculated_real = amp * np.cos(pha)
        calculated_imag = amp * np.sin(pha)
        
        # Check consistency (within numerical precision)
        np.testing.assert_allclose(calculated_real, real, rtol=1e-10)
        np.testing.assert_allclose(calculated_imag, imag, rtol=1e-10)

    def test_tracedata_randomness(self):
        """Test that trace data has random components."""
        # Get multiple traces and check they're different
        trace1_amp, trace1_pha = self.vna.get_tracedata(RealImag=False)
        trace2_amp, trace2_pha = self.vna.get_tracedata(RealImag=False)
        
        # Traces should be different due to random components
        assert not np.array_equal(trace1_amp, trace2_amp)
        assert not np.array_equal(trace1_pha, trace2_pha)

    def test_measurement_functions(self):
        """Test measurement-related functions."""
        # These should not raise exceptions
        self.vna.pre_measurement()
        self.vna.start_measurement()
        self.vna.post_measurement()
        self.vna.avg_clear()

    def test_ready_function(self):
        """Test ready function toggles state."""
        initial_ready = self.vna._ready
        
        result1 = self.vna.ready()
        assert result1 != initial_ready
        assert self.vna._ready == result1
        
        result2 = self.vna.ready()
        assert result2 != result1
        assert self.vna._ready == result2

    def test_sweep_parameters(self):
        """Test sweep-related parameters."""
        assert self.vna.get_sweeptime_averages() == 1
        assert self.vna.get_sweeptime() == 1
        assert self.vna.get_averages() == 1
        assert self.vna.get_Average() is False

    def test_get_all_function(self):
        """Test get_all function doesn't raise exceptions."""
        # Should not raise any exceptions
        self.vna.get_all()

    def test_s21_notch_simulation(self):
        """Test that the simulated S21 data shows resonator-like behavior."""
        # Set up a specific frequency range around a typical resonance
        self.vna.set_startfreq(4.0e9)
        self.vna.set_stopfreq(5.0e9)
        self.vna.set_nop(1001)
        
        # Get trace data multiple times to check consistency of physics
        amplitudes = []
        for _ in range(5):
            amp, _ = self.vna.get_tracedata(RealImag=False)
            amplitudes.append(amp)
        
        # All traces should show a dip (minimum < 0.9 * maximum)
        for amp in amplitudes:
            assert np.min(amp) < 0.9 * np.max(amp)

    def test_frequency_consistency_after_changes(self):
        """Test frequency parameter consistency after multiple changes."""
        # Make multiple frequency changes
        self.vna.set_centerfreq(6e9)
        self.vna.set_span(3e9)
        
        # Check consistency
        expected_start = 6e9 - 3e9/2
        expected_stop = 6e9 + 3e9/2
        
        assert abs(self.vna.get_startfreq() - expected_start) < 1e-6
        assert abs(self.vna.get_stopfreq() - expected_stop) < 1e-6
        assert abs(self.vna.get_centerfreq() - 6e9) < 1e-6
        assert abs(self.vna.get_span() - 3e9) < 1e-6


class TestDummyVNAParameterValidation:
    """Test parameter validation and edge cases."""

    def setup_method(self):
        """Set up test fixture."""
        self.vna = DummyVNA("test_validation_vna")

    def teardown_method(self):
        """Clean up after each test method."""
        if hasattr(self, 'vna'):
            del self.vna

    def test_extreme_frequency_values(self):
        """Test with extreme frequency values."""
        # Test very large frequencies
        self.vna.set_startfreq(1e12)  # 1 THz
        self.vna.set_stopfreq(2e12)   # 2 THz
        
        assert self.vna.get_startfreq() == 1e12
        assert self.vna.get_stopfreq() == 2e12
        assert self.vna.get_span() == 1e12
        
        # Should still generate valid frequency points
        freqpoints = self.vna.get_freqpoints()
        assert len(freqpoints) == self.vna.nop
        assert freqpoints[0] == 1e12
        assert freqpoints[-1] == 2e12

    def test_very_small_span(self):
        """Test with very small span."""
        self.vna.set_centerfreq(5e9)
        self.vna.set_span(1e6)  # 1 MHz span
        
        assert abs(self.vna.get_span() - 1e6) < 1e-6
        
        # Should still work
        freqpoints = self.vna.get_freqpoints()
        amp, pha = self.vna.get_tracedata()
        
        assert len(freqpoints) == self.vna.nop
        assert len(amp) == self.vna.nop

    def test_single_point_measurement(self):
        """Test with single point (nop=1)."""
        self.vna.set_nop(1)
        
        freqpoints = self.vna.get_freqpoints()
        amp, pha = self.vna.get_tracedata()
        
        assert len(freqpoints) == 1
        assert len(amp) == 1
        assert len(pha) == 1
        assert freqpoints[0] == self.vna.get_startfreq()

    def test_large_nop(self):
        """Test with large number of points."""
        self.vna.set_nop(10000)
        
        freqpoints = self.vna.get_freqpoints()
        amp, pha = self.vna.get_tracedata()
        
        assert len(freqpoints) == 10000
        assert len(amp) == 10000
        assert len(pha) == 10000


@pytest.mark.integration
class TestDummyVNAIntegration:
    """Integration tests for DummyVNA with other components."""

    def test_instrument_base_interface(self):
        """Test that DummyVNA properly implements Instrument interface."""
        vna = DummyVNA("integration_test_vna")
        
        # Test that it has required Instrument methods
        assert hasattr(vna, 'get_name')
        assert hasattr(vna, 'get_tags')
        assert hasattr(vna, 'add_parameter')
        assert hasattr(vna, 'add_function')
        
        # Test parameter access through Instrument interface
        assert vna.get_power() == 0
        vna.set_power(-5)
        assert vna.get_power() == -5

    def test_multiple_instances(self):
        """Test that multiple DummyVNA instances work independently."""
        vna1 = DummyVNA("vna1")
        vna2 = DummyVNA("vna2")
        
        # Set different parameters
        vna1.set_power(-10)
        vna2.set_power(5)
        vna1.set_centerfreq(4e9)
        vna2.set_centerfreq(6e9)
        
        # Check they remain independent
        assert vna1.get_power() == -10
        assert vna2.get_power() == 5
        assert vna1.get_centerfreq() == 4e9
        assert vna2.get_centerfreq() == 6e9
        
        # Clean up
        del vna1, vna2


if __name__ == "__main__":
    pytest.main([__file__])
