import asyncio
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Body, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse
from models.Visitors import Visitors, Devices,Users,Template,TemplateResponse,PrinterRespone,PrinterService
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String
import pandas as pd
from api import deps
import aiofiles as aiofiles
import datetime
import os
from pandas import DataFrame
from sqlalchemy.ext.declarative import declarative_base
from fastapi.templating import Jinja2Templates
import requests
import json
from decouple import config
from requests.exceptions import ConnectionError

UPLOAD = config('UPLOAD_DIR', default='./uploaded_files')
SRC_DATA_BASE = config('SRC_DATA_BASE', default='./src/checktickets.db')

router = APIRouter()
now = datetime.datetime.now()

@router.get("/getmyip")
async def get_my_ip(request: Request):
    client_host = request.client.host
    return {"client_host": client_host}

@router.post("/upload")
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

@router.post("/template")
async def template(data:TemplateResponse,db: Session = Depends(deps.get_db)):
    try:
        template = Template(templ_data = data.label,templ_name = data.name,is_default = data.is_default)
        db.add(template)
        db.commit()
        db.close()
        return JSONResponse(status_code=200, content={'status': 'Success'})
    except:
        return JSONResponse(status_code=500, content={'status': 'Error'})

@router.post("/printer")
async def printer(data:PrinterRespone,db: Session = Depends(deps.get_db)):
    try:
        printer = PrinterService(print_name = data.name,url = data.url,is_default = data.is_default,
                                 port = data.port,type = data.type)
        db.add(printer)
        db.commit()
        db.close()
        return JSONResponse(status_code=200, content={'status': 'Success'})
    except:
        return JSONResponse(status_code=500, content={'status': 'Error'})

@router.get("/clear_db")
async def clear(db: Session = Depends(deps.get_db)):
    db.query(Visitors).delete()
    db.commit()
    return JSONResponse(status_code=200, content={'status': 'Success'})


@router.get("/barcode")
async def barcode(code,re:Request, db: Session = Depends(deps.get_db)):
    visitor_temp = db.query(Visitors).filter(Visitors.regQR == str(code)).all()
    return visitor_temp


@router.get("/search")
async def search(surname, db: Session = Depends(deps.get_db)):
    visitor_temp = db.query(Visitors).filter(Visitors.surname.like(f"%{surname}%")).all()

    return visitor_temp


@router.get("/register")
async def register(surname, name, organization, position, db: Session = Depends(deps.get_db)):
    visitor = Visitors(surname=str(surname), name=str(name), organization=str(organization), position=str(position),
                       is_check=0, is_print=0, is_manual=1)
    db.add(visitor)
    db.commit()
    visitor_temp = db.query(Visitors).filter(Visitors.surname == str(surname), Visitors.name == str(name),
                                             Visitors.organization == str(organization),
                                             Visitors.position == str(position)).first()
    return visitor_temp


