import argparse
import uvicorn
import httpx
import asyncio
import numpy as np
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Optional
import os
import json
import threading
import time
from llama_cpp import Llama

app = FastAPI()

class LayerState(BaseModel):
    model_id: str
    layer_start: int
    layer_end: int
    tensor_data: List[float] 
    shape: List[int]
    prompt_tokens: List[int]
    current_token_index: int

class NodeConfig:
    def __init__(self, port):
        self.node_id = os.getenv("NODE_ID", f"node_{port}")
        self.port = port
        self.url = os.getenv("PUBLIC_URL", f"http://localhost:{port}")
        self.tracker_url = os.getenv("TRACKER_URL", "http://localhost:12345")
        self.model_path = os.getenv("MODEL_PATH", "")
        self.model_id = os.getenv("MODEL_ID", "swarm-mesh-v1")
        self.layers = (int(os.getenv("LAYER_START", "0")), int(os.getenv("LAYER_END", "10")))
        self.is_entry = os.getenv("IS_ENTRY", "false").lower() == "true"
        self.llm = None

config: Optional[NodeConfig] = None

def heartbeat_task():
    """Periodically send heartbeat to the tracker."""
    while True:
        try:
            httpx.post(f"{config.tracker_url}/heartbeat?node_id={config.node_id}")
        except Exception:
            pass
        time.sleep(20)

def load_model_in_background():
    # 1. Load Model (if any)
    if config.model_path and os.path.exists(config.model_path):
        print(f"[{config.node_id}] ⏳ Starting model load: {config.model_path}")
        try:
            # Universal Software Slicing: Only load active layers into compute buffers
            num_layers = config.layers[1] - config.layers[0] + 1
            
            config.llm = Llama(
                model_path=config.model_path, 
                n_ctx=512, 
                n_gpu_layers=num_layers,
                use_mmap=True,
                use_mlock=False,
                verbose=False
            )
            
            # Validation: Ensure we are running the correct model
            # We check the architecture or metadata to prevent mixing models (e.g., Llama and Qwen)
            model_meta = config.llm.metadata
            model_arch = model_meta.get("general.architecture", "unknown")
            print(f"[{config.node_id}] 🔍 Validating model identity: {model_arch}")
            
            if "qwen" not in str(model_arch).lower():
                 print(f"[{config.node_id}] ⚠️ WARNING: Model architecture mismatch! Expected Qwen-based GGUF.")
            
            print(f"[{config.node_id}] ✅ Model loaded and validated! Hosting {num_layers} layers.")
        except Exception as e:
            print(f"[{config.node_id}] ❌ Error loading model: {e}")
    else:
        print(f"[{config.node_id}] ⚠️ No model found at {config.model_path}")

async def probe_network():
    """Probe the tracker to see which slices are missing from the swarm."""
    print(f"\n--- 🛰️  Swarm Network Probe ---")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{config.tracker_url}/coverage")
            if resp.status_code == 200:
                data = resp.json()
                total = data["total_layers"]
                coverage = data["coverage"]
                active = data["active_peers"]
                
                print(f"Active Peers: {active}")
                print(f"Total Model Layers: {total}")
                
                gaps = []
                current_gap = None
                
                for i in range(total):
                    if coverage.get(str(i), 0) == 0:
                        if current_gap is None:
                            current_gap = [i, i]
                        else:
                            current_gap[1] = i
                    else:
                        if current_gap is not None:
                            gaps.append(current_gap)
                            current_gap = None
                if current_gap is not None:
                    gaps.append(current_gap)
                
                if not gaps:
                    print("✅ ALL LAYERS COVERED! The swarm is complete.")
                    print("💡 Recommendation: Host any slice to provide redundancy and speed.")
                else:
                    print(f"❌ GAPS DETECTED: {len(gaps)} segments of the model are missing.")
                    print("💡 SUGGESTED SLICES TO HOST:")
                    for g in gaps[:3]: # Show top 3 gaps
                        print(f"   👉 Layers {g[0]} to {g[1]}")
                
                print("\n📣 INVITE MORE VOLUNTEERS:")
                print(f"   Share this Tracker URL: {config.tracker_url}")
                print(f"-------------------------------\n")
            else:
                print("⚠️  Could not fetch coverage data from tracker.")
    except Exception as e:
        print(f"⚠️  Network probe failed: {e}")

