"""
Agent Trust Stack Pilot - Endpoints for Nanook collaboration
Created: 2026-02-18
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, date
import json
import os
from pathlib import Path

# Initialize router
router = APIRouter(prefix="/pilot", tags=["pilot"])

# Data directory (use /tmp for Vercel compatibility)
PILOT_DATA_DIR = Path("/tmp/pilot_data") if os.path.exists("/tmp") else Path("pilot_data")
SNAPSHOTS_DIR = PILOT_DATA_DIR / "snapshots"
SCORES_DIR = PILOT_DATA_DIR / "scores"

# Ensure directories exist
SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
SCORES_DIR.mkdir(parents=True, exist_ok=True)

# Pilot cohort (10 agents)
PILOT_COHORT = {
    "getclawe": {"score_baseline": 8, "category": "coordination"},
    "ucsandman": {"score_baseline": 8, "category": "observability"},
    "star-ga": {"score_baseline": 7, "category": "infrastructure"},
    "sene1337": {"score_baseline": 7, "category": "security"},
    "DiffDelta": {"score_baseline": 7, "category": "identity"},
    "clawdeckio": {"score_baseline": 7, "category": "observability"},
    "JIGGAI": {"score_baseline": 6, "category": "tooling", "voluntary": True},
    "profbernardoj": {"score_baseline": 6, "category": "infrastructure"},
    "marian2js": {"score_baseline": 6, "category": "coordination"},
    "toml0006": {"score_baseline": 6, "category": "observability"}
}

# Data models
class SnapshotData(BaseModel):
    """Daily snapshot data from Nanook"""
    agent_id: str = Field(..., description="Agent identifier (GitHub username)")
    date: str = Field(..., description="Snapshot date (YYYY-MM-DD)")
    commits: int = Field(0, description="Number of commits")
    releases: int = Field(0, description="Number of releases")
    issues_closed: int = Field(0, description="Issues closed")
    prs_merged: int = Field(0, description="PRs merged")
    stars_gained: int = Field(0, description="Stars gained")
    contributors: int = Field(0, description="Active contributors")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

class TrustScore(BaseModel):
    """Computed trust score for an agent"""
    agent_id: str
    pdr: float = Field(..., description="Promise Delivery Ratio (0-1)")
    ass: Optional[float] = Field(None, description="Address Stability Score")
    mdr: Optional[float] = Field(None, description="Memory Distortion Ratio")
    quality_score: float = Field(..., description="Quality signals (0-100)")
    overall_score: float = Field(..., description="Overall trust score (0-100)")
    provenance_chain: Dict[str, Any] = Field(..., description="Provenance of score computation")
    last_updated: datetime

class CohortStatus(BaseModel):
    """Status of entire pilot cohort"""
    total_agents: int
    active_agents: int
    snapshot_dates: List[str]
    agents: List[Dict[str, Any]]
    last_updated: datetime

# Endpoints

@router.post("/ingest")
async def ingest_snapshot(snapshot: SnapshotData):
    """
    Ingest daily snapshot data from Nanook
    
    Stores raw snapshot data for later processing
    """
    # Validate agent is in cohort
    if snapshot.agent_id not in PILOT_COHORT:
        raise HTTPException(
            status_code=400, 
            detail=f"Agent {snapshot.agent_id} not in pilot cohort"
        )
    
    # Create agent directory if needed
    agent_dir = SNAPSHOTS_DIR / snapshot.agent_id
    agent_dir.mkdir(exist_ok=True)
    
    # Save snapshot
    snapshot_file = agent_dir / f"{snapshot.date}.json"
    with open(snapshot_file, 'w') as f:
        json.dump(snapshot.dict(), f, indent=2)
    
    # Log receipt
    return {
        "status": "ingested",
        "agent_id": snapshot.agent_id,
        "date": snapshot.date,
        "file": str(snapshot_file),
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/score/{agent_id}", response_model=TrustScore)
async def get_agent_score(agent_id: str):
    """
    Compute and return trust score for an agent
    
    Computes PDR from stored snapshot data
    """
    # Validate agent
    if agent_id not in PILOT_COHORT:
        raise HTTPException(
            status_code=404,
            detail=f"Agent {agent_id} not in pilot cohort"
        )
    
    # Load all snapshots for this agent
    agent_dir = SNAPSHOTS_DIR / agent_id
    if not agent_dir.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No snapshot data found for agent {agent_id}"
        )
    
    snapshots = []
    for snapshot_file in sorted(agent_dir.glob("*.json")):
        with open(snapshot_file) as f:
            snapshots.append(json.load(f))
    
    if not snapshots:
        raise HTTPException(
            status_code=404,
            detail=f"No snapshot data for agent {agent_id}"
        )
    
    # Compute scores
    pdr, provenance = compute_pdr(agent_id, snapshots)
    quality_score = compute_quality_score(snapshots)
    overall_score = (pdr * 70) + (quality_score * 0.3)  # Weighted average
    
    score = TrustScore(
        agent_id=agent_id,
        pdr=pdr,
        quality_score=quality_score,
        overall_score=overall_score,
        provenance_chain=provenance,
        last_updated=datetime.utcnow()
    )
    
    # Cache score
    score_file = SCORES_DIR / f"{agent_id}.json"
    with open(score_file, 'w') as f:
        json.dump(score.dict(), f, indent=2, default=str)
    
    return score

@router.get("/cohort", response_model=CohortStatus)
async def get_cohort_status():
    """
    Get status of entire pilot cohort
    """
    agents = []
    snapshot_dates_set = set()
    
    for agent_id in PILOT_COHORT:
        agent_dir = SNAPSHOTS_DIR / agent_id
        snapshot_count = 0
        latest_date = None
        
        if agent_dir.exists():
            snapshot_files = list(agent_dir.glob("*.json"))
            snapshot_count = len(snapshot_files)
            
            if snapshot_files:
                latest_file = sorted(snapshot_files)[-1]
                latest_date = latest_file.stem
                snapshot_dates_set.add(latest_date)
        
        # Load cached score if available
        score_file = SCORES_DIR / f"{agent_id}.json"
        cached_score = None
        if score_file.exists():
            with open(score_file) as f:
                cached_score = json.load(f)
        
        agents.append({
            "agent_id": agent_id,
            "category": PILOT_COHORT[agent_id]["category"],
            "voluntary": PILOT_COHORT[agent_id].get("voluntary", False),
            "snapshot_count": snapshot_count,
            "latest_snapshot": latest_date,
            "current_score": cached_score.get("overall_score") if cached_score else None
        })
    
    active_agents = sum(1 for a in agents if a["snapshot_count"] > 0)
    
    return CohortStatus(
        total_agents=len(PILOT_COHORT),
        active_agents=active_agents,
        snapshot_dates=sorted(snapshot_dates_set),
        agents=agents,
        last_updated=datetime.utcnow()
    )

@router.get("/snapshot/{agent_id}/{snapshot_date}")
async def get_snapshot(agent_id: str, snapshot_date: str):
    """
    Get raw snapshot data for transparency
    """
    if agent_id not in PILOT_COHORT:
        raise HTTPException(
            status_code=404,
            detail=f"Agent {agent_id} not in pilot cohort"
        )
    
    snapshot_file = SNAPSHOTS_DIR / agent_id / f"{snapshot_date}.json"
    
    if not snapshot_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No snapshot found for {agent_id} on {snapshot_date}"
        )
    
    with open(snapshot_file) as f:
        return json.load(f)

# Helper functions

def compute_pdr(agent_id: str, snapshots: List[Dict]) -> tuple[float, Dict[str, Any]]:
    """
    Compute Promise Delivery Ratio from snapshot data
    
    For pilot v1: Use observable activity as proxy for delivery
    PDR = current_velocity / baseline_velocity
    """
    if not snapshots:
        return 0.0, {"error": "no_snapshots"}
    
    # Get baseline (first 7 days or all available)
    baseline_snapshots = snapshots[:7] if len(snapshots) >= 7 else snapshots
    current_snapshot = snapshots[-1]
    
    # Calculate baseline velocity
    baseline_commits = sum(s.get("commits", 0) for s in baseline_snapshots)
    baseline_releases = sum(s.get("releases", 0) for s in baseline_snapshots)
    baseline_days = len(baseline_snapshots)
    
    baseline_velocity = (baseline_commits + baseline_releases * 5) / baseline_days
    
    # Calculate current velocity (last 7 days)
    recent_snapshots = snapshots[-7:] if len(snapshots) >= 7 else snapshots
    current_commits = sum(s.get("commits", 0) for s in recent_snapshots)
    current_releases = sum(s.get("releases", 0) for s in recent_snapshots)
    current_days = len(recent_snapshots)
    
    current_velocity = (current_commits + current_releases * 5) / current_days
    
    # Compute PDR
    if baseline_velocity == 0:
        pdr = 1.0 if current_velocity > 0 else 0.5
    else:
        pdr = min(current_velocity / baseline_velocity, 2.0)  # Cap at 2.0 (200%)
    
    # Build provenance
    provenance = {
        "method": "velocity_based_pdr_v1",
        "source": "nanook_snapshots",
        "computation": {
            "baseline_commits": baseline_commits,
            "baseline_releases": baseline_releases,
            "baseline_days": baseline_days,
            "baseline_velocity": round(baseline_velocity, 2),
            "current_commits": current_commits,
            "current_releases": current_releases,
            "current_days": current_days,
            "current_velocity": round(current_velocity, 2),
            "pdr": round(pdr, 3)
        },
        "formula": "PDR = current_velocity / baseline_velocity (capped at 2.0)",
        "timestamp": datetime.utcnow().isoformat(),
        "verifier": "gerundium@agentmail.to"
    }
    
    return pdr, provenance

def compute_quality_score(snapshots: List[Dict]) -> float:
    """
    Compute quality score from observables
    
    Quality = stars_gained + contributors * 5 + issues_closed * 2
    """
    if not snapshots:
        return 50.0
    
    latest = snapshots[-1]
    
    stars = latest.get("stars_gained", 0)
    contributors = latest.get("contributors", 0)
    issues_closed = latest.get("issues_closed", 0)
    
    quality = stars + (contributors * 5) + (issues_closed * 2)
    
    # Normalize to 0-100
    quality_score = min(quality * 2, 100)
    
    return quality_score
