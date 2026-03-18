from typing import Optional, List, Dict, Any, Tuple
from azure.ai.contentsafety.models import TextCategory, AnalyzeTextResult
from app.domain.contants import DecisionAction

class IContentSafetyRepository:
    async def analyze_text(self, text: str, blocklist_names: Optional[List[str]] = [] ) -> None:
        pass

    def valide_categories(self, response: AnalyzeTextResult, reject_thresholds: Dict[Any, int]) -> Tuple[bool, List[TextCategory]]:
        pass
    
    def validate_blocklists(self, response: AnalyzeTextResult) -> bool:
        pass


    def make_decision(self, response: AnalyzeTextResult, reject_thresholds: Dict[Any, int]) -> Tuple[DecisionAction, List[TextCategory]]:
        pass