# @router.get("/print")
# async def prints(id,re:Request, db: Session = Depends(deps.get_db)):
#     print('Is connected from:')
#     print(re.client.host)
#     visitor_temp = db.query(Visitors).filter(Visitors.id == int(id)).first()
#
#     visitor_temp.check_in = datetime.datetime.now().strftime('%y-%m-%d-%H-%M')
#     visitor_temp.is_check = 1
#
#     printer = db.query(PrinterService).filter(PrinterService.is_default == 1).all()
#     if printer != None:
#         for i in range(len(printer)):
#             if printer[i].type == 2:
#                 try:
#                     r0 = requests.get(printer[i].url +':'+ str(printer[i].port) + '/api/v1/connect/printer?code=1',headers={},data={})
#                     print(printer[i].url + str(printer[i].port) + '/api/v1/connect/printer?code=1')
#                     print(r0.status_code)
#                     if r0.status_code == 200:
#                         printer[i].is_online = 1
#                         db.commit()
#                         st1 = str(visitor_temp.organization)
#                         if visitor_temp.regQR != None:
#                             st2 = str(visitor_temp.regQR)
#                         else:
#                             st2 = str(5000 + visitor_temp.id)
#                         dict_new = {
#                             "document": {
#                                 "name": "documents",
#                                 "protocol": "atolmsk",
#                                 "details": [
#                                     {
#                                         "type": "task",
#                                         "code": str(visitor_temp.id) + str(visitor_temp.is_print),
#                                         "count": "2",
#                                         "values": [
#                                             {
#                                                 "id": "Surnam",
#                                                 "data": str(visitor_temp.surname)
#                                             },
#                                             {
#                                                 "id": "Name",
#                                                 "data": str(visitor_temp.name)
#                                             },
#                                             {
#                                                 "id": "org",
#                                                 "data": str(visitor_temp.organization)
#                                             },
#                                             {
#                                                 "id": "Barcode",
#                                                 "data": st2
#                                             },
#                                             {
#                                                 "id": "City",
#                                                 "data": str(visitor_temp.position)
#                                             }
#                                         ]
#                                     }
#                                 ]
#                             }
#                         }
#                         payload = {'Content-Type': 'application/json'}
#                         print(json.dumps(dict_new))
#                         r1 = requests.post(
#                             printer[i].url +':'+ str(printer[i].port)+"/api/v1/add/task?code=" + str(visitor_temp.id) + str(visitor_temp.is_print),
#                             data=json.dumps(dict_new), headers=payload)
#                         if r1.status_code == 200:
#                             visitor_temp.is_print = visitor_temp.is_print + 1
#                             visitor_temp.check_status = 'Зарегистрирован'
#                             db.commit()
#                             i = len(printer)
#                             db.close()
#                             return JSONResponse(status_code=200, content={'status': 'Success'})
#                         else:
#                             return JSONResponse(status_code=500, content={'status': 'Error'})
#                 except ConnectionError:
#                     printer[i].is_online = 0
#                     db.commit()
# @router.get("/device")
# async def devices(ip4:str,is_connected:bool| None=None,printer_id: Optional[int] = None,
#                   label_id: Optional[int] = None,db: Session = Depends(deps.get_db())):
#
#     if ip4 and db.query(Devices).filter(Devices.ip == ip4).first() is not None:
#         device_temp = db.query(Devices).filter(Devices.ip == ip4).first()
#         if printer_id is not None:
#             device_temp.printer_id = printer_id
#         if label_id is not None:
#             device_temp.label_id = label_id
#         if is_connected is not None:
#             device_temp.is_connected = is_connected
#         db.commit()
#         db.refresh(device_temp)
#     else:
#         device_temp = Devices(ip = ip4,is_connected=is_connected,printer_id=printer_id,label_id=label_id)
#         db.add(device_temp)
#         db.commit()
#         db.refresh(device_temp)
#     return

@router.get("/print")
async def prints(id,re:Request, db: Session = Depends(deps.get_db)):
    print('Is connected from:')
    print(re.client.host)
    visitor_temp = db.query(Visitors).filter(Visitors.id == int(id)).first()

    visitor_temp.check_in = datetime.datetime.now().strftime('%y-%m-%d-%H-%M')
    visitor_temp.is_check = 1

    printer = db.query(PrinterService).filter(PrinterService.url == str('http://'+ str(re.client.host))).first()
    if printer == None:
        printer = db.query(PrinterService).filter(PrinterService.is_default== 1).first()
    print(printer.url)
    if printer != None:
        try:
            # проверка, что сервис доступен
            r0 = requests.get(printer.url + ':' + str(printer.port) + '/api/v1/connect/printer?code=1',
                              headers={}, data={})
            print(printer.url +':'+ str(printer.port) + '/api/v1/connect/printer?code=1')
            print(r0.status_code)
            if r0.status_code == 200:
                printer.is_online = 1
                db.commit()
                st1 = str(visitor_temp.organization)
                if visitor_temp.regQR != None:
                    st2 = str(visitor_temp.regQR)
                else:
                    st2 = str(5000 + visitor_temp.id)
                dict_new = {
                    "document": {
                        "name": "documents",
                        "protocol": "atolmsk",
                        "details": [
                            {
                                "type": "task",
                                "code": str(visitor_temp.id) + str(visitor_temp.is_print),
                                "count": "2",
                                "values": [
                                    {
                                        "id": "Surnam",
                                        "data": str(visitor_temp.surname)
                                    },
                                    {
                                        "id": "Name",
                                        "data": str(visitor_temp.name)
                                    },
                                    {
                                        "id": "org",
                                        "data": str(visitor_temp.organization)
                                    },
                                    {
                                        "id": "Barcode",
                                        "data": st2
                                    },
                                    {
                                        "id": "City",
                                        "data": str(visitor_temp.position)
                                    }
                                ]
                            }
                        ]
                    }
                }
                payload = {'Content-Type': 'application/json'}
                print(json.dumps(dict_new))
                r1 = requests.post(
                    printer.url + ':' + str(printer.port) + "/api/v1/add/task?code=" + str(visitor_temp.id) + str(
                        visitor_temp.is_print),
                    data=json.dumps(dict_new), headers=payload)
                if r1.status_code == 200:
                    visitor_temp.is_print = visitor_temp.is_print + 1
                    visitor_temp.check_status = 'Зарегистрирован'
                    db.commit()
                    db.close()
                    return JSONResponse(status_code=200, content={'status': 'Success'})
                else:
                    return JSONResponse(status_code=500, content={'status': 'Error'})
        except ConnectionError:
            print('IS not Connect')

