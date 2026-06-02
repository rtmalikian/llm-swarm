# Changelog

All notable changes to the **LLM Swarm** project will be documented in this file.

## [0.2.0] - 2026-06-02
### Security
- **Swarm API Key Authentication:** Implemented shared-secret `X-Swarm-Key` header validation on all tracker and node endpoints. When `SWARM_API_KEY` is set, unauthorized requests are rejected with `401`. Backward-compatible: unset key allows open access.
- All outgoing node-to-tracker and node-to-node HTTP calls now include the `X-Swarm-Key` header automatically.
- Updated `docker-compose.yml` to propagate `SWARM_API_KEY` to all services.

## [0.1.0] - 2026-04-28
### Added
- **Initial Prototype:** Core P2P Pooled Compute architecture implemented in Python.
- **Pipeline Parallelism:** Logic for forwarding hidden state tensors between nodes.
- **Dynamic Peer Discovery:** Centralized Tracker Node (`tracker.py`) for automatic node registration and health monitoring.
- **Docker Support:** Added `Dockerfile` and `docker-compose.yml` for multi-platform deployment (M1 Mac, Linux, Windows).
- **Test Suite:** Automated local mesh simulation script `test_mesh.py`.
- **Project Documentation:** Comprehensive README with architecture overview and installation guides.
- **Model Slicing Utility:** Added `slice_model.py` to allow nodes to host specific layer ranges of large GGUF models (e.g., Qwen-27B).
- **Agent Integration:** Implemented OpenAI-compatible `/v1/chat/completions` endpoint for seamless use with Hermes Agent, AutoGPT, and other AI frameworks.
- **Public Swarm Instructions:** Added detailed guides for users to join live swarms via public tracker URLs (e.g., ngrok).

### Changed
- Moved from hardcoded peer lists to dynamic tracker-based discovery.
- Standardized tracker port to `12345` to avoid common system conflicts.

### Security
- Implemented MIT License for open-source distribution.
- Added basic heartbeat mechanism to prevent stale peer routing.
