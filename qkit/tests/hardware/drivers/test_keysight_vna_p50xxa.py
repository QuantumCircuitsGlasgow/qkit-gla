"""
Test suite for Keysight_VNA_P50xxA driver.

This module contains comprehensive tests for the Keysight_VNA_P50xxA class,
including mocked hardware communication tests.
"""

from unittest.mock import MagicMock, Mock, call, patch

import numpy as np
import pytest

from qkit.core.instrument_base import Instrument


class TestKeysightVNAP50xxA:
    """Test class for Keysight_VNA_P50xxA driver."""

    def setup_method(self):
        """Set up test fixture with mocked visa communication."""
        # Mock the visa module and instrument
        self.mock_visa_instrument = Mock()
        self.mock_visa_instrument.write = Mock()
        self.mock_visa_instrument.query = Mock()
        self.mock_visa_instrument.query_binary_values = Mock()
        
        # Mock the visa.instrument function
        with patch('qkit.drivers.Keysight_VNA_P50xxA.visa') as mock_visa:
            mock_visa.instrument.return_value = self.mock_visa_instrument
            mock_visa.qkit_visa_version = 2  # Use newer visa version
            mock_visa.single = 'f'
            mock_visa.double = 'd'
            mock_visa.dtypes = {'f': np.float32, 'd': np.float64}
            
            # Import here to ensure mocking is active
            from qkit.drivers.Keysight_VNA_P50xxA import Keysight_VNA_P50xxA

            # Mock the get_all method calls during initialization
            self.mock_visa_instrument.query.side_effect = [
                "1",      # get_averages
                "1001",   # get_nop  
                "-10",    # get_power
                "4e9",    # get_startfreq
                "5e9",    # get_stopfreq
                "4.5e9",  # get_centerfreq
                "0.1",    # get_sweeptime
                "CONT",   # get_sweepmode
                "1"       # get_rf_output
            ]
            
            self.vna = Keysight_VNA_P50xxA("test_keysight_vna", "TCPIP::192.168.1.1::INSTR")
            
            # Reset the mock after initialization
            self.mock_visa_instrument.reset_mock()

    def teardown_method(self):
        """Clean up after each test method."""
        if hasattr(self, 'vna'):
            del self.vna

    def test_initialization(self):
        """Test that Keysight VNA initializes correctly."""
        assert self.vna.get_name() == "test_keysight_vna"
        assert "physical" in self.vna.get_tags()
        assert isinstance(self.vna, Instrument)
        assert self.vna._address == "TCPIP::192.168.1.1::INSTR"
        assert self.vna._ci == 1
        assert not self.vna.cw_mode
        assert self.vna._edel == 0

    def test_initialization_with_custom_parameters(self):
        """Test initialization with custom channel_id and cw_mode."""
        with patch('qkit.drivers.Keysight_VNA_P50xxA.visa') as mock_visa:
            mock_visa.instrument.return_value = self.mock_visa_instrument
            mock_visa.qkit_visa_version = 2
            
            # Mock get_all calls
            self.mock_visa_instrument.query.side_effect = [
                "1", "1001", "-10", "4e9", "5e9", "4.5e9", "0.1", "CONT", "1"
            ]
            
            from qkit.drivers.Keysight_VNA_P50xxA import Keysight_VNA_P50xxA
            vna = Keysight_VNA_P50xxA("test_vna", "TCPIP::192.168.1.1::INSTR", 
                                     channel_id=2, cw_mode=True)
            
            assert vna._ci == 2
            assert vna.cw_mode is True

    def test_reset(self):
        """Test reset functionality."""
        self.vna.reset()
        self.mock_visa_instrument.write.assert_called_with("*RST")

    def test_ready_with_single_average(self):
        """Test ready function with single average."""
        # Mock the necessary method calls
        self.mock_visa_instrument.query.side_effect = ["1", "HOLD\n"]  # get_averages, get_sweepmode
        
        result = self.vna.ready()
        assert result is True
        
        # Test with non-HOLD mode
        self.mock_visa_instrument.query.side_effect = ["1", "CONT\n"]
        result = self.vna.ready()
        assert result is False

    def test_ready_with_multiple_averages(self):
        """Test ready function with multiple averages."""
        self.mock_visa_instrument.query.side_effect = ["5", "2"]  # get_averages, status query
        
        result = self.vna.ready()
        assert result is True  # 2 & 0b10 = True
        
        self.mock_visa_instrument.query.side_effect = ["5", "1"]  # status = 1
        result = self.vna.ready()
        assert result is False  # 1 & 0b10 = False

    def test_hold_function(self):
        """Test hold function."""
        # Test setting hold mode
        self.vna.hold(True)
        self.mock_visa_instrument.write.assert_called_with("SENS1:SWE:MODE HOLD")
        
        # Test setting continuous mode
        self.vna.hold(False)
        self.mock_visa_instrument.write.assert_called_with("SENS1:SWE:MODE CONT")

    def test_avg_clear(self):
        """Test average clear function."""
        self.vna.avg_clear()
        self.mock_visa_instrument.write.assert_called_with("SENS1:AVER:CLE")

    def test_data_format(self):
        """Test data format setting."""
        self.vna.data_format("ASC")
        self.mock_visa_instrument.write.assert_called_with("FORM ASC")
        
        self.vna.data_format("REAL32")
        self.mock_visa_instrument.write.assert_called_with("FORM REAL,32")
        
        self.vna.data_format("REAL64")
        self.mock_visa_instrument.write.assert_called_with("FORM REAL,64")
        
        # Test invalid format
        with pytest.raises(ValueError, match="Incorrect data format"):
            self.vna.data_format("INVALID")

    def test_set_sweeptime_auto(self):
        """Test automatic sweep time setting."""
        self.vna.set_sweeptime_auto()
        self.mock_visa_instrument.write.assert_called_with("SENS1:SWE:TIME:AUTO ON")

    def test_get_tracedata_amplitude_phase(self):
        """Test trace data retrieval in amplitude/phase format."""
        # Mock binary data return (interleaved real/imag)
        mock_data = [1.0, 0.5, 0.8, 0.3, 0.9, 0.1]  # 3 complex points
        self.mock_visa_instrument.query_binary_values.return_value = np.array(mock_data)
        
        amp, pha = self.vna.get_tracedata(format="AmpPha")
        
        # Verify the write calls for format setting
        expected_calls = [
            call("FORM REAL,32"),
            call("FORM:BORD SWAPPED")
        ]
        self.mock_visa_instrument.write.assert_has_calls(expected_calls)
        
        # Verify the query call
        self.mock_visa_instrument.query_binary_values.assert_called_with(
            "CALC1:MEAS:DATA:SDATA?", datatype=np.float32, container=np.array
        )
        
        # Check output format
        assert len(amp) == 3
        assert len(pha) == 3
        assert isinstance(amp, np.ndarray)
        assert isinstance(pha, np.ndarray)

    def test_get_tracedata_real_imag(self):
        """Test trace data retrieval in real/imaginary format."""
        mock_data = [1.0, 0.5, 0.8, 0.3, 0.9, 0.1]
        self.mock_visa_instrument.query_binary_values.return_value = np.array(mock_data)
        
        real, imag = self.vna.get_tracedata(format="RealImag")
        
        # Check output format
        assert len(real) == 3
        assert len(imag) == 3
        np.testing.assert_array_equal(real, [1.0, 0.8, 0.9])
        np.testing.assert_array_equal(imag, [0.5, 0.3, 0.1])

    def test_get_tracedata_cw_mode(self):
        """Test trace data retrieval in CW mode."""
        # Set CW mode
        self.vna.cw_mode = True
        
        mock_data = [1.0, 0.5, 0.8, 0.3, 0.9, 0.1]
        self.mock_visa_instrument.query_binary_values.return_value = np.array(mock_data)
        
        amp, pha = self.vna.get_tracedata(format="AmpPha")
        
        # In CW mode, should return single averaged value
        assert len(amp) == 1
        assert len(pha) == 1

    def test_get_tracedata_invalid_format(self):
        """Test trace data with invalid format."""
        mock_data = [1.0, 0.5]
        self.mock_visa_instrument.query_binary_values.return_value = np.array(mock_data)
        
        with pytest.raises(ValueError, match="Format must be AmpPha or RealImag"):
            self.vna.get_tracedata(format="Invalid")

    def test_get_freqpoints_linear_mode(self):
        """Test frequency points retrieval in linear sweep mode."""
        self.vna.cw_mode = False
        mock_freqs = np.array([4e9, 4.1e9, 4.2e9, 4.3e9, 4.4e9])
        self.mock_visa_instrument.query_binary_values.return_value = mock_freqs
        
        freqs = self.vna.get_freqpoints()
        
        # Verify format setting calls
        expected_calls = [
            call("FORM REAL,64"),
            call("FORM:BORD SWAPPED")
        ]
        self.mock_visa_instrument.write.assert_has_calls(expected_calls)
        
        # Verify query call
        self.mock_visa_instrument.query_binary_values.assert_called_with(
            "CALC1:MEAS:DATA:X?", datatype=np.float64, container=np.array
        )
        
        np.testing.assert_array_equal(freqs, mock_freqs)

    def test_get_freqpoints_cw_mode(self):
        """Test frequency points retrieval in CW mode."""
        self.vna.cw_mode = True
        self.mock_visa_instrument.query.return_value = "4.5e9"
        
        freq = self.vna.get_freqpoints()
        
        self.mock_visa_instrument.query.assert_called_with("SENS1:FREQ:CW?")
        assert freq == "4.5e9"

    def test_parameter_getters_setters(self):
        """Test various parameter getters and setters."""
        # Test averages
        self.mock_visa_instrument.query.return_value = "10"
        result = self.vna.do_get_averages()
        self.mock_visa_instrument.query.assert_called_with("SENS1:AVER:COUN?")
        
        self.vna.do_set_averages(5)
        self.mock_visa_instrument.write.assert_called_with("SENS1:AVER:COUN 5")
        
        # Test bandwidth
        self.mock_visa_instrument.query.return_value = "1000"
        result = self.vna.do_get_bandwidth()
        self.mock_visa_instrument.query.assert_called_with("SENS1:BWID?")
        
        self.vna.do_set_bandwidth(500)
        self.mock_visa_instrument.write.assert_called_with("SENS1:BWID 500")
        
        # Test center frequency
        self.mock_visa_instrument.query.return_value = "4.5e9"
        result = self.vna.do_get_centerfreq()
        self.mock_visa_instrument.query.assert_called_with("SENS1:FREQ:CENT?")
        
        self.vna.do_set_centerfreq(5e9)
        self.mock_visa_instrument.write.assert_called_with("SENS1:FREQ:CENT 5000000000.0")

    def test_cw_mode_operations(self):
        """Test CW mode specific operations."""
        # Test getting CW mode
        assert self.vna.do_get_cw() == self.vna.cw_mode
        
        # Test setting CW mode
        self.vna.do_set_cw(True)
        self.mock_visa_instrument.write.assert_called_with("SENS1:SWEEP:TYPE CW")
        assert self.vna.cw_mode is True
        
        self.vna.do_set_cw(False)
        self.mock_visa_instrument.write.assert_called_with("SENS1:SWEEP:TYPE LIN")
        assert self.vna.cw_mode is False
        
        # Test CW frequency setting when in CW mode
        self.vna.cw_mode = True
        self.mock_visa_instrument.query.return_value = "4.5e9"
        result = self.vna.do_get_cwfreq()
        self.mock_visa_instrument.query.assert_called_with("SENS1:FREQ:CW?")
        
        self.vna.do_set_cwfreq(5e9)
        self.mock_visa_instrument.write.assert_called_with("SENS1:FREQ:CW 5000000000.0")
        
        # Test error when setting CW freq while not in CW mode
        self.vna.cw_mode = False
        with pytest.raises(ValueError, match="VNA not in CW mode"):
            self.vna.do_set_cwfreq(5e9)

    def test_edel_operations(self):
        """Test electrical delay operations."""
        # Test get_edel with no active measurement
        self.mock_visa_instrument.query.side_effect = [
            '""',  # PAR:SEL query returns empty
            '"CH1_S11_1,S11"',  # PAR:CAT query
            "1e-9"  # EDEL query
        ]
        
        result = self.vna.do_get_edel()
        
        expected_calls = [
            call("CALC1:PAR:SEL?"),
            call("CALC1:PAR:CAT?"),
            call("CALC1:CORR:EDEL:TIME?")
        ]
        self.mock_visa_instrument.query.assert_has_calls(expected_calls)
        
        expected_write = call("CALC1:PAR:SEL CH1_S11_1")
        self.mock_visa_instrument.write.assert_has_calls([expected_write])
        
        # Test set_edel
        self.mock_visa_instrument.query.side_effect = [
            '""',
            '"CH1_S11_1,S11"'
        ]
        
        self.vna.do_set_edel(2e-9)
        
        expected_write_calls = [
            call("CALC1:PAR:SEL CH1_S11_1"),
            call("CALC1:CORR:EDEL:TIME 2e-09")
        ]
        self.mock_visa_instrument.write.assert_has_calls(expected_write_calls)

    def test_power_operations(self):
        """Test power-related operations."""
        # Test get power
        self.mock_visa_instrument.query.return_value = "-10"
        result = self.vna.do_get_power()
        self.mock_visa_instrument.query.assert_called_with("SOUR1:POW1?")
        
        result = self.vna.do_get_power(port=2)
        self.mock_visa_instrument.query.assert_called_with("SOUR1:POW2?")
        
        # Test set power
        self.vna.do_set_power(-5)
        self.mock_visa_instrument.write.assert_called_with("SOUR1:POW1 -5")
        
        self.vna.do_set_power(-3, port=2)
        self.mock_visa_instrument.write.assert_called_with("SOUR1:POW2 -3")

    def test_rf_output_operations(self):
        """Test RF output operations."""
        self.mock_visa_instrument.query.return_value = "1"
        result = self.vna.do_get_rf_output()
        self.mock_visa_instrument.query.assert_called_with("OUTP?")
        
        self.vna.do_set_rf_output(True)
        self.mock_visa_instrument.write.assert_called_with("OUTP True")
        
        self.vna.do_set_rf_output(False)
        self.mock_visa_instrument.write.assert_called_with("OUTP False")

    def test_sweep_operations(self):
        """Test sweep-related operations."""
        # Test sweepmode
        self.mock_visa_instrument.query.return_value = "CONT"
        result = self.vna.do_get_sweepmode()
        self.mock_visa_instrument.query.assert_called_with("SENS1:SWE:MODE?")
        
        self.vna.do_set_sweepmode("HOLD")
        self.mock_visa_instrument.write.assert_called_with("SENS1:SWE:MODE HOLD")
        
        # Test invalid sweep mode
        with pytest.raises(ValueError, match="Sweep mode unknown"):
            self.vna.do_set_sweepmode("INVALID")
        
        # Test sweeptime
        self.mock_visa_instrument.query.return_value = "0.1"
        result = self.vna.do_get_sweeptime()
        self.mock_visa_instrument.query.assert_called_with("SENS1:SWE:TIME?")

    def test_measurement_workflow(self):
        """Test the complete measurement workflow."""
        # Mock necessary return values
        self.mock_visa_instrument.query.side_effect = [
            "1",      # get_averages for start_measurement
            "HOLD",   # get_sweepmode for start_measurement
        ]
        
        # Test pre_measurement
        self.vna.pre_measurement()
        expected_calls = [
            call("TRIG:SOUR MAN"),
            call("SENS1:SWE:MODE CONT"),
            call("SENS1:AVER ON")
        ]
        self.mock_visa_instrument.write.assert_has_calls(expected_calls)
        
        # Reset mock for next test
        self.mock_visa_instrument.reset_mock()
        self.mock_visa_instrument.query.side_effect = ["1"]
        
        # Test start_measurement with single average
        self.vna.start_measurement()
        expected_calls = [
            call("SENS1:SWE:MODE HOLD"),
            call("INIT:IMM")
        ]
        self.mock_visa_instrument.write.assert_has_calls(expected_calls)
        
        # Test post_measurement
        self.vna.post_measurement()
        expected_calls = [
            call("TRIG:SOUR IMM"),
            call("SENS1:AVER OFF"),
            call("SENS1:SWE:MODE CONT")
        ]
        self.mock_visa_instrument.write.assert_has_calls(expected_calls)

    def test_start_measurement_multiple_averages(self):
        """Test start_measurement with multiple averages."""
        # Mock for multiple averages
        self.mock_visa_instrument.query.side_effect = [
            "5",    # get_averages
            "1", "1", "1", "1", "1"  # TRIG:STAT:READ responses
        ]
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            self.vna.start_measurement()
        
        # Should call avg_clear and INIT:IMM for each average
        expected_write_calls = [
            call("SENS1:AVER:CLE"),
            call("INIT:IMM"),
            call("INIT:IMM"),
            call("INIT:IMM"),
            call("INIT:IMM"),
            call("INIT:IMM")
        ]
        self.mock_visa_instrument.write.assert_has_calls(expected_write_calls)

    def test_visa_version_1_compatibility(self):
        """Test compatibility with visa version 1."""
        with patch('qkit.drivers.Keysight_VNA_P50xxA.visa') as mock_visa:
            mock_visa.qkit_visa_version = 1
            mock_visa.instrument.return_value = self.mock_visa_instrument
            
            # Add ask_for_values method for visa v1
            self.mock_visa_instrument.ask = Mock(return_value="test")
            self.mock_visa_instrument.ask_for_values = Mock(return_value=[1, 2, 3])
            
            # Mock get_all calls
            self.mock_visa_instrument.ask.side_effect = [
                "1", "1001", "-10", "4e9", "5e9", "4.5e9", "0.1", "CONT", "1"
            ]
            
            from qkit.drivers.Keysight_VNA_P50xxA import Keysight_VNA_P50xxA
            vna_v1 = Keysight_VNA_P50xxA("test_v1", "TCPIP::192.168.1.1::INSTR")
            
            # Test ask method
            result = vna_v1.ask("TEST?")
            assert result == "test"


