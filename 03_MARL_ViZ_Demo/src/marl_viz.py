"""
Multi-Agent Reinforcement Learning (MARL) Visualization Demo

This script demonstrates API-first MARL with PettingZoo environments:
- High-level director assigns agents to landmarks (greedy or LLM-based)
- Low-level policy server provides discrete actions via HTTP API
- Client renders episodes with annotated frames and metrics

Outputs:
- outputs/rollout_*.gif: Annotated episode visualization
- outputs/metrics_*.png: Cumulative team reward and coverage curves
"""

import argparse
import requests
from pathlib import Path
from typing import List, Dict

import imageio.v2 as imageio
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from pettingzoo.mpe import simple_spread_v3, simple_tag_v3
from llm_director import plan_assignments


# ========== Environment Factory ==========
def make_env(name: str = "spread", seed: int = 0, max_steps: int = 80):
    """
    Create and initialize a PettingZoo MPE environment.
    
    Args:
        name: Environment type ("spread" for cooperative, "tag" for adversarial)
        seed: Random seed for reproducibility
        max_steps: Maximum steps per episode
        
    Returns:
        Tuple of (environment, initial_observations)
    """
    if name == "spread":
        env = simple_spread_v3.parallel_env(
            N=3, local_ratio=0.5, max_cycles=max_steps,
            continuous_actions=False, render_mode="rgb_array"
        )
    elif name == "tag":
        env = simple_tag_v3.parallel_env(
            num_good=1, num_adversaries=2, num_obstacles=2,
            max_cycles=max_steps, continuous_actions=False, render_mode="rgb_array"
        )
    else:
        raise ValueError("env must be 'spread' or 'tag'")
    
    obs, _ = env.reset(seed=seed)
    return env, obs


# ========== Caption Overlay ==========
def overlay(frame: np.ndarray, lines: List[str], box=(0, 0, 640, 128)) -> np.ndarray:
    """
    Overlay text captions on a rendered frame.
    
    Args:
        frame: RGB frame array from environment rendering
        lines: List of text strings to display
        box: Bounding box (x1, y1, x2, y2) for semi-transparent background
        
    Returns:
        Frame with overlaid text
    """
    img = Image.fromarray(frame)
    draw = ImageDraw.Draw(img, "RGBA")
    
    # Semi-transparent dark background for readability
    draw.rectangle(box, fill=(0, 0, 0, 160))
    
    # Draw text lines
    y, x = box[1] + 8, box[0] + 10
    # Use default font for better compatibility
    # Default PIL font handles ASCII reliably
    
    for line in lines:
        draw.text((x, y), line, fill=(255, 255, 255, 235))
        y += 20
    
    return np.asarray(img)


# ========== Coverage Estimator (for spread environment) ==========
def _dilate(mask: np.ndarray, iters: int = 2) -> np.ndarray:
    """
    Morphological dilation for coverage estimation.
    Expands regions to account for agent influence area.
    """
    m = mask.astype(bool)
    for _ in range(iters):
        pad = np.pad(m, ((1, 1), (1, 1)), constant_values=False)
        out = np.zeros_like(m)
        for i in range(3):
            for j in range(3):
                out |= pad[i:i + m.shape[0], j:j + m.shape[1]]
        m = out
    return m


def estimate_coverage(frame: np.ndarray) -> float:
    """
    Estimate landmark coverage from rendered frame using color detection.
    
    Works by detecting green landmarks and nearby agents, then computing
    the fraction of landmark pixels covered by agent influence.
    
    Args:
        frame: RGB frame from environment rendering
        
    Returns:
        Coverage ratio [0, 1], or NaN if no landmarks detected
    """
    arr = frame
    
    # Detect green landmarks (bright green pixels)
    gmask = (arr[..., 1] > 160) & \
            (arr[..., 1] > arr[..., 0] + 30) & \
            (arr[..., 1] > arr[..., 2] + 30)
    
    # Detect agents (non-green bright pixels)
    agmask = (arr[..., 1] < 180) & ((arr[..., 0] > 120) | (arr[..., 2] > 120))
    agmask = _dilate(agmask, 3)
    
    total_g = gmask.sum()
    if total_g < 50:
        return float("nan")
    
    covered = (gmask & agmask).sum()
    return float(covered / (total_g + 1e-6))


