import os
import logging
import fitz
from PIL import Image
import io
from typing import Any, Dict, List, Optional, Union, Tuple
from uuid import uuid4, UUID
from datetime import datetime
from urllib.parse import urlparse
from app.domain.contants import MEDIA_FILE_MAPPER
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm 
from agent_framework import DataContent

logger = logging.getLogger(__name__)

def generate_uuid() -> UUID:
    return uuid4()

def filter_unnecesary_keys_from_dict(data: Dict[str, Any], valid_keys: List[str])-> Dict[str, Any]:
    return { f"{key}": data[key]  for key in data.keys() if key in valid_keys }

def replace_path_param(raw_value: str, mapper_value: Dict[str, str]) -> str:
    for key, value in mapper_value.items():
        raw_value = raw_value.replace(f"{{{key}}}", value)
    return raw_value

def get_or_create_uuid(session_id: Optional[Union[UUID, str]] =  None) -> UUID:
    if session_id is None:
        return generate_uuid()

    if isinstance(session_id, UUID):
        return session_id

    try:
        return UUID(session_id)
    except (ValueError, AttributeError):
        return generate_uuid()
    
def get_current_datetime() -> str:
    return datetime.now().isoformat()

def secuential_pdf_to_img(img_folder: str, source_pdf: str, dpi: Optional[int] = 150, format: Optional[str] = 'jpg'):

    os.makedirs(img_folder, exist_ok=True)

    pdf = fitz.open(source_pdf)
    
    for page_number in range(len(pdf)):
        pagina = pdf[page_number]
        
        zoom = dpi / 72
        matriz = fitz.Matrix(zoom, zoom)
        pixmap = pagina.get_pixmap(matrix=matriz)
        
        img_data = pixmap.tobytes("ppm")
        img = Image.open(io.BytesIO(img_data))
        
        file_name = f"page_{page_number + 1:03d}.{format}"
        ruta_completa = os.path.join(img_folder, file_name)
        
        if format.lower() in ["jpg", "jpeg"]:
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")
            img.save(ruta_completa, "JPEG", quality=95)
        else:
            img.save(ruta_completa, "PNG")
        
    pdf.close()

def page_pdf_to_img(
                source_pdf: str, page_number: str, output_directory: str,
                output_file_path: str, format: Optional[str] = 'jpg', dpi: Optional[int] = 150 
            ) -> Tuple[int, str]:
    os.makedirs(output_directory, exist_ok=True)
    pdf = fitz.open(source_pdf)
    pagina = pdf[page_number]
        
    zoom = dpi / 72
    matriz = fitz.Matrix(zoom, zoom)
    pixmap = pagina.get_pixmap(matrix=matriz)
    
    img_data = pixmap.tobytes("ppm")
    img = Image.open(io.BytesIO(img_data))
    
    if format.lower() in ["jpg", "jpeg"]:
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")
        img.save(output_file_path, "JPEG", quality=95)
    else:
        img.save(output_file_path, "PNG")
    
    pdf.close()
    return page_number, output_file_path


def parrallel_pdf_to_img(source_pdf: str, dpi: Optional[int] = 150, 
                         image_format: Optional[str] = 'jpg', max_workers:  Optional[int] = 40) -> List[str]:
    print(f"Source Pdf {source_pdf}")
    source_pdf_file = fitz.open(source_pdf)
    total_pages = len(source_pdf_file)
    file_name = source_pdf_file.name
    source_pdf_file.close()

    output_directory_name = f"images/{generate_uuid()}/{file_name}"

    result_process = []

    args_list = [
        (
            source_pdf, index, output_directory_name, 
            f"{output_directory_name}/page_{index}.{image_format}", image_format, dpi
        ) 
        for index in range(total_pages)
    ]
    
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [
                    executor.submit(page_pdf_to_img, *args) 
                    for args in args_list
                ]
        
        with tqdm(total=total_pages, desc="Converting pdf to images", unit="pag") as pbar:
            for future in as_completed(futures):
                result_process.append(future.result())
                pbar.update(1)

    result_process = [ result for _, result in sorted(result_process, key=lambda x: x[0]) ]

    return result_process

def get_metadata_from_uri(url: str) -> Dict[str, str]:

    parsed_url = urlparse(url)
    path = parsed_url.path

    _, extension = os.path.splitext(path)
    type_file = extension.replace('.', '')

    mapped_media_file = MEDIA_FILE_MAPPER.get(type_file, None)
    if not mapped_media_file:
        raise TypeError(f"Type file {type_file} not found")
    
    return {
        "uri": url,
        "media_type": mapped_media_file
    }

def get_class_name(current_class: Any):
    return type(current_class).__name__

def url_to_data_content(url: str, media_type: str) -> Any:
    import requests
    import base64
    print(f"La url {url}")
    response = requests.get(url)
    response.raise_for_status()
    
    base64_data = base64.b64encode(response.content).decode('utf-8')
    
    data_uri = f"data:{media_type};base64,{base64_data}"
    
    return DataContent(uri=data_uri)
    