"""
LLM-based Director for Agent-Landmark Assignment

This module provides high-level coordination for cooperative MARL tasks
by assigning agents to landmarks using either:
1. Greedy algorithm (minimum total distance)
2. LLM-based reasoning (OpenAI API with fallback to greedy)

The director acts as a centralized planner that computes one-to-one
agent-landmark assignments to minimize total travel distance.
"""

from __future__ import annotations
import os
import json
from typing import List, Tuple
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def _greedy_min_cost_assign(dist: List[List[float]]) -> List[Tuple[int, int]]:
    """
    Greedy algorithm for one-to-one assignment minimizing total distance.
    
    This is sufficient for small-scale demos (e.g., 3 agents × 3 landmarks).
    For larger problems, consider Hungarian algorithm (scipy.optimize.linear_sum_assignment).
    
    Args:
        dist: Distance matrix where dist[i][j] is distance from agent i to landmark j
        
    Returns:
        List of (agent_index, landmark_index) pairs
    """
    n_agents = len(dist)
    n_landmarks = len(dist[0]) if n_agents else 0
    
    pairs, used_a, used_l = [], set(), set()
    
    # Create list of (distance, agent_idx, landmark_idx) tuples
    triples = [
        (dist[a][l], a, l)
        for a in range(n_agents)
        for l in range(n_landmarks)
    ]
    
    # Sort by distance (break ties by agent index, then landmark index)
    triples.sort(key=lambda x: (x[0], x[1], x[2]))
    
    # Greedily assign pairs ensuring one-to-one mapping
    for cost, a, l in triples:
        if a in used_a or l in used_l:
            continue
        pairs.append((a, l))
        used_a.add(a)
        used_l.add(l)
        if len(pairs) == min(n_agents, n_landmarks):
            break
    
    return pairs


def _format(pairs, agent_ids, lm_ids, rationale: str):
    """
    Format assignment result as standardized JSON.
    
    Args:
        pairs: List of (agent_index, landmark_index) tuples
        agent_ids: List of agent ID strings
        lm_ids: List of landmark ID strings
        rationale: Explanation of the assignment strategy
        
    Returns:
        Dictionary with 'assignments' and 'rationale' keys
    """
    return {
        "assignments": [
            {"agent": agent_ids[a], "landmark": lm_ids[l]}
            for a, l in pairs
        ],
        "rationale": rationale
    }


def _call_openai(dist, agent_ids, lm_ids):
    """
    Call OpenAI API to generate agent-landmark assignments using LLM reasoning.
    
    The LLM is prompted to produce a one-to-one assignment that minimizes
    total distance, with JSON output format.
    
    Args:
        dist: Distance matrix
        agent_ids: List of agent IDs
        lm_ids: List of landmark IDs
        
    Returns:
        Parsed JSON dictionary with 'assignments' and 'rationale', or None on failure
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        
        # System prompt defining the task
        system_prompt = (
            "You are an expert planner for multi-agent coordination. "
            "Given a distance matrix between agents and landmarks, assign each agent "
            "to exactly one landmark with one-to-one mapping to minimize total distance. "
            "Return pure JSON with format: "
            '{"assignments": [{"agent": "agent_0", "landmark": "l2"}], "rationale": "explanation"}. '
            "Use only the provided agent and landmark IDs."
        )
        
        # User message with problem data
        user_message = json.dumps(
            {
                "distance": dist,
                "agents": agent_ids,
                "landmarks": lm_ids
            },
            ensure_ascii=False
        )
        
        # Call OpenAI API
        resp = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0  # Deterministic for consistency
        )
        
        # Parse response
        txt = resp.choices[0].message.content or ""
        
        # Extract JSON from markdown code blocks if present
        s, e = txt.find("{"), txt.rfind("}")
        if s >= 0 and e > s:
            return json.loads(txt[s:e + 1])
        
    except Exception as e:
        # Log error for debugging (in production, use proper logging)
        print(f"[LLM Director] OpenAI API error: {e}")
        return None
    
    return None


def plan_assignments(
    distance_matrix: List[List[float]],
    agent_ids: List[str],
    lm_ids: List[str],
    mode: str = "auto"
) -> dict:
    """
    Compute agent-landmark assignments using specified planning mode.
    
    Args:
        distance_matrix: 2D list where [i][j] is distance from agent i to landmark j
        agent_ids: List of agent ID strings (e.g., ["agent_0", "agent_1", "agent_2"])
        lm_ids: List of landmark ID strings (e.g., ["l0", "l1", "l2"])
        mode: Planning mode - "auto" (default), "greedy", or "llm"
        
    Returns:
        Dictionary with:
        - 'assignments': List of {"agent": str, "landmark": str} mappings
        - 'rationale': String explaining the assignment strategy
        
    Example:
        >>> dist = [[1.0, 2.0], [2.0, 1.0]]
        >>> agents = ["agent_0", "agent_1"]
        >>> landmarks = ["l0", "l1"]
        >>> plan_assignments(dist, agents, landmarks, mode="greedy")
        {
            'assignments': [
                {'agent': 'agent_0', 'landmark': 'l0'},
                {'agent': 'agent_1', 'landmark': 'l1'}
            ],
            'rationale': 'Greedy minimum distance assignment.'
        }
    """
    m = (mode or "auto").lower()
    
    if m == "llm":
        # Try LLM-based assignment first
        js = _call_openai(distance_matrix, agent_ids, lm_ids)
        
        if js and "assignments" in js:
            # Validate that assignments use correct IDs
            valid = all(
                item.get("agent") in agent_ids and item.get("landmark") in lm_ids
                for item in js.get("assignments", [])
            )
            if valid:
                js.setdefault("rationale", "LLM-based assignment")
                return js
        
        # Fallback to greedy on API failure or invalid response
        pairs = _greedy_min_cost_assign(distance_matrix)
        return _format(
            pairs, agent_ids, lm_ids,
            "Fallback to greedy (LLM API error or invalid response)"
        )
    else:
        # Default: greedy algorithm
        pairs = _greedy_min_cost_assign(distance_matrix)
        return _format(
            pairs, agent_ids, lm_ids,
            "Greedy minimum distance assignment"
        )