# ========== Observation Helpers (spread environment) ==========
def extract_landmark_relpos(obs_vec: np.ndarray, n_landmarks: int) -> np.ndarray:
    """
    Extract relative landmark positions from observation vector.
    
    Observation format: [self_vel(2), self_pos(2), landmark_rel(2*N), other_rel(2*(N-1)), ...]
    
    Args:
        obs_vec: Flattened observation vector
        n_landmarks: Number of landmarks in environment
        
    Returns:
        Array of shape (n_landmarks, 2) with relative positions
    """
    start, end = 4, 4 + 2 * n_landmarks
    return np.asarray(obs_vec[start:end], dtype=np.float32).reshape(n_landmarks, 2)


def build_distance_matrix(obs_dict: Dict[str, np.ndarray], n_landmarks: int):
    """
    Build distance matrix from all agents to all landmarks.
    
    Args:
        obs_dict: Dictionary mapping agent_id to observation vector
        n_landmarks: Number of landmarks
        
    Returns:
        Tuple of (agent_ids, landmark_ids, distance_matrix)
    """
    agent_ids = sorted(list(obs_dict.keys()))
    lm_ids = [f"l{i}" for i in range(n_landmarks)]
    dist = []
    
    for aid in agent_ids:
        rel = extract_landmark_relpos(np.asarray(obs_dict[aid]), n_landmarks)
        dist.append([float(np.linalg.norm(rel[i])) for i in range(n_landmarks)])
    
    return agent_ids, lm_ids, dist


# ========== Local Discrete Controller ==========
def discrete_move_towards(rel: np.ndarray, deadzone: float = 0.03) -> int:
    """
    Heuristic controller for discrete movement towards a target.
    
    Discrete action encoding (MPE standard):
    0: no-op, 1: left, 2: right, 3: down, 4: up
    
    Args:
        rel: Relative position (dx, dy) to target
        deadzone: Distance threshold to stop moving
        
    Returns:
        Discrete action index
    """
    dx, dy = float(rel[0]), float(rel[1])
    
    if abs(dx) < deadzone and abs(dy) < deadzone:
        return 0  # Stop when close enough
    
    # Move along the axis with larger displacement
    if abs(dx) >= abs(dy):
        return 2 if dx > 0 else 1
    else:
        return 4 if dy > 0 else 3


