import subprocess
import time
import os
import httpx
import asyncio

def run_local_mesh():
    # Shared key for authentication (set before starting processes)
    os.environ.setdefault("SWARM_API_KEY", "test-swarm-secret")
    swarm_key = os.environ["SWARM_API_KEY"]
    headers = {"X-Swarm-Key": swarm_key}

    # 1. Start Tracker (Default port 12345)
    tracker_proc = subprocess.Popen(["llm_pool_venv/bin/python", "tracker.py"], env=os.environ.copy())
    print("[Test] Started Tracker Node on port 12345")
    time.sleep(3) # Wait for tracker to be ready

    # 2. Start Entry Node (Port 9000, Layers 0-10)
    env_entry = os.environ.copy()
    env_entry.update({
        "NODE_ID": "entry_node",
        "IS_ENTRY": "true",
        "LAYER_START": "0",
        "LAYER_END": "10",
        "TRACKER_URL": "http://localhost:12345"
    })
    entry_proc = subprocess.Popen(["llm_pool_venv/bin/python", "swarm_node.py", "--port", "9000"], env=env_entry)

    # 3. Start Worker Node (Port 9001, Layers 11-20)
    env_worker = os.environ.copy()
    env_worker.update({
        "NODE_ID": "worker_node",
        "IS_ENTRY": "false",
        "LAYER_START": "11",
        "LAYER_END": "20",
        "TRACKER_URL": "http://localhost:12345"
    })
    worker_proc = subprocess.Popen(["llm_pool_venv/bin/python", "swarm_node.py", "--port", "9001"], env=env_worker)

    print("[Test] Started Swarm Nodes. Waiting for registration...")
    time.sleep(5)

    try:
        print("\n--- Testing Automatic Discovery & Generation ---")
        async def test_gen():
            async with httpx.AsyncClient() as client:
                # Query tracker to see registered peers
                peers_resp = await client.get("http://localhost:12345/peers", headers=headers)
                print(f"[Test] Tracker Registered Peers: {peers_resp.json()}")

                # Trigger generation on entry node
                print("[Test] Sending generation request to entry node...")
                response = await client.post("http://localhost:9000/generate?prompt=Hello+Discovery", timeout=30.0, headers=headers)
                print(f"[Test] Swarm Response: {response.json()}")

        asyncio.run(test_gen())

    except Exception as e:
        print(f"[Test] Error during test: {e}")
    finally:
        print("\nShutting down all processes...")
        entry_proc.terminate()
        worker_proc.terminate()
        tracker_proc.terminate()

if __name__ == "__main__":
    run_local_mesh()
