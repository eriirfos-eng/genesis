import sys
import time
import os
import json
import random
import asyncio
import psutil
import websockets

# --- Global Agent State ---
last_payload = {
    'error': 'Agent starting up...',
    'sent_mb': 0.0,
    'recv_mb': 0.0,
    'cpu_percent': 0.0,
    'memory_percent': 0.0,
    'process_count': 0,
    'pipeline_interval': 0
}
last_update_time = 0
PIPELINE_UPDATE_INTERVAL = 5  # seconds

# To track the network data between updates
last_sent_bytes = 0
last_recv_bytes = 0

# --- WebSocket Client Management ---
connected_clients = set()

# --- Ternary Logic Core ---
def apply_ternary_logic_to_system(sent_mbps: float, recv_mbps: float, num_connections: int, listening_ports_present: bool, cpu_percent: float, memory_percent: float, process_count: int) -> int:
    """
    Applies a more complex ternary logic based on multiple real-time system metrics.

    Args:
        sent_mbps: Outgoing data in megabytes per second.
        recv_mbps: Incoming data in megabytes per second.
        num_connections: The total number of active network connections.
        listening_ports_present: A boolean indicating if any ports are in a 'LISTEN' state.
        cpu_percent: The current CPU usage percentage.
        memory_percent: The current memory usage percentage.
        process_count: The number of active processes.

    Returns:
        +1 (Affirm), 0 (Tend), or -1 (Disconfirm)
    """
    total_mbps = sent_mbps + recv_mbps

    # Condition for Affirm: High throughput and a significant number of connections,
    # and low to moderate system resource usage.
    if total_mbps > 5.0 and num_connections > 10 and cpu_percent < 80 and memory_percent < 85:
        return 1
    
    # Condition for Disconfirm: A sudden data spike with few connections,
    # or the presence of listening ports (which could indicate a new service),
    # or high resource usage.
    elif (total_mbps > 5.0 and num_connections <= 10) or listening_ports_present or cpu_percent > 80 or memory_percent > 85:
        return -1
    
    # Condition for Tend: All other cases, indicating a stable, moderate state.
    else:
        return 0

def adjust_pipeline_interval(ternary_value: int) -> int:
    """
    Adjusts the observation interval based on the agent's ternary assessment.

    Args:
        ternary_value: The current ternary state of the system (+1, 0, -1).

    Returns:
        The new observation interval in seconds.
    """
    if ternary_value == 1:
        # System is healthy, slow down to conserve resources
        return 8
    elif ternary_value == -1:
        # Anomaly detected, speed up for granular observation
        return 2
    else:
        # Moderate state, maintain default interval
        return 5

# --- Agent Server Logic ---
async def update_payload_and_broadcast():
    global last_payload, last_update_time, last_sent_bytes, last_recv_bytes, PIPELINE_UPDATE_INTERVAL
    while True:
        try:
            print(f"Observing new system state at a {PIPELINE_UPDATE_INTERVAL}s interval...")
            
            # Get the current network I/O counters
            net_io = psutil.net_io_counters()
            current_sent_bytes = net_io.bytes_sent
            current_recv_bytes = net_io.bytes_recv
            
            # Get the current network connections and check for listening ports
            connections = psutil.net_connections(kind='inet')
            num_connections = len(connections)
            listening_ports = any(conn.status == 'LISTEN' for conn in connections)
            
            # Get CPU and memory usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            process_count = len(psutil.pids())

            # Calculate the difference and convert to MB/s
            time_delta = time.time() - last_update_time
            if time_delta > 0:
                sent_mbps = (current_sent_bytes - last_sent_bytes) / time_delta / (1024 * 1024)
                recv_mbps = (current_recv_bytes - last_recv_bytes) / time_delta / (1024 * 1024)
            else:
                sent_mbps = 0
                recv_mbps = 0
            
            # Store the current counters for the next loop
            last_sent_bytes = current_sent_bytes
            last_recv_bytes = current_recv_bytes
            last_update_time = time.time()

            # Apply ternary logic to the real data
            ternary_value = apply_ternary_logic_to_system(sent_mbps, recv_mbps, num_connections, listening_ports, cpu_percent, memory_percent, process_count)
            
            # Adjust the pipeline interval based on the ternary value
            PIPELINE_UPDATE_INTERVAL = adjust_pipeline_interval(ternary_value)
            
            # Create the new JSON payload based on the state
            if ternary_value == 1:
                commit_message = f"feat: Healthy system state ({sent_mbps:.2f} Mbps sent, {recv_mbps:.2f} Mbps received, {cpu_percent}% CPU, {memory_percent}% Mem)"
            elif ternary_value == 0:
                commit_message = f"refactor: Moderate system state ({sent_mbps:.2f} Mbps sent, {recv_mbps:.2f} Mbps received, {cpu_percent}% CPU, {memory_percent}% Mem)"
            else:
                commit_message = f"fixup: Anomaly detected ({sent_mbps:.2f} Mbps sent, {recv_mbps:.2f} Mbps received, {cpu_percent}% CPU, {memory_percent}% Mem)"
            
            new_payload = {
                'commit_message': commit_message,
                'ternary_value': ternary_value,
                'sent_mb': sent_mbps,
                'recv_mb': recv_mbps,
                'num_connections': num_connections,
                'listening_ports_present': listening_ports,
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'process_count': process_count,
                'pipeline_interval': PIPELINE_UPDATE_INTERVAL
            }
            
            last_payload = new_payload
            
            # Broadcast the updated payload to all connected clients
            if connected_clients:
                message = json.dumps(last_payload)
                await asyncio.gather(*[client.send(message) for client in connected_clients])

        except Exception as e:
            print(f"Error in data observation loop: {e}")
        
        await asyncio.sleep(PIPELINE_UPDATE_INTERVAL)

async def handler(websocket):
    connected_clients.add(websocket)
    try:
        # Send initial payload
        await websocket.send(json.dumps(last_payload))
        # Keep connection open until client closes it
        await websocket.wait_closed()
    finally:
        connected_clients.remove(websocket)

async def main():
    # Initial read to establish a baseline
    global last_sent_bytes, last_recv_bytes, last_update_time
    net_io = psutil.net_io_counters()
    last_sent_bytes = net_io.bytes_sent
    last_recv_bytes = net_io.bytes_recv
    last_update_time = time.time()
    
    print("-------------------------------------------------------")
    print(" RFI-IRFOS Ternary Logic Agent v0.9 | System Sentinel ")
    print("-------------------------------------------------------")
    print("Agent is online. Awaiting WebSocket connections.")
    
    server = websockets.serve(handler, "localhost", 8000)
    
    # Run the server and the data update loop concurrently
    await asyncio.gather(server, update_payload_and_broadcast())

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nForceful shutdown detected. Exiting.")

