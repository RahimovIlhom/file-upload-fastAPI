from pydantic import BaseModel


class PDFFileCreate(BaseModel):
    name: str
    content: bytes
