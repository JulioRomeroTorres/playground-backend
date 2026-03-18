import logging
from typing import Any
from app.domain.orchestrator import Orchestrator

logger = logging.getLogger(__name__)

class WorkflowOrchestrator(Orchestrator):
    def __init__(self, 
                 conversation_manager: Any,
                 db_client: Any
                 ):
        
        logger.info("Initializing Workflow Orchestrator")
        self.conversation_manager = conversation_manager
        self.db_client = db_client
        logger.info("Workflow Orchestrator initialized successfully with conditional routing")