@router.get("/prints")
async def prints_pack(value_1:int,value_2:int,sleep:float,re:Request, db: Session = Depends(deps.get_db)):
    print('/prints')
    for ii in range(value_2-value_1+1):
        await asyncio.sleep(sleep)
        id = value_1 +ii
        print(datetime.datetime.now().strftime('%y-%m-%d-%H-%M'))
        print('id: ' + str(id))
        visitor_temp = db.query(Visitors).filter(Visitors.id == int(id)).first()
        print('Surname: ' + str(visitor_temp.surname))
        visitor_temp.check_in = datetime.datetime.now().strftime('%y-%m-%d-%H-%M')
        visitor_temp.is_check = 1
        db.commit()
        db.refresh(visitor_temp)


        printer = db.query(PrinterService).filter(PrinterService.is_default == 1).all()
        if printer != None:
            for i in range(len(printer)):
                if printer[i].type == 2:
                    try:
                        r0 = requests.get(
                            printer[i].url + ':' + str(printer[i].port) + '/api/v1/connect/printer?code=1', headers={},
                            data={})
                        print(printer[i].url + ':'+ str(printer[i].port) + '/api/v1/connect/printer?code=1')
                        print(r0.status_code)
                        if r0.status_code == 200:
                            printer[i].is_online = 1
                            db.commit()
                            st1 = str(visitor_temp.organization)
                            if visitor_temp.regQR != None:
                                st2 = str(visitor_temp.regQR)
                            else:
                                st2 = str(5000 + visitor_temp.id)
                            # dict_new = {
                            #     "document": {
                            #         "name": "documents",
                            #         "protocol": "atolmsk",
                            #         "details": [
                            #             {
                            #                 "type": "task",
                            #                 "code": str(visitor_temp.id) + str(visitor_temp.is_print),
                            #                 "count": "2",
                            #                 "values": [
                            #                     {
                            #                         "id": "Surnam",
                            #                         "data": str(visitor_temp.surname)
                            #                     },
                            #                     {
                            #                         "id": "Name",
                            #                         "data": str(visitor_temp.name)
                            #                     },
                            #                     {
                            #                         "id": "org",
                            #                         "data": str(visitor_temp.organization)
                            #                     },
                            #                     {
                            #                         "id": "Barcode",
                            #                         "data":st2
                            #                     },
                            #                     {
                            #                         "id": "City",
                            #                         "data":str(visitor_temp.position)
                            #                     }
                            #                 ]
                            #             }
                            #         ]
                            #     }
                            # }

                            dict_new = {
                                "document": {
                                    "name": "documents",
                                    "protocol": "atolmsk",
                                    "details": [
                                        {
                                            "type": "task",
                                            "code": str(visitor_temp.id) + str(visitor_temp.is_print),
                                            "count": "2",
                                            "values": [
                                                {
                                                    "id": "Surnam",
                                                    "data": str(visitor_temp.surname)
                                                },
                                                {
                                                    "id": "Name",
                                                    "data": str(visitor_temp.name)
                                                },
                                                {
                                                    "id": "City",
                                                    "data": str(visitor_temp.position)
                                                },
                                                {
                                                    "id": "Org",
                                                    "data": str(visitor_temp.organization)
                                                }
                                            ]
                                        }
                                    ]
                                }
                            }

                            payload = {'Content-Type': 'application/json'}
                            r1 = requests.post(
                                printer[i].url + ':' + str(printer[i].port) + "/api/v1/add/task?code=" + str(
                                    visitor_temp.id) + str(visitor_temp.is_print),
                                data=json.dumps(dict_new), headers=payload)
                            if r1.status_code == 200:
                                visitor_temp.is_print = visitor_temp.is_print + 1
                                visitor_temp.check_status = 'Зарегистрирован'
                                db.commit()
                                i = len(printer)
                                db.close()
                            else:
                                return JSONResponse(status_code=500, content={'status': f'Error {visitor_temp.id}'})
                    except ConnectionError:
                        printer[i].is_online = 0
                        db.commit()

@router.get("/visitors")
async def visitors(db: Session = Depends(deps.get_db)):
    return db.query(Visitors).all()

