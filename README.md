# 🚀 LLM Swarm: Decentralized P2P Pooled Compute Mesh

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

**LLM Swarm** is a revolutionary, open-source technology designed to put the power of Large Language Models (LLMs) back into the hands of the people. By utilizing a peer-to-peer (P2P) grid/mesh—similar to BitTorrent—LLM Swarm allows users to pool their hardware resources (RAM/VRAM) to run massive models that would otherwise require expensive cloud subscriptions or industrial-grade GPUs.

## 💖 Support the Project
If you believe in the future of decentralized AI and want to support the development of LLM Swarm, donations are greatly appreciated!

**Donations (PayPal/Email):** [rtmalikian@gmail.com](mailto:rtmalikian@gmail.com)

## 🌟 Key Features

- **Swarm Intelligence:** Upon startup, nodes automatically probe the network to identify missing "slices" (layer ranges) and suggest exactly what the user should host to complete the mesh.
- **Distributed Layer Execution:** Split large models (e.g., Qwen3.5 27B) across multiple consumer devices.
- **Resource-Aware "Software Slicing":** Nodes automatically optimize RAM usage by only loading their assigned layer range into active compute buffers.
- **Model Integrity Validation:** Automatic metadata verification ensures all peers are using the correct model architecture.
- **Multi-Platform Docker Support:** Seamlessly run on M1 Mac, Linux (Ubuntu), and Windows.

## 🌍 Join the Public Swarm

The LLM Swarm is designed to be shared across the internet. If a Leader (like @rtmalikian) has shared their **Public Tracker URL**, you can join the grid in minutes.

### 1. Installation
```bash
git clone https://github.com/rtmalikian/llm-swarm.git
cd llm_swarm
python3 -m venv llm_pool_venv
source llm_pool_venv/bin/activate
pip install -r requirements.txt
```

