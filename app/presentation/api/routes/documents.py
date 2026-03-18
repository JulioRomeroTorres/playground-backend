import logging
from typing import Annotated
from fastapi import APIRouter, UploadFile, File, Form

from starlette.responses import JSONResponse

from app.presentation.api.dependencies import (
    get_handle_documents_use_case,

)
from app.presentation.api.dto import (
    UploadedDocumentResponse
)

logger = logging.getLogger(__name__)

BASE_PATH = "/api/v1/documents"

router = APIRouter(
    prefix=BASE_PATH
)

@router.post("/")
async def upload_document(
    file: UploadFile = File(...),
    username: Annotated[str, Form()] = "anonymous",
    description: Annotated[str | None, Form()] = None
    ):

    handle_document = get_handle_documents_use_case()

    pdf_images_files = await handle_document.upload_document(file)

    uploaded_document = UploadedDocumentResponse(
        generated_img_files=pdf_images_files,
        file_name=file.filename
    )
    
    return JSONResponse(uploaded_document.model_dump(), headers={"status_code": "200"})

@router.post("/documents/index/")
async def upload_document(
    file: UploadFile = File(...),
    username: Annotated[str, Form()] = "anonymous"
    ):

    handle_document = get_handle_documents_use_case()

    pdf_images_files = await handle_document.index_document(file)

    uploaded_document = UploadedDocumentResponse(
        generated_img_files=pdf_images_files,
        file_name=file.filename
    )
    
    return JSONResponse(uploaded_document.model_dump(), headers={"status_code": "200"})

    
