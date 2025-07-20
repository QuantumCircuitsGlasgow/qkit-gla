import sys
import os
import logging

# --- Path setup to ensure qkit is found ---
# Get the absolute path of the directory where this script is located.
# This assumes test_vna_refactor.py is in your *inner* QKIT-GLA root directory
# (the one that directly contains your 'qkit' package folder).
script_dir = os.path.abspath(os.path.dirname(__file__))

# Insert this directory at the beginning of Python's search path.
sys.path.insert(0, script_dir)
# --- End of path setup ---


# Now, import qkit (which should work as per diagnostics)
import qkit 

# Configure basic logging to see driver messages
# Set level to DEBUG for more verbose output from drivers
logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

print("--- Initializing QKIT Framework ---")
# Call qkit.start() to initialize the framework, including qkit.instruments
# silent=True prevents extra print statements from qkit.start()
qkit.start(silent=True)
print("QKIT Framework initialized.")


print("\n--- Attempting to instantiate Keysight_VNA_P50xxA driver ---")

try:
    # Replace with dummy values for address/IP since you don't have hardware access
    # The Prologix driver will likely attempt to connect and time out, which is expected.
    vna = qkit.instruments.create( # Use qkit.instruments.create AFTER qkit.start()
        "test_vna_instance",
        "Keysight_VNA_P50xxA",
        gpib_address_str="GPIB::99::INSTR", # A dummy GPIB address
        ip="192.168.0.1",                # A dummy IP address
        port=1234                        # Default Prologix port
    )
    print("\n--- Driver Instantiation Attempt Complete ---")
    print(f"Successfully created VNA object: {vna.get_name()}")
    print(f"VNA type: {vna.get_type()}")

    # Try accessing a simple property to see if discovery worked
    try:
        current_averages = vna.averages
        print(f"Accessed 'averages' property. Current value (if connected): {current_averages}")
    except Exception as prop_e:
        print(f"Could not access 'averages' property (expected if not connected to hardware): {prop_e}")

except Exception as e:
    print("\n--- Driver Instantiation Attempt FAILED ---")
    logging.error(f"An error occurred during VNA driver instantiation: {e}", exc_info=True)

print("\nScript finished.")