"""
Multi-Agent Policy Server

A lightweight FastAPI server providing action recommendations for MARL agents.
Supports both random and heuristic (goal-directed) policies.

Endpoints:
- GET  /health: Health check
- POST /act: Get action for a given agent observation

This demonstrates API-first MARL architecture where policies are served
as microservices, decoupling training from deployment.
"""

import argparse
from fastapi import FastAPI
from pydantic import BaseModel, Field
import uvicorn
import numpy as np


# ========== Observation Parsing (simple_spread_v3) ==========
def extract_landmark_relpos(obs_vec: np.ndarray, n_landmarks: int) -> np.ndarray:
    """
    Extract landmark relative positions from observation vector.
    
    Observation format: [self_vel(2), self_pos(2), landmark_rel(2*nL), other_rel(2*(N-1)), ...]
    
    Args:
        obs_vec: Flattened observation vector
        n_landmarks: Number of landmarks in environment
        
    Returns:
        Array of shape (n_landmarks, 2) with relative positions
    """
    start, end = 4, 4 + 2 * n_landmarks
    return np.asarray(obs_vec[start:end], dtype=np.float32).reshape(n_landmarks, 2)


def discrete_move_towards(rel: np.ndarray, deadzone: float = 0.03) -> int:
    """
    Heuristic discrete action towards a target position.
    
    Discrete action encoding (MPE standard):
    0: no-op, 1: left, 2: right, 3: down, 4: up
    
    Strategy: Move along the axis with larger displacement;
              stop when within deadzone of target.
    
    Args:
        rel: Relative position (dx, dy) to target
        deadzone: Distance threshold to stop moving
        
    Returns:
        Discrete action index
    """
    dx, dy = float(rel[0]), float(rel[1])
    
    if abs(dx) < deadzone and abs(dy) < deadzone:
        return 0  # Stop when close
    
    # Move along axis with larger displacement
    if abs(dx) >= abs(dy):
        return 2 if dx > 0 else 1
    else:
        return 4 if dy > 0 else 3


# ========== Request/Response Models ==========
class ActReq(BaseModel):
    """Action request payload from MARL client."""
    agent_id: str
    obs: list[float]
    env: str = Field(pattern="^(simple_spread_v3|simple_tag_v3)$")
    mode: str = Field(pattern="^(random|to_target)$")  # random or goal-directed
    target_index: int | None = None
    n_landmarks: int = 3


class ActResp(BaseModel):
    """Action response with discrete action and reasoning."""
    action: int
    reason: str


# ========== FastAPI Application ==========
app = FastAPI(
    title="MARL Policy Server",
    version="0.1.0",
    description="Lightweight policy server for multi-agent environments"
)


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"ok": True, "status": "healthy"}


@app.post("/act", response_model=ActResp)
def act(req: ActReq):
    """
    Compute action for a single agent given its observation.
    
    Supports two modes:
    - 'random': Sample random action from action space
    - 'to_target': Use heuristic to move towards specified landmark
    
    Args:
        req: Action request with agent observation and parameters
        
    Returns:
        Action response with discrete action and explanation
    """
    obs = np.asarray(req.obs, dtype=np.float32)
    
    if req.env == "simple_spread_v3":
        if req.mode == "to_target" and req.target_index is not None:
            # Goal-directed heuristic
            rel_all = extract_landmark_relpos(obs, req.n_landmarks)
            k = int(np.clip(req.target_index, 0, req.n_landmarks - 1))
            a = discrete_move_towards(rel_all[k])
            return ActResp(
                action=int(a),
                reason=f"Heuristic towards landmark L{k}"
            )
        else:
            # Random exploration
            a = int(np.random.randint(0, 5))
            return ActResp(
                action=a,
                reason="Random action (no target assigned)"
            )
    else:
        # simple_tag_v3: Random actions (can be extended with chase/evade heuristics)
        a = int(np.random.randint(0, 5))
        return ActResp(
            action=a,
            reason="Random action (tag environment)"
        )


# ========== Server Entry Point ==========
if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="Start MARL policy server"
    )
    ap.add_argument(
        "--host",
        default="127.0.0.1",
        help="Server host address"
    )
    ap.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Server port"
    )
    args = ap.parse_args()
    
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info"
    )
