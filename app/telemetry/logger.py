import logging
import sys
import json
from datetime import datetime
from app.config.settings import get_settings

settings = get_settings()

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        
        # Add extra fields if they exist
        if hasattr(record, "extra_info"):
            log_record.update(record.extra_info)
            
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

def setup_telemetry(name: str) -> logging.Logger:
    """Configures structured JSON logging for telemetry and observability."""
    logger = logging.getLogger(name)
    
    # Only configure if no handlers are set to avoid duplicates
    if not logger.handlers:
        logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        
        logger.addHandler(handler)
        
    return logger
