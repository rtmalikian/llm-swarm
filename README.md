# 🚀 LLM Swarm: Decentralized P2P Pooled Compute Mesh

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

**LLM Swarm** is a revolutionary, open-source technology designed to put the power of Large Language Models (LLMs) back into the hands of the people. By utilizing a peer-to-peer (P2P) grid/mesh—similar to BitTorrent—LLM Swarm allows users to pool their hardware resources (RAM/VRAM) to run massive models that would otherwise require expensive cloud subscriptions or industrial-grade GPUs.

## 🌟 Key Features

- **Distributed Layer Execution:** Split large models (e.g., Llama-3 70B) across multiple consumer devices.
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

### 2. Prepare your Model Slice
You don't need the whole model! Download the GGUF and slice only the layers you want to contribute (e.g., layers 11-20).
```bash
# Example: Contribution layers 11-20 of Qwen-27B
python slice_model.py Qwen_Qwen3.5-27B-Q4_K_M.gguf qwen_slice_11_20.gguf 11 20
```

### 3. Start your Worker Node
Point your node to the Leader's Public Tracker. Replace `[TRACKER_URL]` with the link shared on X/social media.
```bash
export TRACKER_URL="https://your-leader-id.ngrok-free.app"
export NODE_ID="Volunteer_Node_$(hostname)"
export LAYER_START=11
export LAYER_END=20
export MODEL_PATH="qwen_slice_11_20.gguf"

python swarm_node.py --port 9001
```

Once started, your node will automatically register with the Leader. When a prompt is processed, your machine will handle its assigned layers and forward the result, contributing to the global "Swarm" inference!

## 🧪 Proof of Concept: Collaborative Qwen-27B Swarm

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
   source llm_pool_venv/lib/activate
   pip install -r requirements.txt
   ```

2. **Start the Tracker:**
   ```bash
   python tracker.py
   ```

3. **Start Worker/Entry Nodes:**
   See the `test_mesh.py` or the `docker-compose.yml` for environment variable configurations.

## 👤 Author
**Raphael Malikian**  
*Based in Palmdale, California*  
A visionary developer focused on decentralizing AI and making advanced technology accessible to everyone.

## 💖 Support the Project
If you believe in the future of decentralized AI and want to support the development of LLM Swarm, donations are greatly appreciated!

**Donations (PayPal/Email):** [rtmalikian@gmail.com](mailto:rtmalikian@gmail.com)

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
