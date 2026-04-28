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
        self.url = f"http://localhost:{port}"
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

@app.on_event("startup")
async def startup_event():
    # 1. Load Model (if any)
    if config.model_path and os.path.exists(config.model_path):
        print(f"[{config.node_id}] Loading model: {config.model_path}")
        try:
            config.llm = Llama(model_path=config.model_path, n_ctx=512, verbose=False)
        except Exception as e:
            print(f"Error loading model: {e}")

    # 2. Register with Tracker
    registration_data = {
        "node_id": config.node_id,
        "url": config.url,
        "model_id": config.model_id,
        "layer_start": config.layers[0],
        "layer_end": config.layers[1]
    }
    try:
        async with httpx.AsyncClient() as client:
            await client.post(f"{config.tracker_url}/register", json=registration_data)
            print(f"[{config.node_id}] Registered with tracker at {config.tracker_url}")
    except Exception as e:
        print(f"[{config.node_id}] Failed to register with tracker: {e}")

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=9000)
    args = parser.parse_args()
    
    config = NodeConfig(args.port)
    uvicorn.run(app, host="0.0.0.0", port=args.port)