# ========== Episode Recording ==========
def record_episode(
    env_name: str = "spread",
    max_steps: int = 80,
    seed: int = 7,
    fps: int = 8,
    out_dir: str | Path = "outputs",
    gif_name: str | None = None,
    png_name: str | None = None,
    director: str = "none",           # none | greedy | llm
    actor: str = "local",             # local | http
    policy_url: str = "http://127.0.0.1:8000/act",
):
    """
    Record a full MARL episode with visualization and metrics.
    
    This function orchestrates the entire demo:
    1. Initialize environment
    2. Optionally compute agent-landmark assignments (director)
    3. Execute episode by querying policy API or using local heuristics (actor)
    4. Render annotated frames with overlays
    5. Save GIF and metrics plot
    
    Args:
        env_name: Environment type ("spread" or "tag")
        max_steps: Maximum episode length
        seed: Random seed
        fps: Frames per second for GIF output
        out_dir: Output directory for artifacts
        gif_name: Custom GIF filename (default: auto-generated)
        png_name: Custom PNG filename (default: auto-generated)
        director: Assignment strategy ("none", "greedy", or "llm")
        actor: Action source ("local" heuristic or "http" API)
        policy_url: URL for policy server API endpoint
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    if gif_name is None:
        gif_name = f"rollout_{env_name}_seed{seed}.gif"
    if png_name is None:
        png_name = f"metrics_{env_name}_seed{seed}.png"
    
    # Initialize environment
    env, obs = make_env(env_name, seed=seed, max_steps=max_steps)
    n_landmarks = 3 if env_name == "spread" else 0
    
    # High-level assignment (only meaningful for spread environment)
    target_index_by_agent, rationale = {}, ""
    if env_name == "spread" and director.lower() in ("greedy", "llm"):
        agent_ids, lm_ids, dist = build_distance_matrix(obs, n_landmarks)
        plan = plan_assignments(
            dist, agent_ids, lm_ids,
            mode=("llm" if director == "llm" else "greedy")
        )
        rationale = plan.get("rationale", "")
        
        # Map landmark IDs to indices
        idxmap = {f"l{i}": i for i in range(n_landmarks)}
        for item in plan.get("assignments", []):
            a, l = item.get("agent"), item.get("landmark")
            if a in agent_ids and l in idxmap:
                target_index_by_agent[a] = idxmap[l]
    
    frames, ep_rewards, coverages = [], [], []
    done, step = False, 0
    
    # Main episode loop
    while not done and step < max_steps:
        acts = {}
        
        # Query actions for all agents
        for aid in env.agents:
            if actor == "http":
                # Call policy server API
                payload = {
                    "agent_id": aid,
                    "obs": list(map(float, np.asarray(obs[aid]).ravel())),
                    "env": "simple_spread_v3" if env_name == "spread" else "simple_tag_v3",
                    "mode": "to_target" if (env_name == "spread" and aid in target_index_by_agent) else "random",
                    "target_index": target_index_by_agent.get(aid),
                    "n_landmarks": n_landmarks
                }
                try:
                    r = requests.post(policy_url, json=payload, timeout=2)
                    a = int(r.json().get("action", 0))
                except Exception:
                    # Fallback to local heuristic on API failure
                    if env_name == "spread" and aid in target_index_by_agent:
                        rel_all = extract_landmark_relpos(np.asarray(obs[aid]), n_landmarks)
                        a = discrete_move_towards(rel_all[target_index_by_agent[aid]])
                    else:
                        a = env.action_space(aid).sample()
            else:
                # Use local heuristic or random action
                if env_name == "spread" and aid in target_index_by_agent:
                    rel_all = extract_landmark_relpos(np.asarray(obs[aid]), n_landmarks)
                    a = discrete_move_towards(rel_all[target_index_by_agent[aid]])
                else:
                    a = env.action_space(aid).sample()
            
            acts[aid] = a
        
        # Execute step
        obs, rews, terms, truncs, infos = env.step(acts)
        frame = env.render()
        team_r = float(sum(rews.values()))
        ep_rewards.append(team_r)
        
        # Prepare caption overlay
        if env_name == "spread":
            cov = estimate_coverage(frame)
            coverages.append(cov)
            
            goal_text = "Goal: 3 agents cover 3 landmarks (cooperative)"
            status = f"Coverage ~ {0.0 if np.isnan(cov) else cov * 100:4.1f}%"
            
            if target_index_by_agent:
                pairs_text = ", ".join(
                    f"A{a[-1]}->L{target_index_by_agent[a]}"
                    for a in sorted(target_index_by_agent)
                )
                extra = f"Assignment: {pairs_text}"
                if rationale:
                    extra += f" | Reason: {rationale[:40]}..." if len(rationale) > 40 else f" | Reason: {rationale}"
            else:
                extra = "Assignment: (none)"
        else:
            goal_text = "Goal: Predators chase prey (adversarial)"
            status = f"Team reward {team_r:+.2f}"
            extra = ""
        
        lines = [
            goal_text,
            f"Step {step:02d} | Cumulative reward {np.sum(ep_rewards):+.2f}",
            status
        ]
        if extra:
            lines.append(extra)
        
        frames.append(overlay(frame, lines))
        
        done = all(terms.values()) or all(truncs.values())
        step += 1
    
    # Save GIF
    gif_path = out_dir / gif_name
    imageio.mimsave(gif_path, frames, fps=fps)
    
    # Save metrics plot with dual subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
    
    # Top: Per-step reward (shows improvement)
    ax1.plot(ep_rewards, color='steelblue', linewidth=1.5, label="Per-step Reward")
    ax1.axhline(y=0, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)
    ax1.set_ylabel("Reward per Step", fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='lower right')
    ax1.set_title("Agent Performance Over Time", fontsize=11, fontweight='bold')
    
    # Bottom: Cumulative reward
    ax2.plot(np.cumsum(ep_rewards), color='darkblue', linewidth=1.5, label="Cumulative Reward")
    ax2.set_xlabel("Steps", fontsize=10)
    ax2.set_ylabel("Cumulative Reward", fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='lower right')
    
    # Add coverage curve for spread environment (on top subplot)
    if env_name == "spread" and coverages and not np.isnan(coverages).all():
        ax1_twin = ax1.twinx()
        ax1_twin.plot(np.array(coverages) * 100.0, color='orange', linestyle='--', 
                      linewidth=1.5, alpha=0.8, label="Coverage")
        ax1_twin.set_ylabel("Coverage (%)", color='orange', fontsize=10)
        ax1_twin.tick_params(axis='y', labelcolor='orange')
        ax1_twin.legend(loc='upper right')
    
    fig.tight_layout()
    png_path = out_dir / png_name
    fig.savefig(png_path, dpi=150)
    plt.close(fig)
    
    print(f"✓ Saved GIF: {gif_path}")
    print(f"✓ Saved metrics: {png_path}")


# ========== Command-Line Interface ==========
def parse_args():
    """Parse command-line arguments for the visualization demo."""
    p = argparse.ArgumentParser(
        description="API-first Multi-Agent Reinforcement Learning Visualization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Cooperative environment with greedy assignment and HTTP policy
  python marl_viz.py --env spread --steps 80 --director greedy --actor http --policy-url http://127.0.0.1:8000/act
  
  # Adversarial environment with local random actions
  python marl_viz.py --env tag --steps 120 --actor local
  
  # Cooperative with LLM-based assignment (requires OPENAI_API_KEY)
  python marl_viz.py --env spread --director llm --actor local
        """
    )
    
    p.add_argument(
        "--env",
        choices=["spread", "tag"],
        default="spread",
        help="Environment type: 'spread' (cooperative) or 'tag' (adversarial)"
    )
    p.add_argument(
        "--steps",
        type=int,
        default=80,
        help="Maximum steps per episode"
    )
    p.add_argument(
        "--seed",
        type=int,
        default=7,
        help="Random seed for reproducibility"
    )
    p.add_argument(
        "--fps",
        type=int,
        default=8,
        help="Frames per second for GIF output"
    )
    p.add_argument(
        "--out",
        type=str,
        default="outputs",
        help="Output directory for GIF and metrics"
    )
    p.add_argument(
        "--director",
        choices=["none", "greedy", "llm"],
        default="none",
        help="High-level assignment strategy: "
             "'none' (random), 'greedy' (minimum distance), 'llm' (OpenAI-based, fallback to greedy on error)"
    )
    p.add_argument(
        "--actor",
        choices=["local", "http"],
        default="local",
        help="Low-level action source: 'local' (heuristic/random) or 'http' (policy server API)"
    )
    p.add_argument(
        "--policy-url",
        type=str,
        default="http://127.0.0.1:8000/act",
        help="Policy server /act endpoint URL"
    )
    
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    record_episode(
        env_name=args.env,
        max_steps=args.steps,
        seed=args.seed,
        fps=args.fps,
        out_dir=args.out,
        director=args.director,
        actor=args.actor,
        policy_url=args.policy_url
    )