class TestKeysightVNAParameterValidation:
    """Test parameter validation and edge cases."""

    def setup_method(self):
        """Set up test fixture with mocked visa."""
        self.mock_visa_instrument = Mock()
        
        with patch('qkit.drivers.Keysight_VNA_P50xxA.visa') as mock_visa:
            mock_visa.instrument.return_value = self.mock_visa_instrument
            mock_visa.qkit_visa_version = 2
            mock_visa.single = 'f'
            mock_visa.double = 'd'
            mock_visa.dtypes = {'f': np.float32, 'd': np.float64}
            
            # Mock get_all method calls
            self.mock_visa_instrument.query.side_effect = [
                "1", "1001", "-10", "4e9", "5e9", "4.5e9", "0.1", "CONT", "1"
            ]
            
            from qkit.drivers.Keysight_VNA_P50xxA import Keysight_VNA_P50xxA
            self.vna = Keysight_VNA_P50xxA("test_validation", "TCPIP::192.168.1.1::INSTR")
            
            self.mock_visa_instrument.reset_mock()

    def test_valid_sweep_modes(self):
        """Test all valid sweep modes."""
        valid_modes = ["CONT", "HOLD", "SING", "GRO"]
        
        for mode in valid_modes:
            self.vna.do_set_sweepmode(mode)
            self.mock_visa_instrument.write.assert_called_with(f"SENS1:SWE:MODE {mode}")

    def test_data_format_validation(self):
        """Test data format validation."""
        valid_formats = ["ASC", "REAL32", "REAL64"]
        
        for fmt in valid_formats:
            self.vna.data_format(fmt)  # Should not raise exception
        
        with pytest.raises(ValueError):
            self.vna.data_format("INVALID_FORMAT")

    def test_channel_id_usage(self):
        """Test that channel ID is used correctly in commands."""
        # Create VNA with different channel ID
        with patch('qkit.drivers.Keysight_VNA_P50xxA.visa') as mock_visa:
            mock_visa.instrument.return_value = self.mock_visa_instrument
            mock_visa.qkit_visa_version = 2
            
            self.mock_visa_instrument.query.side_effect = [
                "1", "1001", "-10", "4e9", "5e9", "4.5e9", "0.1", "CONT", "1"
            ]
            
            from qkit.drivers.Keysight_VNA_P50xxA import Keysight_VNA_P50xxA
            vna_ch2 = Keysight_VNA_P50xxA("test_ch2", "TCPIP::192.168.1.1::INSTR", channel_id=2)
            
            self.mock_visa_instrument.reset_mock()
            
            # Test that channel 2 is used in commands
            vna_ch2.avg_clear()
            self.mock_visa_instrument.write.assert_called_with("SENS2:AVER:CLE")
            
            vna_ch2.do_set_averages(10)
            self.mock_visa_instrument.write.assert_called_with("SENS2:AVER:COUN 10")


