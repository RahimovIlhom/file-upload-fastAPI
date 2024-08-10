from sqlalchemy import Column, Integer, String, LargeBinary
from database import Base


class PDFFile(Base):
    __tablename__ = "pdf_files"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    content = Column(LargeBinary)
