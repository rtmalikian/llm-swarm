# 🚀 LLM Swarm: Decentralized P2P Pooled Compute Mesh

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

**LLM Swarm** is a revolutionary, open-source technology designed to put the power of Large Language Models (LLMs) back into the hands of the people. By utilizing a peer-to-peer (P2P) grid/mesh—similar to BitTorrent—LLM Swarm allows users to pool their hardware resources (RAM/VRAM) to run massive models that would otherwise require expensive cloud subscriptions or industrial-grade GPUs.

## 💖 Support the Project
If you believe in the future of decentralized AI and want to support the development of LLM Swarm, donations are greatly appreciated!

**Donations (PayPal/Email):** [rtmalikian@gmail.com](mailto:rtmalikian@gmail.com)

## 🌟 Key Features

- **Distributed Layer Execution:** Split large models (e.g., Qwen3.5 27B) across multiple consumer devices.
- **P2P Pipeline Parallelism:** Tensors are passed seamlessly through a mesh of nodes for collaborative inference.
- **Dynamic Peer Discovery:** Automatic node registration via a centralized Tracker Node.
- **Multi-Platform Docker Support:** Seamlessly run on M1 Mac, Linux (Ubuntu), and Windows.
- **Hardware Agnostic:** Run LLMs on local hardware regardless of single-device limitations.

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
Point your node to the Leader's Public Tracker.

**Example (Qwen3.5-27B POC):**
```bash
export TRACKER_URL="https://remedy-unwatched-styling.ngrok-free.dev"
export NODE_ID="Volunteer_Node_$(hostname)"
export LAYER_START=11
export LAYER_END=20
export MODEL_PATH="Qwen_Qwen3.5-27B-Q4_K_M.gguf"

# Optional: If you want to be reachable by others, set your public IP/URL
# export PUBLIC_URL="http://[YOUR_PUBLIC_IP]:9001" 

python swarm_node.py --port 9001
```

## 🌐 Hosting a Swarm (Port Forwarding)

If you are hosting a Tracker or an Entry Node from home (e.g., behind an Orbi or Eero router), you must ensure your ports are reachable:

1. **Tracker Port (12345):** Use a tunnel like `ngrok http 12345` or forward port `12345` (TCP) in your router settings.
2. **Node Port (9000):** You **must** forward port `9000` (TCP) to your machine's local IP in your router's Port Forwarding dashboard. This allows tensors to travel across the internet to your node.
3. **Public IP:** Find your public IP at `whatismyip.com` and use it in your `PUBLIC_URL` variable so others can find you.

## 🧪 Proof of Concept: Collaborative Qwen3.5-27B Swarm

This is how we run **Qwen3.5-27B** (which normally requires ~18GB+ VRAM) across multiple consumer machines.

**Live POC Tracker:** `https://remedy-unwatched-styling.ngrok-free.dev`

1. **Leader Setup:** Runs the Tracker and the Entry Node (Layers 0-10).
2. **Dynamic Discovery:** Workers join and register with the tracker for subsequent layers (11-20, 21-30, etc.).
3. **Distributed Inference:** The hidden state tensor travels across the internet through each participant's node to complete the full 27B parameter forward pass.

## 🐳 Running with Docker (Recommended)

The easiest way to migrate and run LLM Swarm on any OS (Mac M1, Linux, Windows) is using Docker.

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

LLM Swarm is designed to be a drop-in replacement for OpenAI-compatible APIs. This allows you to use the power of the swarm with agentic frameworks like **Hermes Agent**, **AutoGPT**, or **LangChain**.

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

## 🗺️ Roadmap & TODO

LLM Swarm is an experimental prototype. We are looking for contributors to help with the following:

- [ ] **Security Hardening:** Implement Swarm-wide API Keys for node-to-node authentication.
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

## 💖 Support the Project
If you believe in the future of decentralized AI and want to support the development of LLM Swarm, donations are greatly appreciated!

**Donations (PayPal/Email):** [rtmalikian@gmail.com](mailto:rtmalikian@gmail.com)

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