@pytest.mark.integration
class TestKeysightVNAIntegration:
    """Integration tests for Keysight VNA."""

    def test_instrument_interface_compliance(self):
        """Test that Keysight VNA implements Instrument interface correctly."""
        with patch('qkit.drivers.Keysight_VNA_P50xxA.visa') as mock_visa:
            mock_visa.instrument.return_value = Mock()
            mock_visa.qkit_visa_version = 2
            
            # Mock get_all calls
            mock_visa.instrument.return_value.query.side_effect = [
                "1", "1001", "-10", "4e9", "5e9", "4.5e9", "0.1", "CONT", "1"
            ]
            
            from qkit.drivers.Keysight_VNA_P50xxA import Keysight_VNA_P50xxA
            vna = Keysight_VNA_P50xxA("integration_test", "TCPIP::192.168.1.1::INSTR")
            
            # Test Instrument interface
            assert hasattr(vna, 'get_name')
            assert hasattr(vna, 'get_tags')
            assert "physical" in vna.get_tags()
            assert vna.get_name() == "integration_test"

    def test_error_handling(self):
        """Test error handling in various scenarios."""
        with patch('qkit.drivers.Keysight_VNA_P50xxA.visa') as mock_visa:
            mock_visa_instrument = Mock()
            mock_visa.instrument.return_value = mock_visa_instrument
            mock_visa.qkit_visa_version = 2
            mock_visa.single = 'f'
            mock_visa.dtypes = {'f': np.float32}
            
            # Mock get_all calls
            mock_visa_instrument.query.side_effect = [
                "1", "1001", "-10", "4e9", "5e9", "4.5e9", "0.1", "CONT", "1"
            ]
            
            from qkit.drivers.Keysight_VNA_P50xxA import Keysight_VNA_P50xxA
            vna = Keysight_VNA_P50xxA("error_test", "TCPIP::192.168.1.1::INSTR")
            
            # Test that exceptions are properly raised for invalid parameters
            with pytest.raises(ValueError):
                vna.data_format("INVALID")
            
            with pytest.raises(ValueError):
                vna.do_set_sweepmode("INVALID")


if __name__ == "__main__":
    pytest.main([__file__])
