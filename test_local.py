"""
Quick local test for TrustVerifier API
Run: python test_local.py
"""

import httpx
import asyncio
import json

BASE_URL = "http://localhost:8000"

async def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

async def test_verify_trust():
    """Test trust verification"""
    print("\n=== Testing Trust Verification ===")
    
    request_data = {
        "agent_id": "did:gerundium:test123",
        "context": {
            "platform": "nearai",
            "reputation": 85
        },
        "platforms": ["github", "nearai", "clawfriend"]
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/verify-trust",
            json=request_data,
            timeout=10.0
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Error: {response.text}")

async def test_get_profile():
    """Test agent profile retrieval"""
    print("\n=== Testing Agent Profile ===")
    
    agent_id = "did:gerundium:test123"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/v1/agent/{agent_id}")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

async def main():
    """Run all tests"""
    print("=" * 60)
    print("TrustVerifier API Local Test Suite")
    print("=" * 60)
    
    try:
        await test_health()
        await test_verify_trust()
        await test_get_profile()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        
    except httpx.ConnectError:
        print("\n❌ ERROR: Could not connect to server")
        print("Make sure the server is running: python main.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
