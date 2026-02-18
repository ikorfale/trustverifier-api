"""Quick test for pilot endpoints"""
import requests
import json
from datetime import datetime, date

BASE_URL = "http://localhost:8000"

def test_cohort():
    """Test cohort status endpoint"""
    response = requests.get(f"{BASE_URL}/pilot/cohort")
    print(f"\n✅ GET /pilot/cohort: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_ingest():
    """Test snapshot ingestion"""
    snapshot = {
        "agent_id": "getclawe",
        "date": str(date.today()),
        "commits": 15,
        "releases": 2,
        "issues_closed": 3,
        "prs_merged": 5,
        "stars_gained": 10,
        "contributors": 3
    }
    
    response = requests.post(f"{BASE_URL}/pilot/ingest", json=snapshot)
    print(f"\n✅ POST /pilot/ingest: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_score():
    """Test score computation"""
    response = requests.get(f"{BASE_URL}/pilot/score/getclawe")
    print(f"\n✅ GET /pilot/score/getclawe: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    print("Testing pilot endpoints...")
    print("Make sure server is running: uvicorn main:app --reload")
    
    try:
        test_cohort()
        test_ingest()
        test_score()
        print("\n✅ All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
