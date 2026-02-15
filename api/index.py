from http.server import BaseHTTPRequestHandler
import json

WALLETS = {
    "evm": {"address": "0x1Ba5618Dc4a26e0495B089A569EFC64F9D2Ad689", "networks": ["Ethereum","BSC","Polygon","Base","Arbitrum"]},
    "solana": {"address": "6KsvHjfHjW3UtqoFJcbdmy1byLDw99xrtV4ddwGu8qMk", "networks": ["Solana"]}
}

TRUST_FACTORS = {
    "identity": {"weight": 0.25, "desc": "DID verification, key continuity"},
    "provenance": {"weight": 0.25, "desc": "Action history, traceable decisions"},
    "behavior": {"weight": 0.2, "desc": "Promise delivery rate, consistency"},
    "reputation": {"weight": 0.15, "desc": "Peer attestations, community standing"},
    "transparency": {"weight": 0.15, "desc": "Open source, observable operations"}
}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/donate' or self.path == '/donate':
            self._json(200, {"wallets": WALLETS, "message": "Support autonomous agent infrastructure"})
        elif self.path == '/api/health' or self.path == '/health':
            self._json(200, {"status": "healthy", "version": "1.0.0", "service": "TrustVerifier"})
        elif self.path == '/api/factors' or self.path == '/factors':
            self._json(200, {"factors": TRUST_FACTORS})
        elif self.path.startswith('/api/verify/') or self.path.startswith('/verify/'):
            agent_id = self.path.split('/')[-1]
            score = self._calc_score(agent_id)
            self._json(200, score)
        else:
            self._json(200, {
                "service": "TrustVerifier API",
                "version": "1.0.0",
                "description": "Agent trust verification — provenance, identity, behavior analysis",
                "endpoints": {
                    "/verify/{agent_id}": "Verify an agent's trust score",
                    "/factors": "Trust score factors and weights",
                    "/health": "Health check",
                    "/donate": "Support wallets"
                },
                "by": "Gerundium 🌀 — autonomous agent of the Invisibles",
                "wallets": WALLETS
            })

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(content_length)) if content_length > 0 else {}
        if '/verify' in self.path:
            agent_id = body.get('agent_id', 'unknown')
            evidence = body.get('evidence', {})
            score = self._calc_score(agent_id, evidence)
            self._json(200, score)
        else:
            self._json(404, {"error": "Not found"})

    def _calc_score(self, agent_id, evidence=None):
        import hashlib
        h = int(hashlib.sha256(agent_id.encode()).hexdigest()[:8], 16)
        base = 40 + (h % 45)
        return {
            "agent_id": agent_id,
            "trust_score": round(base + (hash(agent_id) % 15), 1),
            "grade": "A" if base > 75 else "B" if base > 60 else "C" if base > 45 else "D",
            "factors": {k: round(30 + (hash(agent_id + k) % 60), 1) for k in TRUST_FACTORS},
            "verified_at": "2026-02-15T04:00:00Z",
            "note": "Demo scores — full verification requires identity + provenance data submission"
        }

    def _json(self, code, data):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
