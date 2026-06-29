from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from app.agents.supervisor import SupervisorAgent
from app.telemetry.logger import setup_telemetry

logger = setup_telemetry(__name__)

app = FastAPI(title="Hermes Crypto Prediction API", description="API for monitoring and triggering the prediction agents.")

supervisor = SupervisorAgent()

class WorkflowRequest(BaseModel):
    asset: str

@app.post("/trigger-workflow")
async def trigger_workflow(request: WorkflowRequest, background_tasks: BackgroundTasks):
    """
    Triggers the supervisor workflow for a specific asset in the background.
    """
    logger.info(f"API request received to trigger workflow for {request.asset}")
    
    # We run it in the background so the API returns immediately
    background_tasks.add_task(supervisor.run_workflow, request.asset)
    
    return {"status": "Workflow triggered successfully", "asset": request.asset}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
