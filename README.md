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

## 🧪 Proof of Concept: Collaborative Qwen-27B Swarm

This is how we run a model like **Qwen-2.5-27B** (which normally requires ~18GB+ VRAM) across multiple consumer machines.

### 1. The Setup (Leader)
The Swarm Leader (e.g., @rtmalikian) runs the Tracker and the Entry Node.
- **Tracker:** `python tracker.py`
- **Entry Node:** `IS_ENTRY=true LAYER_START=0 LAYER_END=10 python swarm_node.py`

### 2. Slicing the Model
Each node only needs to host a small "slice" of the model. 
```bash
# Leader slices layers 0-10
python slice_model.py qwen27b.gguf qwen_slice_0_10.gguf 0 10

# Worker A slices layers 11-20
python slice_model.py qwen27b.gguf qwen_slice_11_20.gguf 11 20
```

### 3. Joining the Swarm (As a Volunteer)
If you want to contribute compute power to the Qwen swarm:
1. Install dependencies: `pip install -r requirements.txt`
2. Connect to the public tracker:
```bash
export TRACKER_URL="http://[LEADER_PUBLIC_IP]:12345"
export NODE_ID="My_Volunteer_PC"
export LAYER_START=11
export LAYER_END=20
export MODEL_PATH="qwen_slice_11_20.gguf"
python swarm_node.py --port 9001
```

### 4. Generation
When the Leader sends a prompt, the "tensor hidden state" travels from the Leader's iMac to your PC and back, completing the 27B parameter inference collaboratively!

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
