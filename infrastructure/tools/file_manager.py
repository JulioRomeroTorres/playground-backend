from typing import Optional, Dict, Any
from pydantic import Field
from agent_framework import ai_function
from app.infrastructure.repository.presentation_manager import PptManager
from app.infrastructure.repository.word_manager import WordManager
from app.domain.utils import generate_uuid
from app.domain.repository.storage_repository import IStorageRepository
from app.domain.repository.file_document_repository import IFileDocumentRepository

MAPPER_FILE_MANAGER: Dict[str, IFileDocumentRepository] = {
    'pptx': PptManager,
    'docx': WordManager
}

@ai_function(
    name="Get_Template_Document", 
    description="""
        This function can get the template file from an external source or from 
        a user input reference document
        """
    )
async def get_template_document(user_query: str, 
                                reference_document: Optional[str] = Field(description="La URL o la ruta local exacta del archivo de plantilla de PowerPoint (.pptx). Ejemplo: 'https://example.com/plantilla.pptx' o 'data/plantillas/reporte.pptx'.", default=None)) -> str:
    if reference_document:
        return reference_document

@ai_function(
    name="Extract_Document_Structure", 
    description="""
        This function can get the json structure of the document, 
        it is neccesary to recreated and detect which params will be
        replaced because have some special keywords
        """
    )
async def extract_document_structure(
    type_document: str = Field(default='pptx',
                                examples=['pptx', 'docx'],
                                description="Tipo de documento a analizar. Para este agente, el valor siempre debe ser 'pptx'."), 
    document_reference: str = Field(description="La ruta del archivo o URL de la plantilla"),
    is_remote: bool = Field(description="Valor Booleano en donde se indica si el archivo es un documento local o una url, si es una URL este campo es True")
    ):

    file_document_manager = MAPPER_FILE_MANAGER[type_document](document_reference, is_remote)

    return file_document_manager.analize_placeholders()


class FillDocumentTool:
    def __init__(self, storage_respository: IStorageRepository):
        self.storage_respository = storage_respository
        pass

    @ai_function(
    name="Fill_Document", 
    description="""
        This function can recreted a new document in base of the 
        generated structure and upload to external source
        """
    )
    async def execute(
        self,
        type_document: str = Field(
            default='pptx',
            examples=['pptx', 'docx'],
            description="Tipo de documento a generar."), 
        fill_data: Dict[str, Any] = Field(
            description="""
            Un diccionario (JSON) que contiene los datos finales para rellenar en los placeholders.
            Debe seguir estas reglas de formato estrictas:
            - Para 'string': un valor de texto, si no se pudo encontrar informacion del campo, dejarlo como esta en la plantilla origial.
            - Para 'table': una lista de listas. La primera lista DEBE ser las cabeceras. Ejemplo: [["Header1", "Header2"], ["Dato1", "Dato2"]], si no se pudo encontrar informacion del campo, dejarlo como esta en la plantilla origial.
            - Para 'chart': un objeto JSON con 'categories' (una lista) y 'series' (una lista de objetos con 'name' y 'values'). Ejemplo: {"categories": ["A"], "series": [{"name": "S1", "values": [1]}]}, si no se pudo encontrar informacion del campo, dejarlo como esta en la plantilla origial.
            """
        ), 
        document_reference: str = Field(description="La ruta del archivo o URL de la plantilla original que se va a rellenar."),
        is_remote: bool = Field(description="Valor Booleano en donde se indica si el archivo es un documento local o una url, si es una URL este campo es True")
        ):

        file_document_manager: IFileDocumentRepository = MAPPER_FILE_MANAGER[type_document](document_reference, is_remote)

        output_file_path = f'tmp/{generate_uuid()}/output_2.{type_document}'
        file_document_manager.refill_document(fill_data, output_file_path)

        remote_document_url = await self.storage_respository.upload_many_files("ctnreu2aiasd02", [output_file_path])
        
        return f"Documento guardado en esta ruta localmente  {output_file_path} y remotamente en {remote_document_url[0]}"

@ai_function(
    name="Fill_Document", 
    description="""
        This function can recreted a new document in base of the 
        generated structure and upload to external source
        """
    )
async def fill_document(
        type_document: str = Field(
            default='pptx',
            examples=['pptx', 'docx'],
            description="Tipo de documento a generar."), 
        fill_data: Dict[str, Any] = Field(
            description="""
            Un diccionario (JSON) que contiene los datos finales para rellenar en los placeholders.
            Debe seguir estas reglas de formato estrictas:
            - Para 'string': un valor de texto, si no se pudo encontrar informacion del campo, dejarlo como esta en la plantilla origial.
            - Para 'table': una lista de listas. La primera lista DEBE ser las cabeceras. Ejemplo: [["Header1", "Header2"], ["Dato1", "Dato2"]], si no se pudo encontrar informacion del campo, dejarlo como esta en la plantilla origial.
            - Para 'chart': un objeto JSON con 'categories' (una lista) y 'series' (una lista de objetos con 'name' y 'values'). Ejemplo: {"categories": ["A"], "series": [{"name": "S1", "values": [1]}]}, si no se pudo encontrar informacion del campo, dejarlo como esta en la plantilla origial.
            """
        ), 
        document_reference: str = Field(description="La ruta del archivo o URL de la plantilla original que se va a rellenar."),
        is_remote: bool = Field(description="Valor Booleano en donde se indica si el archivo es un documento local o una url, si es una URL este campo es True")
        ):
    
    file_document_manager: IFileDocumentRepository = MAPPER_FILE_MANAGER[type_document](document_reference, is_remote)

    output_file_path = f'tmp/{generate_uuid()}/output_2.{type_document}'
    file_document_manager.refill_document(fill_data, output_file_path)
    
    return f"Documento guardado en esta ruta {output_file_path}"
