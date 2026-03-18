from app.application.use_cases.handle_conversation import (
    HandleMessageUseCase, HandleMessageStreamUseCase, HandleThreadsUseCase
)
from app.application.use_cases.handle_document import (
    HandleDocumentsUseCase
)
from app.infrastructure.container import get_container

def get_handle_message_use_case() -> HandleMessageUseCase:
    return get_container().get_handle_message_use_case()

def get_handle_threads_use_case() -> HandleThreadsUseCase:
    return get_container().get_handle_threads_use_case()

def get_handle_message_stream_use_case() -> HandleMessageStreamUseCase:
    return get_container().get_handle_message_stream_use_case()

def get_handle_documents_use_case() -> HandleDocumentsUseCase:
    return get_container().get_handle_documents_use_case()
