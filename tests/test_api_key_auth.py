import importlib
from pathlib import Path
import sys
import types

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def reload_module(name):
    sys.modules.pop(name, None)
    return importlib.import_module(name)


def test_tracker_rejects_register_without_swarm_api_key(monkeypatch):
    monkeypatch.setenv("SWARM_API_KEY", "test-secret")
    tracker = reload_module("tracker")
    tracker.peers_db.clear()

    client = TestClient(tracker.app)
    response = client.post(
        "/register",
        json={
            "node_id": "node-a",
            "url": "http://node-a:9000",
            "model_id": "swarm-mesh-v1",
            "layer_start": 0,
            "layer_end": 4,
        },
    )

    assert response.status_code == 401
    assert tracker.peers_db == {}


def test_tracker_accepts_register_with_swarm_api_key(monkeypatch):
    monkeypatch.setenv("SWARM_API_KEY", "test-secret")
    tracker = reload_module("tracker")
    tracker.peers_db.clear()

    client = TestClient(tracker.app)
    response = client.post(
        "/register",
        headers={"Authorization": "Bearer test-secret"},
        json={
            "node_id": "node-a",
            "url": "http://node-a:9000",
            "model_id": "swarm-mesh-v1",
            "layer_start": 0,
            "layer_end": 4,
        },
    )

    assert response.status_code == 200
    assert "node-a" in tracker.peers_db


def test_swarm_node_rejects_layer_processing_without_swarm_api_key(monkeypatch):
    monkeypatch.setenv("SWARM_API_KEY", "test-secret")
    fake_llama_cpp = types.ModuleType("llama_cpp")
    fake_llama_cpp.Llama = object
    monkeypatch.setitem(sys.modules, "llama_cpp", fake_llama_cpp)
    swarm_node = reload_module("swarm_node")
    swarm_node.config = swarm_node.NodeConfig(port=9000)

    client = TestClient(swarm_node.app)
    response = client.post(
        "/process_layers",
        json={
            "model_id": "swarm-mesh-v1",
            "layer_start": 0,
            "layer_end": 4,
            "tensor_data": [1.0, 2.0],
            "shape": [1, 2],
            "prompt_tokens": [1],
            "current_token_index": 0,
        },
    )

    assert response.status_code == 401
