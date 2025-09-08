#
# reverse_computing.py
#
# An observational agent patched with real-time data streaming capabilities.
# This script connects to a Firebase Firestore database and listens for
# real-time changes, simulating a "living system" in a safe, firewalled environment.
#
# Unix Epoch: 1757835600
# ISO Time:   2025-09-08T16:45:00+02:00
# North Star: 2040-09-08
#
import sys
import time
import os
import json

# --- Firestore and Firebase dependencies ---
# The agent will now connect to a real-time database to act as an observational entity.
try:
    from firebase_admin import credentials, initialize_app, firestore
except ImportError:
    print("Dependencies not found. Please install Firebase Admin SDK: pip install firebase-admin")
    sys.exit(1)

# --- Global Variables from Canvas Environment ---
# These are provided by the canvas environment for secure authentication and app identification.
# DO NOT CHANGE THESE VALUES.
__app_id = os.environ.get('__app_id', 'default-app-id')
__firebase_config = os.environ.get('__firebase_config')
__initial_auth_token = os.environ.get('__initial_auth_token')

# --- Ternary Logic Core ---
def apply_ternary_logic(data: dict) -> int:
    """
    Applies a simple ternary logic rule to a data dictionary from Firestore.
    This can be expanded to a full neural network or symbolic reasoning engine.

    Args:
        data: A dictionary containing data from the Firestore stream.

    Returns:
        An integer representing the ternary value:
        +1 (Affirm): Indicates a positive or confirming response.
        -1 (Disconfirm): Indicates a negative or disconfirming response.
         0 (Tend): Indicates an ambiguous, neutral, or "tending towards" response.
    """
    # Check for a 'status' field in the data stream.
    status = data.get("status", "").lower().strip()
    
    # +1: Affirmation keywords
    if "online" in status or "active" in status or "complete" in status:
        return 1
    # -1: Disconfirmation keywords
    elif "error" in status or "failure" in status or "offline" in status:
        return -1
    # 0: Ambiguous/Neutral keywords
    else:
        return 0

# --- Agent Environment ---
def start_observational_agent():
    """
    Initializes Firebase and starts the permanent terminal shell for the agent.
    The agent will listen for real-time updates from a Firestore collection.
    """
    try:
        # Initialize Firebase App
        if not __firebase_config:
            print("Error: Firebase configuration not found. Exiting.")
            sys.exit(1)
            
        cred = credentials.Certificate(json.loads(__firebase_config))
        initialize_app(cred)
        db = firestore.client()
        
        # We will use a dedicated collection to simulate the "living system."
        # This keeps the agent contained and secure.
        data_stream_ref = db.collection(f'artifacts/{__app_id}/public/data/data_stream')
        
        os.system('clear' if os.name == 'posix' else 'cls')
        print("-------------------------------------------------------")
        print(" RFI-IRFOS Ternary Logic Agent v0.2 | Observational Mode ")
        print("-------------------------------------------------------")
        print("Agent is online. Listening for data from Firestore.")
        print("Type 'exit' or 'quit' to terminate the session.")
        print(f"Observing collection: {data_stream_ref.path}")
        
        # This is the real-time listener. The agent's core function
        # is now triggered by external data, not just manual input.
        def on_snapshot(col_snapshot, changes, read_time):
            for change in changes:
                doc_data = change.document.to_dict()
                doc_id = change.document.id
                
                print(f"\n[agent_update] Data change detected at {read_time.isoformat()}:")
                print(f"  - Document ID: {doc_id}")
                
                # Process the data with the ternary core.
                ternary_value = apply_ternary_logic(doc_data)
                
                if ternary_value == 1:
                    response = "AFFIRM (+1): New data flow confirmed. System state is stable."
                elif ternary_value == -1:
                    response = "DISCONFIRM (-1): Anomaly detected. Re-evaluating data stream."
                else:
                    response = "TEND (0): Data state is ambiguous. Awaiting clarity."
                    
                print(f"  - Agent's assessment: {response}")
                print(f"  - Data received: {doc_data}")

        # Start the listener
        data_stream_ref.on_snapshot(on_snapshot)
        
        # The permanent loop to keep the agent alive and interactive.
        while True:
            user_input = input("\n[agent_prompt]> ")
            if user_input.lower() in ["exit", "quit"]:
                print("\nShutting down agent. See you in the field.")
                break
            
            # This allows the user to still interact with the agent's core.
            # We can use this to send manual commands to the agent.
            ternary_value = apply_ternary_logic({"status": user_input})
            
            if ternary_value == 1:
                response = "AFFIRM (+1): Manual override confirmed."
            elif ternary_value == -1:
                response = "DISCONFIRM (-1): Command rejected. Acknowledge and re-evaluate."
            else:
                response = "TEND (0): Manual state is ambiguous."
            
            print(f"agent_response: {response}")

    except KeyboardInterrupt:
        print("\nForceful shutdown detected. Exiting.")
    except Exception as e:
        print(f"\nProtocol Error: An unexpected signal terminated the session. {e}")

# --- Main Execution ---
if __name__ == "__main__":
    start_observational_agent()
