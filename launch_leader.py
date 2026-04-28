import os
import sys
import subprocess
import time
import httpx

def check_ngrok():
    """Check if ngrok is running and get the public URL."""
    try:
        response = httpx.get("http://localhost:4040/api/tunnels")
        tunnels = response.json().get('tunnels', [])
        for tunnel in tunnels:
            if tunnel['config']['addr'] == 'http://localhost:12345':
                return tunnel['public_url']
    except Exception:
        return None
    return None

def main():
    print("🚀 LLM Swarm: Leader Launch Sequence")
    print("-" * 40)

    # 1. Check for Model
    model_path = "Qwen_Qwen3.5-27B-Q4_K_M.gguf"
    if not os.path.exists(model_path):
        print(f"❌ Error: {model_path} not found in current directory.")
        print("Please download it first using the instructions in the README.")
        return

    # 2. Check for ngrok
    print("📡 Checking ngrok tunnel...")
    public_url = check_ngrok()
    if not public_url:
        print("⚠️  ngrok is not running for port 12345.")
        print("Please run 'ngrok http 12345' in a separate terminal and try again.")
        return
    print(f"✅ Tracker Public URL: {public_url}")

    # 3. Build/Start Leader Services
    print("🐳 Starting Docker containers (Tracker + Entry Node)...")
    try:
        # We only start the tracker and the entry node for the leader
        # We ignore the generic 'worker-node' in the compose file for the leader's own machine
        subprocess.run(["docker-compose", "up", "-d", "--build", "tracker", "entry-node"], check=True)
        print("✅ Services started successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker Error: {e}")
        return

    print("-" * 40)
    print(f"🌟 SWARM IS LIVE 🌟")
    print(f"Tracker: {public_url}")
    print(f"Entry Node: localhost:9000 (Layers 0-4)")
    print("-" * 40)
    print("To view logs, run: docker-compose logs -f")

if __name__ == "__main__":
    main()
