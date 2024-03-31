from fastapi import APIRouter, UploadFile, File, Depends, Request
from fastapi.responses import JSONResponse
from models.Visitors import Visitors, Devices,Template,TemplateResponse,PrinterRespone,PrinterService,DeviceResponse
from sqlalchemy.orm import Session
import pandas as pd
from api import deps
import aiofiles as aiofiles
import datetime
import os
from decouple import config

UPLOAD = config('UPLOAD_DIR', default='./uploaded_files')
SRC_DATA_BASE = config('SRC_DATA_BASE', default='./src/checktickets.db')
LIMIT_ACCESS = config('LIMIT_ACCESS',default = 0)
CHECK_PRINTER_TYPE2= config('CHECK_PRINTER_TYPE2',default='/api/v1/connect/printer?code=1')
START_NUM = config('START_NUM',default=5000)
ADD_TASK_TYPE2=config('ADD_TASK_TYPE2',default="/api/v1/add/task?code=")

router = APIRouter()
now = datetime.datetime.now()

@router.get("/getmyip", summary="Получить IP4 подключенного устройства",
             description="Реализуем регистрацию устройства")
async def get_my_ip(request: Request):
    client_host = request.client.host
    return {"client_host": client_host}

@router.post("/upload", summary="Загрузка файла с данными для регистрации в БД",
             description="Загружаем excel заданного формата")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(deps.get_db)):
    if 5 == 5:
        # Делаем что-то с загруженным файлом, например, сохраняем его на сервере
        async with aiofiles.open(os.path.join(UPLOAD, file.filename), 'wb') as out_file:
            content = await file.read()  # async read
            await out_file.write(content)
        df = pd.read_excel(os.path.join(UPLOAD, file.filename), engine='openpyxl')
        data = df.to_dict(orient='index')
        for row in data:
            visitor = Visitors(surname=data[row]['Surname'], name=data[row]['Name'],
                               organization=data[row]['Organization'], position=data[row]['Position'],
                               regQR=str(data[row]['RegQR']),is_check=0, is_print=0,
                               check_status = 'На регистрации',is_manual=0)
            db.add(visitor)
            db.commit()
            if 'LabelName' in data[row]:
                visitor.templ_name = data[row]['LabelName']
            db.commit()
        db.close()
        return {"filename": file.filename}

@router.post("/template", summary="Загружаем шаблон этикетки",
             description="Этикетка ZPL")
async def template(data:TemplateResponse,db: Session = Depends(deps.get_db)):
    try:
        template = Template(templ_data = data.label,templ_name = data.name,is_default = data.is_default,is_deleted = 0)
        db.add(template)
        db.commit()
        db.close()
        return JSONResponse(status_code=200, content={'status': 'Success'})
    except:
        return JSONResponse(status_code=500, content={'status': 'Error'})

@router.post("/printer", summary="Добавляем принтер в БД",
             description="Отправка на сервер файла конфигурации ")
async def printer(data:PrinterRespone,db: Session = Depends(deps.get_db)):
    try:
        printer = PrinterService(print_name = data.name,url = data.url,is_default = data.is_default,
                                 port = data.port,type = data.type,is_deleted = 0)
        db.add(printer)
        db.commit()
        db.close()
        return JSONResponse(status_code=200, content={'status': 'Success'})
    except:
        return JSONResponse(status_code=500, content={'status': 'Error'})

@router.post("/device", summary="Определяем устройство -> принтер",
             description="Реализуем печать на определенный принтер")
async def devices(data:DeviceResponse,db: Session = Depends(deps.get_db)):
    if 'ip4' in data:
        try:
            if db.query(Devices).filter(Devices.ip == data.ip4).first() is not None:
                device_temp = db.query(Devices).filter(Devices.ip == data.ip4).first()
                if 'printer_id' in data:
                    device_temp.printer_id = data.printer_id
                if 'label_id' in data:
                    device_temp.label_id = data.label_id
                if 'is_connected' in data:
                    device_temp.is_connected = data.is_connected
                db.commit()
                db.refresh(device_temp)
            else:
                device_temp = Devices(ip = data.ip4,is_connected=data.is_connected,printer_id=data.printer_id,label_id=data.label_id,is_deleted = 0)
                db.add(device_temp)
                db.commit()
                db.refresh(device_temp)
            return JSONResponse(status_code=200, content={'status': f'Success {device_temp.id}'})
        except:
            return JSONResponse(status_code=500, content={'status': 'DB error'})

    else:
        return JSONResponse(status_code=500, content={'status': f'No IP4'})

@router.get("/clear_db", summary="Очистка БД с данными",
             description="Очищаем таблицу с участниками для регистрации")
async def clear(db: Session = Depends(deps.get_db)):
    db.query(Visitors).delete()
    db.commit()
    return JSONResponse(status_code=200, content={'status': 'Success'})

