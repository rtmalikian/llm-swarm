#!/bin/bash

# 🚀 LLM Swarm: Native Leader Launch (Optimized for Mac)
echo "🚀 Starting LLM Swarm Natively..."

# 1. Activate Virtual Environment
if [ -d "llm_pool_venv" ]; then
    source llm_pool_venv/bin/activate
else
    echo "❌ Error: llm_pool_venv not found."
    exit 1
fi

# 2. Start Tracker in background
echo "📡 Starting Tracker on port 12345..."
python3 tracker.py > tracker.log 2>&1 &
TRACKER_PID=$!

# 3. Setup Environment for Node
export NODE_ID="Leader_Mac_$(hostname)"
export IS_ENTRY=true
export LAYER_START=0
export LAYER_END=10
export TRACKER_URL="http://localhost:12345"
export MODEL_PATH="Qwen_Qwen3.5-27B-Q4_K_M.gguf"
export PUBLIC_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "import sys, json; print(json.load(sys.stdin)['tunnels'][0]['public_url'])")

if [ -z "$PUBLIC_URL" ]; then
    echo "⚠️  Warning: Could not detect ngrok public URL. Is ngrok running on port 12345?"
fi

# 4. Start Entry Node
echo "🧠 Starting Entry Node (Layers 0-10)..."
echo "Public URL: $PUBLIC_URL"
python3 swarm_node.py --port 9000

# Cleanup on exit
kill $TRACKER_PID
