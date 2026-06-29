from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.agents.supervisor import SupervisorAgent
from app.telemetry.logger import setup_telemetry
from app.services.storage import DatabaseManager
from fastapi.middleware.cors import CORSMiddleware

logger = setup_telemetry(__name__)

app = FastAPI(title="Hermes Crypto Prediction API", description="API for monitoring and triggering the prediction agents.")

# Enable CORS for the frontend dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

supervisor = SupervisorAgent()
db_manager = DatabaseManager()

class WorkflowRequest(BaseModel):
    asset: str

@app.post("/api/trigger-workflow")
async def trigger_workflow(request: WorkflowRequest, background_tasks: BackgroundTasks):
    """
    Triggers the supervisor workflow for a specific asset in the background.
    """
    logger.info(f"API request received to trigger workflow for {request.asset}")
    background_tasks.add_task(supervisor.run_workflow, request.asset)
    return {"status": "Workflow triggered successfully", "asset": request.asset}

@app.get("/api/health-check")
async def health_check():
    """System Health Check"""
    # In a real app, you would ping each service. Here we mock status for the dashboard.
    return {
        "status": "online",
        "services": {
            "backend": "online",
            "sqlite": "online",
            "openrouter": "online",
            "binance": "online",
            "polymarket": "online",
            "apify": "online"
        }
    }

@app.get("/api/predictions/latest")
async def get_latest_predictions():
    """Fetches the latest fused probabilities and kelly sizes."""
    query = '''
        SELECT * FROM position_recommendations 
        ORDER BY timestamp DESC 
        LIMIT 2
    '''
    try:
        results = await db_manager.execute_query(query)
        return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Error fetching latest predictions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/predictions/history")
async def get_prediction_history(asset: str, limit: int = 20):
    """Fetches past predictions (last N for sparklines)."""
    query = '''
        SELECT timestamp, signal_direction, fused_probability 
        FROM position_recommendations 
        WHERE asset = ? 
        ORDER BY timestamp ASC 
        LIMIT ?
    '''
    try:
        results = await db_manager.execute_query(query, (asset, limit))
        return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Error fetching prediction history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/metrics")
async def get_metrics():
    """Fetches global Brier scores, accuracy, win rate, etc."""
    query = '''
        SELECT * FROM evaluation_metrics 
        ORDER BY timestamp DESC 
        LIMIT 10
    '''
    try:
        results = await db_manager.execute_query(query)
        if not results:
            # Return mock data if db is empty for demonstration purposes
            return {
                "accuracy": 0.71,
                "win_rate": 0.68,
                "brier_score": 0.18
            }
        return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/markets")
async def get_markets(asset: str):
    """Fetches Polymarket/Kalshi odds."""
    query = '''
        SELECT * FROM market_odds 
        WHERE asset = ?
        ORDER BY timestamp DESC 
        LIMIT 10
    '''
    try:
        results = await db_manager.execute_query(query, (asset,))
        if not results:
            # Return mock odds for demonstration if DB is empty (since we aren't saving them yet)
            return [
                {"source": "Polymarket", "implied_probability": 0.55, "odds": 1.81},
                {"source": "Kalshi", "implied_probability": 0.52, "odds": 1.92}
            ]
        return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Error fetching market odds: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/runs")
async def get_agent_runs():
    """Returns structured data from agent_runs."""
    query = '''
        SELECT * FROM agent_runs 
        ORDER BY timestamp DESC 
        LIMIT 20
    '''
    try:
        results = await db_manager.execute_query(query)
        if not results:
            # Mock runs if empty
            return [
                {"timestamp": "2026-06-29T12:00:00Z", "agent_name": "PredictionAgent", "status": "completed", "execution_time_ms": 123, "error_message": None, "message": "Prediction completed for BTC"},
                {"timestamp": "2026-06-29T12:00:05Z", "agent_name": "RiskAgent", "status": "completed", "execution_time_ms": 45, "error_message": None, "message": "Calculated Kelly size"}
            ]
        return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Error fetching agent runs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