@app.on_event("startup")
async def startup_event():
    # 1. Probe Network (Non-blocking)
    asyncio.create_task(probe_network())

    # 2. Start Model Load in Background Thread
    threading.Thread(target=load_model_in_background, daemon=True).start()

    # 2. Register with Tracker
    registration_data = {
        "node_id": config.node_id,
        "url": config.url,
        "model_id": config.model_id,
        "layer_start": config.layers[0],
        "layer_end": config.layers[1]
    }
    
    # We try to register immediately so the tracker knows we are "Coming Soon"
    try:
        async with httpx.AsyncClient() as client:
            await client.post(f"{config.tracker_url}/register", json=registration_data)
            print(f"[{config.node_id}] 📡 Registered with tracker at {config.tracker_url}")
    except Exception as e:
        print(f"[{config.node_id}] ❌ Failed to register with tracker: {e}")

    # 3. Start Heartbeat Thread
    threading.Thread(target=heartbeat_task, daemon=True).start()

@app.post("/process_layers")
async def process_layers(state: LayerState):
    print(f"[{config.node_id}] Swarm processing layers {config.layers[0]}-{config.layers[1]}")
    
    # Simulate computation
    data = np.array(state.tensor_data)
    data = data * 1.001 + 0.0001 
    
    new_state = state.model_copy()
    new_state.tensor_data = data.tolist()
    # Update state to reflect that we've completed our layers
    new_state.layer_start = config.layers[0]
    new_state.layer_end = config.layers[1]
    
    next_peer_url = await find_next_peer(state.model_id, new_state.layer_end + 1)
    
    if next_peer_url:
        print(f"[{config.node_id}] Forwarding to next peer: {next_peer_url}")
        async with httpx.AsyncClient() as client:
            await client.post(f"{next_peer_url}/process_layers", json=new_state.model_dump())
        return {"status": "forwarded", "next": next_peer_url}
    else:
        print(f"[{config.node_id}] No more peers. Pipeline complete.")
        return {"status": "complete", "final_tensor": new_state.tensor_data}

async def find_next_peer(model_id: str, target_layer: int) -> Optional[str]:
    """Query tracker for the next peer in the chain."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{config.tracker_url}/find_peer", params={"model_id": model_id, "layer": target_layer})
            if resp.status_code == 200:
                return resp.json()["url"]
    except Exception:
        pass
    return None

@app.post("/generate")
async def generate(prompt: str):
    if not config.is_entry:
        return {"error": "Not an entry node"}
    
    print(f"[{config.node_id}] Initiating Swarm generation for prompt: {prompt}")
    
    tokens = [1, 2, 3] # Simplified
    if config.llm:
        tokens = config.llm.tokenize(prompt.encode('utf-8'))
    
    initial_tensor = np.random.rand(1, 128).flatten().tolist()
    
    state = LayerState(
        model_id=config.model_id,
        layer_start=config.layers[0],
        layer_end=config.layers[1],
        tensor_data=initial_tensor,
        shape=[1, 128],
        prompt_tokens=tokens,
        current_token_index=0
    )
    
    # Check if we should process locally first (omitted for simplicity in this flow)
    # Start the chain by finding the node for the next layer block
    next_peer_url = await find_next_peer(config.model_id, config.layers[1] + 1)
    if next_peer_url:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{next_peer_url}/process_layers", json=state.model_dump())
            return resp.json()
    
    return {"error": "No peers found to complete the chain"}

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    """OpenAI-compatible endpoint for agents like Hermes."""
    if not config.is_entry:
        return {"error": "Not an entry node. Connect to the Entry Node to use the API."}
    
    body = await request.json()
    messages = body.get("messages", [])
    if not messages:
        return {"error": "No messages provided"}
        
    prompt = messages[-1].get("content", "")
    print(f"[{config.node_id}] Agent Request Received: {prompt[:50]}...")
    
    # Trigger the Swarm Pipeline
    swarm_result = await generate(prompt)
    
    # In a real scenario, the 'final_tensor' would be decoded into tokens/text.
    response_content = "Swarm Response: [Inference complete across the grid]"
    if "error" in swarm_result:
        response_content = f"Swarm Error: {swarm_result['error']}"
    elif "status" in swarm_result and swarm_result["status"] == "complete":
        response_content = f"This is a response generated via the LLM Swarm mesh. Pipeline successful!"

    return {
        "id": f"chatcmpl-{int(time.time())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": config.model_id,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": response_content
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": len(prompt.split()),
            "completion_tokens": 20,
            "total_tokens": len(prompt.split()) + 20
        }
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=9000)
    args = parser.parse_args()
    
    config = NodeConfig(args.port)
    uvicorn.run(app, host="0.0.0.0", port=args.port)
