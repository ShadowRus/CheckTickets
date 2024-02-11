from fastapi import APIRouter, UploadFile, File,Body,Depends
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse
from models.Visitors import Visitors,Users
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String
import pandas as pd
from api import deps
import aiofiles as aiofiles
import os
from pandas import DataFrame
from sqlalchemy.ext.declarative import declarative_base

router = APIRouter()
router.mount("/static", StaticFiles(directory="static"), name="static")

@router.get("/")
async def index():
    # Открываем файл index.html, который содержит JavaScript код
    with open("static/index.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content, status_code=200)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...),db: Session = Depends(deps.get_db)):
    # Делаем что-то с загруженным файлом, например, сохраняем его на сервере
    async with aiofiles.open(f"uploaded_files/{file.filename}", 'wb') as out_file:
        content = await file.read()  # async read
        await out_file.write(content)

    df = pd.read_excel(f"uploaded_files/{file.filename}",engine='openpyxl')
    print(df)
    df.to_dict(orient='index')
    for row
    db.close()
    return {"filename": file.filename}

@router.post("/barcode")
async def barcode(value= Body()):
    print("Получено новое значение:", value)
    return {"message": "Значение обновлено"}