### 2. Prepare the Model
For the most robust experience, all participants should use the same GGUF model:
- **Model:** [Qwen3.5-27B-Instruct GGUF (bartowski)](https://huggingface.co/bartowski/Qwen_Qwen3.5-27B-GGUF)
- **Quantization:** `Qwen_Qwen3.5-27B-Q4_K_M.gguf`

```bash
huggingface-cli download bartowski/Qwen_Qwen3.5-27B-GGUF --include "Qwen_Qwen3.5-27B-Q4_K_M.gguf" --local-dir ./
```

### 3. Start your Worker Node
Point your node to the Leader's Public Tracker. The node will automatically probe the network and suggest a slice if you haven't set one.

**Example (Qwen3.5-27B POC):**
```bash
export TRACKER_URL="https://remedy-unwatched-styling.ngrok-free.dev"
export NODE_ID="Volunteer_Node_$(hostname)"
export LAYER_START=5
export LAYER_END=10
export MODEL_PATH="Qwen_Qwen3.5-27B-Q4_K_M.gguf"

python swarm_node.py --port 9001
```

## 🌐 Hosting a Swarm (Port Forwarding)

### 🚀 Leader Setup (One-Click)
If you are the Swarm Leader (hosting the Tracker and initial layers), use the automation script:

1. **Start ngrok:** `ngrok http 12345`
2. **Launch:** `python3 launch_leader.py`

This script starts the Tracker and your Entry Node (hosting Layers 0-4).

### Port Forwarding Details
If you are hosting from home (e.g., behind an Orbi or Eero router), ensure your ports are reachable:

1. **Tracker Port (12345):** Use `ngrok http 12345` or forward port `12345` (TCP).
2. **Node Port (9000):** You **must** forward port `9000` (TCP) to your machine's local IP. This allows tensors to travel across the internet.
3. **Public IP:** Find your public IP at `whatismyip.com` and use it in your `PUBLIC_URL` variable.

## ⚡ Performance: The "BitTorrent" for Inference

LLM Swarm is designed to be fast by leveraging the collective power of the grid. While a single device might struggle, a mesh of devices excels:

- **Distributed Workload:** Instead of one machine computing 27B parameters, each node only handles a small "slice" (e.g., 5-10 layers).
- **Heterogeneous Hardware:** The mesh automatically utilizes the best of all worlds. Volunteers with high-end GPUs (VRAM) provide rapid execution for their slices, while others contribute stable CPU/RAM compute.
- **Unified Memory Optimization:** On platforms like Apple Silicon (M1/M2/M3), the swarm utilizes Unified Memory to accelerate inference even when models exceed traditional VRAM limits.
- **The "Mesh" Advantage:** As the swarm grows, the Tracker can route traffic through the fastest available paths, minimizing latency and maximizing throughput.

## 🧪 Proof of Concept: Collaborative Qwen3.5-27B Swarm

This is how we run **Qwen3.5-27B** (which normally requires ~18GB+ VRAM) across multiple consumer machines.

**Live POC Tracker:** `https://remedy-unwatched-styling.ngrok-free.dev`

1. **Leader Setup:** Runs the Tracker and the Entry Node (Layers 0-4).
2. **Dynamic Discovery:** Workers join and register with the tracker for subsequent layers (5-10, 11-15, etc.).
3. **Distributed Inference:** The hidden state tensor travels across the internet through each participant's node to complete the full 27B parameter forward pass.

## 🐳 Running with Docker (Recommended)

The easiest way to run LLM Swarm is using Docker.

**Note on Optimization:** The Docker setup uses **Volumes**. Large `.gguf` model files are mounted directly from your host into the container.
- **No Disk Waste:** The model isn't copied into the Docker image.
- **Instant Builds:** Rebuilding the container takes seconds, regardless of model size.
- **Persistence:** Logs and registrations stay consistent.

### 1. Build and Start the Mesh
```bash
docker-compose up --build
```
This command starts:
- A **Tracker** on port `12345`
- An **Entry Node** on port `9000` (serving layers 0-10)
- A **Worker Node** on port `9001` (serving layers 11-20)

### 2. Test the Swarm
Send a request to the dockerized entry node:
```bash
curl -X POST "http://localhost:9000/generate?prompt=Hello+Docker+Swarm"
```

## 🚀 Manual Installation

### Prerequisites
- Python 3.10+
- `pip`

1. **Setup:**
   ```bash
   python3 -m venv llm_pool_venv
   source llm_pool_venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Start the Tracker:**
   ```bash
   python tracker.py
   ```

3. **Start Worker/Entry Nodes:**
   See the `test_mesh.py` or the `docker-compose.yml` for environment variable configurations.

## 🤖 Agent Integration (OpenAI Compatible)

LLM Swarm is designed to be a drop-in replacement for OpenAI-compatible APIs. This allows you to use the power of the swarm with agentic frameworks and tools that support OpenAI endpoints, such as **Hermes Agent**, **OpenClaw**, **Continue**, **LibreChat**, **AutoGPT**, or **LangChain**.

### Connecting your Agent
Point your agent to your Entry Node's API endpoint:

- **Base URL:** `http://localhost:9000/v1` (or your public ngrok URL)
- **API Key:** `swarm-mesh` (any string works)
- **Model:** `swarm-mesh-v1`

### Example Request
```bash
curl http://localhost:9000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "swarm-mesh-v1",
    "messages": [{"role": "user", "content": "Hello Swarm!"}]
  }'
```

The Entry Node will receive the request, orchestrate the inference across the global mesh, and return a standard OpenAI-formatted response.

## 🔐 Swarm API Key (Node Authentication)

LLM Swarm supports a shared-secret API key to prevent unauthorized nodes from joining your mesh or sending unauthenticated requests.

**How it works:**
- All nodes and the Tracker check for an `X-Swarm-Key` HTTP header on every request.
- If `SWARM_API_KEY` is set, requests without a matching key are rejected with `401 Unauthorized`.
- If `SWARM_API_KEY` is empty or unset, the swarm operates without authentication (backward-compatible).

**Usage:**

```bash
# Set the same key on every node and the tracker
export SWARM_API_KEY="your-secret-swarm-key"

# Start tracker and nodes as usual — they will automatically include the key in all requests
python tracker.py
python swarm_node.py --port 9000
```

**Docker:**

```bash
# Pass via environment variable (all services read it automatically)
SWARM_API_KEY="your-secret-key" docker-compose up --build
```

**Testing unauthorized access:**

```bash
# Without key — should return 401
curl http://localhost:12345/peers
# → {"detail":"Invalid or missing X-Swarm-Key header."}

# With key — should return peer list
curl -H "X-Swarm-Key: your-secret-swarm-key" http://localhost:12345/peers
```

---

## 🗺️ Roadmap & TODO

LLM Swarm is an experimental prototype. We are looking for contributors to help with the following:

- [ ] **Security Hardening:** Implement Swarm-wide API Keys for node-to-node authentication. ✅ *Implemented in v0.2.0*
- [ ] **Encrypted Communication:** Move from raw HTTP to `libp2p` with Noise/TLS encryption.
- [ ] **Tensor Validation:** Implement checksums and basic verification to prevent malicious nodes from poisoning the inference.
- [ ] **Compression:** Implement tensor quantization/compression for faster transmission over slow internet connections.
- [ ] **Dynamic Slicing:** Automated model slicing based on a volunteer's available VRAM.
- [ ] **GUI:** A simple dashboard to see the real-time status of the swarm.
- [ ] **Geographic Routing:** Make the Tracker return the peer with the lowest latency (closest to you geographically) to minimize "hop" times.

## ❓ FAQ

**Q: What happens if multiple people host the same layers?**
A: The system automatically load-balances. The Tracker identifies all peers hosting a specific layer range and routes traffic accordingly. This provides **redundancy** (if one node drops, another takes over) and **scalability** (handling more requests simultaneously).

**Q: Is my prompt data private?**
A: In this prototype, data travels across nodes in the clear (HTTP). Do not use sensitive information. Future versions (v0.2.0) will implement `libp2p` with Noise/TLS encryption for end-to-end security.

**Q: Does this use my GPU or CPU?**
A: LLM Swarm uses `llama.cpp` under the hood. It will automatically use your GPU (Metal on Mac, CUDA on NVIDIA, ROCm on AMD) if available, falling back to CPU if not.

**Q: How much bandwidth does this use?**
A: Each "hop" between nodes involves sending a hidden state tensor. For Qwen3.5-27B, this is roughly a few megabytes per request. It is recommended to have a stable broadband connection.

**Q: What if a node goes offline mid-generation?**
A: Currently, the request will fail, but the Tracker will remove the stale node within 60 seconds. The next request will automatically be routed to a remaining healthy node hosting those layers.

## 👤 Author
**Raphael Malikian**  
*Based in Palmdale, California*  
A visionary developer focused on decentralizing AI and making advanced technology accessible to everyone.

**X (Twitter):** [@rtmalikian](https://x.com/rtmalikian)

## 💖 Support the Project
If you believe in the future of decentralized AI and want to support the development of LLM Swarm, donations are greatly appreciated!

**Donations (PayPal/Email):** [rtmalikian@gmail.com](mailto:rtmalikian@gmail.com)

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
