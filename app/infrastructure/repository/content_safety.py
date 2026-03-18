
from typing import Optional, List, Dict, Any, Tuple
from azure.ai.contentsafety.aio import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.contentsafety.models import AnalyzeTextOptions, TextCategory, AnalyzeTextResult
from app.domain.repository.content_safety_repository import IContentSafetyRepository
from app.domain.contants import DecisionAction

class ContentSafetyGuardilRepository(IContentSafetyRepository):
    def __init__(self, content_safety_client: ContentSafetyClient):
        self.content_safety_client = content_safety_client
    
    async def analyze_text(self, text: str, blocklist_names: Optional[List[str]] = [] ) -> Any:
        request = AnalyzeTextOptions(text=text, blocklist_names=blocklist_names)
        response = await self.content_safety_client.analyze_text(request)
        return response

    def valide_categories(self, response: AnalyzeTextResult, reject_thresholds: Dict[Any, int]) -> Tuple[bool, List[TextCategory]]:
        action_by_category = {}
        reject_decision = False

        for category, threshold in reject_thresholds.items():
            cat_result = next((c for c in response.categories_analysis if c.category == category), None)
            
            if cat_result and cat_result.severity >= threshold:
                action_by_category[category] = DecisionAction.REJECT.value
                reject_decision = reject_decision or True
            else:
                action_by_category[category] = DecisionAction.ACCEPT.value

        return reject_decision, action_by_category
    
    def validate_blocklists(self, response: AnalyzeTextResult) -> bool:
        if hasattr(response, 'blocklists_match') and response.blocklists_match:
            return True
        return False


    def make_decision(self, response: AnalyzeTextResult, reject_thresholds: Dict[Any, int]) -> Tuple[DecisionAction, List[TextCategory]]:
        reject_by_decision, action_by_category = self.valide_categories(response, reject_thresholds)
        reject_by_blocklists = self.validate_blocklists(response)

        final_action = DecisionAction.REJECT if reject_by_blocklists or reject_by_decision else DecisionAction.ACCEPT

        return final_action, action_by_category

        


