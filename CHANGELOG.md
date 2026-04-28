# Changelog

All notable changes to the **LLM Swarm** project will be documented in this file.

## [0.1.0] - 2026-04-28
### Added
- **Initial Prototype:** Core P2P Pooled Compute architecture implemented in Python.
- **Pipeline Parallelism:** Logic for forwarding hidden state tensors between nodes.
- **Dynamic Peer Discovery:** Centralized Tracker Node (`tracker.py`) for automatic node registration and health monitoring.
- **Docker Support:** Added `Dockerfile` and `docker-compose.yml` for multi-platform deployment (M1 Mac, Linux, Windows).
- **Test Suite:** Automated local mesh simulation script `test_mesh.py`.
- **Project Documentation:** Comprehensive README with architecture overview and installation guides.

### Changed
- Moved from hardcoded peer lists to dynamic tracker-based discovery.
- Standardized tracker port to `12345` to avoid common system conflicts.

### Security
- Implemented MIT License for open-source distribution.
- Added basic heartbeat mechanism to prevent stale peer routing.
