from fastapi import APIRouter, UploadFile, File,Body
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse
import pandas as pd

router = APIRouter()
router.mount("/static", StaticFiles(directory="static"), name="static")

@router.get("/")
async def index():
    # Открываем файл index.html, который содержит JavaScript код
    with open("static/index.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content, status_code=200)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    # Делаем что-то с загруженным файлом, например, сохраняем его на сервере
    with open(f"uploaded_files/{file.filename}", "wb") as f:
        f.write(contents)
        data = pd.read_excel(f)
        # for i in range(len(data)):

    return {"filename": file.filename}

@router.post("/barcode")
async def barcode(value= Body()):
    print("Получено новое значение:", value)
    return {"message": "Значение обновлено"}