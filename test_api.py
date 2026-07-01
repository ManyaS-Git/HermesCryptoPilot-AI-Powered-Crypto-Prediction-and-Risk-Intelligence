import sys
import os
import asyncio
from fastapi.testclient import TestClient

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.main import app, db_manager

# Initialize DB for tests if needed
async def setup():
    await db_manager.init_db()

asyncio.run(setup())

client = TestClient(app)

print("--- Testing /api/health-check ---")
resp = client.get("/api/health-check")
print(resp.status_code, resp.json())

print("--- Testing /api/predictions ---")
resp = client.get("/api/predictions")
print(resp.status_code, len(resp.json()), "predictions returned")

print("--- Testing /api/dashboard/stats ---")
resp = client.get("/api/dashboard/stats")
print(resp.status_code, resp.json())

print("--- Testing /api/portfolio ---")
resp = client.get("/api/portfolio")
print(resp.status_code, resp.json())

print("--- Testing /api/agents ---")
resp = client.get("/api/agents")
print(resp.status_code, len(resp.json()), "agents returned")
