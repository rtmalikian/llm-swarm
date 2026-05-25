import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import time
import threading
from auth_utils import require_swarm_api_key

app = FastAPI()

class PeerInfo(BaseModel):
    node_id: str
    url: str
    model_id: str
    layer_start: int
    layer_end: int
    total_layers: int = 60
    last_seen: float = 0.0

# In-memory database of peers
peers_db: Dict[str, PeerInfo] = {}

def cleanup_stale_peers():
    """Background thread to remove peers that haven't heartbeated in 60 seconds."""
    while True:
        now = time.time()
        to_remove = [node_id for node_id, info in peers_db.items() if now - info.last_seen > 60]
        for node_id in to_remove:
            print(f"[Tracker] Removing stale peer: {node_id}")
            del peers_db[node_id]
        time.sleep(30)

@app.on_event("startup")
def start_cleanup_thread():
    threading.Thread(target=cleanup_stale_peers, daemon=True).start()

@app.post("/register", dependencies=[Depends(require_swarm_api_key)])
async def register_peer(peer: PeerInfo):
    peer.last_seen = time.time()
    peers_db[peer.node_id] = peer
    print(f"[Tracker] Registered/Updated peer: {peer.node_id} ({peer.url}) layers {peer.layer_start}-{peer.layer_end}")
    return {"status": "registered"}

@app.post("/heartbeat", dependencies=[Depends(require_swarm_api_key)])
async def heartbeat(node_id: str):
    if node_id in peers_db:
        peers_db[node_id].last_seen = time.time()
        return {"status": "ok"}
    raise HTTPException(status_code=404, detail="Peer not found")

@app.get("/peers", dependencies=[Depends(require_swarm_api_key)])
async def list_peers():
    return list(peers_db.values())

@app.get("/coverage", dependencies=[Depends(require_swarm_api_key)])
async def get_coverage():
    """Return a map of layer coverage to help nodes identify gaps."""
    coverage = {}
    total_layers = 60
    if peers_db:
        total_layers = list(peers_db.values())[0].total_layers
        
    for i in range(total_layers):
        coverage[i] = 0
        
    for peer in peers_db.values():
        for i in range(peer.layer_start, peer.layer_end + 1):
            if i in coverage:
                coverage[i] += 1
    
    return {
        "total_layers": total_layers,
        "coverage": coverage,
        "active_peers": len(peers_db)
    }

@app.get("/find_peer", dependencies=[Depends(require_swarm_api_key)])
async def find_peer(model_id: str, layer: int):
    # Find a peer that hosts the requested layer
    for peer in peers_db.values():
        if peer.model_id == model_id and peer.layer_start <= layer <= peer.layer_end:
            return peer
    raise HTTPException(status_code=404, detail="No peer found for requested layer")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=12345)
