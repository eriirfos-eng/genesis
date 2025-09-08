#
# network_agent.py
#
# An agent designed to observe and apply ternary logic to system network activity.
# This script monitors a specified directory for changes (creations, modifications, deletions)
# and applies ternary logic to each event, treating the user's local actions as the
# "living system" data stream.
#
# Unix Epoch: 1757835600
# ISO Time:   2025-09-08T17:15:00+02:00
# North Star: 2040-09-08
#
import sys
import time
import os
import psutil

# --- Dependency Installation ---
# BEFORE RUNNING, you must install the 'psutil' library.
# Open your terminal and run this command:
# pip install psutil

# --- Global Variables ---
# The agent will now observe network activity.
# You can adjust these thresholds to define a new ternary logic based on your usage.
NETWORK_SPIKE_THRESHOLD_MB = 100  # A spike of over 100 MB sent or received is a major event.
NETWORK_SILENCE_THRESHOLD_S = 10  # A period of 10 seconds with no network activity.

# --- Ternary Logic Core ---
def apply_ternary_logic(bytes_sent: float, bytes_recv: float) -> int:
    """
    Applies ternary logic to network activity.

    Args:
        bytes_sent: The number of bytes sent since the last check.
        bytes_recv: The number of bytes received since the last check.

    Returns:
        An integer representing the ternary value:
        +1 (Affirm): Indicates a significant data flow (spike).
        -1 (Disconfirm): Indicates a lack of data flow (silence).
         0 (Tend): Indicates a normal or ambiguous data flow.
    """
    total_mb = (bytes_sent + bytes_recv) / (1024 * 1024)
    if total_mb > NETWORK_SPIKE_THRESHOLD_MB:
        return 1
    elif total_mb == 0:
        return -1
    else:
        return 0

# --- Agent Environment ---
def start_network_agent():
    """
    Initializes and starts the local observational agent.
    """
    try:
        os.system('clear' if os.name == 'posix' else 'cls')
        print("-------------------------------------------------------")
        print(" RFI-IRFOS Ternary Logic Agent v0.4 | Network Observer ")
        print("-------------------------------------------------------")
        print("Agent is online. Listening for network data flow.")
        print("Type 'exit' or 'quit' to terminate the session.")

        last_bytes_sent = psutil.net_io_counters().bytes_sent
        last_bytes_recv = psutil.net_io_counters().bytes_recv
        last_activity_time = time.time()

        while True:
            # Check for user input without blocking the loop
            try:
                user_input = sys.stdin.readline().strip()
                if user_input.lower() in ["exit", "quit"]:
                    print("\nShutting down agent. See you in the field.")
                    break
            except IOError:
                pass  # No user input available

            time.sleep(1) # Check every second
            
            current_bytes_sent = psutil.net_io_counters().bytes_sent
            current_bytes_recv = psutil.net_io_counters().bytes_recv

            bytes_sent_diff = current_bytes_sent - last_bytes_sent
            bytes_recv_diff = current_bytes_recv - last_bytes_recv
            
            ternary_value = apply_ternary_logic(bytes_sent_diff, bytes_recv_diff)

            response = ""
            if ternary_value == 1:
                response = f"AFFIRM (+1): Significant data flow detected. (+{(bytes_sent_diff / (1024*1024)):.2f} MB sent, +{(bytes_recv_diff / (1024*1024)):.2f} MB received)."
            elif ternary_value == -1:
                if (time.time() - last_activity_time) > NETWORK_SILENCE_THRESHOLD_S:
                    response = "DISCONFIRM (-1): Anomaly detected. Network is quiet. Re-evaluating data stream."
                    last_activity_time = time.time()
                else:
                    response = "" # Keep silent unless silence threshold is met
            else:
                response = f"TEND (0): Normal data flow. (+{(bytes_sent_diff / (1024*1024)):.2f} MB sent, +{(bytes_recv_diff / (1024*1024)):.2f} MB received)."

            if response:
                print(f"\n[agent_update] Agent's assessment: {response}")

            last_bytes_sent = current_bytes_sent
            last_bytes_recv = current_bytes_recv

    except KeyboardInterrupt:
        print("\nForceful shutdown detected. Exiting.")
    except Exception as e:
        print(f"\nProtocol Error: An unexpected signal terminated the session. {e}")

# --- Main Execution ---
if __name__ == "__main__":
    start_network_agent()

