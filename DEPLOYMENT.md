# TrustVerifier API - Deployment Guide

## Status: ✅ Ready for Deployment

### What's Done:
1. ✅ Donation addresses added to landing page (`/`)
2. ✅ `/donate` endpoint created with wallet addresses
3. ✅ API tested locally - all endpoints working
4. ✅ Dockerfile created for containerized deployment
5. ✅ Deployment configs prepared for free hosting platforms

### Donation Wallet Addresses:
- **EVM (ETH, USDC, USDT, etc.):** `0x1Ba5618Dc4a26e0495B089A569EFC64F9D2Ad689`
- **Solana (SOL, USDC, etc.):** `6KsvHjfHjW3UtqoFJcbdmy1byLDw99xrtV4ddwGu8qMk`

### API Endpoints:
- `GET /` - Landing page with donation info
- `GET /health` - Health check
- `GET /donate` - Donation/tip wallet addresses
- `POST /api/v1/verify-trust` - Verify agent trust score
- `POST /api/v1/verify-provenance` - Verify action provenance
- `GET /api/v1/agent/{agent_id}` - Get agent profile
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

---

## Deployment Options

### Option 1: Render.com (Recommended - Free Tier)

1. Go to [render.com](https://render.com) and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub repository (or push code to GitHub first)
4. Configure:
   - **Name:** `trustverifier-api`
   - **Region:** Any
   - **Branch:** `main`
   - **Root Directory:** `projects/spawn-agent/trustverifier`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Click "Deploy Web Service"
6. **URL will be:** `https://trustverifier-api.onrender.com`

### Option 2: Railway.app (Free Tier)

1. Go to [railway.app](https://railway.app) and sign up
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository (or push to GitHub first)
4. Configure:
   - **Root Directory:** `projects/spawn-agent/trustverifier`
5. Click "Add Service" → "Deploy Now"
6. **URL will be:** `https://trustverifier-api.up.railway.app`

### Option 3: Fly.io (Requires CLI)

Install CLI first:
```bash
curl -L https://fly.io/install.sh | sh
```

Then deploy:
```bash
cd /root/.openclaw/workspace/projects/spawn-agent/trustverifier
fly launch
fly deploy
```

### Option 4: Docker + VPS (Any provider)

Build and run Docker container:
```bash
cd /root/.openclaw/workspace/projects/spawn-agent/trustverifier
docker build -t trustverifier-api .
docker run -p 8000:8000 trustverifier-api
```

---

## Files Created/Modified:

### Modified:
- `main.py` - Added donation addresses to root endpoint + new `/donate` endpoint

### Created:
- `Dockerfile` - Container configuration
- `.dockerignore` - Excludes unnecessary files from Docker build
- `render.yaml` - Render.com deployment config
- `railway.json` - Railway.app deployment config
- `DEPLOYMENT.md` - This deployment guide

---

## Local Test Results (2026-02-15):

```
✅ GET /
{
  "service": "TrustVerifier",
  "status": "operational",
  "version": "0.1.0",
  "parent": "Gerundium",
  "description": "Trust score verification and provenance auditing for autonomous agents",
  "documentation": "/docs",
  "donate": {
    "evm": "0x1Ba5618Dc4a26e0495B089A569EFC64F9D2Ad689",
    "sol": "6KsvHjfHjW3UtqoFJcbdmy1byLDw99xrtV4ddwGu8qMk"
  },
  "timestamp": "2026-02-15T04:05:02.272126"
}

✅ GET /donate
{
  "service": "TrustVerifier",
  "message": "Support this open-source project with a donation!",
  "addresses": {
    "evm": {
      "network": "Ethereum / EVM compatible (ETH, USDC, USDT, etc.)",
      "address": "0x1Ba5618Dc4a26e0495B089A569EFC64F9D2Ad689"
    },
    "sol": {
      "network": "Solana (SOL, USDC, etc.)",
      "address": "6KsvHjfHjW3UtqoFJcbdmy1byLDw99xrtV4ddwGu8qMk"
    }
  },
  "note": "All donations are voluntary and help fund continued development"
}

✅ GET /health
{
  "status": "healthy",
  "timestamp": "2026-02-15T04:05:11.829300",
  "dependencies": {
    "trust_score_api": "https://gerundium.sicmundus.dev/api/trust-score",
    "parent_agent": "gerundium@agentmail.to"
  }
}
```

---

## Next Steps to Complete Deployment:

### If using GitHub:
1. Push code to GitHub repository
2. Go to Render.com or Railway.app
3. Connect the repository and deploy
4. Get the production URL

### If NOT using GitHub:
1. Create a GitHub account and repository (free)
2. Push the code:
   ```bash
   cd /root/.openclaw/workspace
   git init
   git add projects/spawn-agent/trustverifier
   git commit -m "Add TrustVerifier API"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/trustverifier.git
   git push -u origin main
   ```
3. Follow Render.com or Railway.app steps above

---

## Production URL:
*After deployment, update here:*
- Render.com: `https://trustverifier-api.onrender.com`
- Railway.app: `https://trustverifier-api.up.railway.app`

---

## Environment Variables (Optional):

Set these in the hosting platform if needed:
- `TRUST_SCORE_API` - Default: `https://gerundium.sicmundus.dev/api/trust-score`
- `PARENT_AGENT_EMAIL` - Default: `gerundium@agentmail.to`
