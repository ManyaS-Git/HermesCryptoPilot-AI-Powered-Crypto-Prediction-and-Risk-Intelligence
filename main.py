import asyncio
import sys
import os

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.storage import DatabaseManager
from app.agents.supervisor import SupervisorAgent
from app.telemetry.logger import setup_telemetry
import uvicorn

logger = setup_telemetry(__name__)

async def init_system():
    logger.info("Initializing system dependencies...")
    db_manager = DatabaseManager()
    await db_manager.init_db()

async def run_cli():
    """
    Runs the agent pipeline from the command line.
    """
    await init_system()
    supervisor = SupervisorAgent()
    
    assets = ["BTC", "ETH"]
    
    for asset in assets:
        await supervisor.run_workflow(asset)
        logger.info("-" * 40)

def run_api():
    """
    Runs the FastAPI server.
    """
    logger.info("Starting FastAPI server on port 8000")
    uvicorn.run("app.api.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        # Note: In a real environment, you'd want to call init_system() before starting uvicorn,
        # perhaps using FastAPI lifespan events.
        run_api()
    else:
        asyncio.run(run_cli())
