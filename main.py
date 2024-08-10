from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Request, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
import models, database
from database import engine, get_db
from fastapi.responses import StreamingResponse
import io
import uuid

app = FastAPI()


# Modelsni yaratish
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


@app.post("/upload_pdf/")
async def upload_pdf(request: Request, name: str = Form(...), file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    content = await file.read()

    result = await db.execute(select(models.PDFFile).where(models.PDFFile.name == name))
    existing_file = result.scalars().first()
    if existing_file:
        name = f"{name}_{uuid.uuid4().hex}"

    db_pdf = models.PDFFile(name=name, content=content)
    db.add(db_pdf)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Failed to save the PDF file. Please try again.")

    await db.refresh(db_pdf)
    file_url = f"{request.url.scheme}://{request.client.host}:{request.url.port}/get_pdf/{db_pdf.id}"
    return {"file_url": file_url}


@app.get("/get_pdf/{pdf_id}")
async def get_pdf(pdf_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.PDFFile).where(models.PDFFile.id == pdf_id))
    db_pdf = result.scalars().first()
    if db_pdf is None:
        raise HTTPException(status_code=404, detail="PDF file not found")
    return StreamingResponse(io.BytesIO(db_pdf.content), media_type="application/pdf")
