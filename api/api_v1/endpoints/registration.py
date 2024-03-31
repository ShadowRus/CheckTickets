import asyncio
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from models.Visitors import Visitors, Devices,PrinterService
from models.vizitor_params import visitor_data_type2
from sqlalchemy.orm import Session
from sqlalchemy import desc
from api import deps
import datetime
import requests
import json
from decouple import config
from requests.exceptions import ConnectionError

UPLOAD = config('UPLOAD_DIR', default='./uploaded_files')
SRC_DATA_BASE = config('SRC_DATA_BASE', default='./src/checktickets.db')
LIMIT_ACCESS = config('LIMIT_ACCESS',default = 0)
CHECK_PRINTER_TYPE2= config('CHECK_PRINTER_TYPE2',default='/api/v1/connect/printer?code=1')
START_NUM = config('START_NUM',default=5000)
ADD_TASK_TYPE2=config('ADD_TASK_TYPE2',default="/api/v1/add/task?code=")

router = APIRouter()
now = datetime.datetime.now()

@router.get("/barcode",summary="Поиск по коду",
             description="Ищет участника с QR-кодом")
async def barcode(code, db: Session = Depends(deps.get_db)):
    visitor_temp = db.query(Visitors).filter(Visitors.regQR == str(code)).all()
    return visitor_temp


@router.get("/search", summary="Поиск по фамилии участника",
             description="Ищет похожие совпадения")
async def search(surname, db: Session = Depends(deps.get_db)):
    visitor_temp = db.query(Visitors).filter(Visitors.surname.like(f"%{surname}%")).all()

    return visitor_temp


@router.get("/register", summary="Регистрация нового участника",
             description="Добавляем в таблицу нового участника, ставим тэг is_manual = 1")
async def register(surname, name, organization, position, db: Session = Depends(deps.get_db)):
    visitor = Visitors(surname=str(surname), name=str(name), organization=str(organization), position=str(position),
                       is_check=0, is_print=0, is_manual=1)
    db.add(visitor)
    db.commit()
    visitor_temp = db.query(Visitors).filter(Visitors.surname == str(surname), Visitors.name == str(name),
                                             Visitors.organization == str(organization),
                                             Visitors.position == str(position)).first()
    return visitor_temp


@router.get("/print", summary="Печать бейджа по id",
             description="Печать бейджа по id  участника")
async def prints(id,re:Request, db: Session = Depends(deps.get_db)):
    if LIMIT_ACCESS == 1:
        device_temp = db.query(Devices).filter(Devices.ip == str(re.client.host),Devices.is_deleted == 0).first()
        if device_temp == None:
            return JSONResponse(status_code=500, content={'status': 'Access Denied'})
    device_temp = db.query(Devices).filter(Devices.ip == str(re.client.host), Devices.is_connected == 1,Devices.is_deleted == 0).first()
    # если заранее указано на какой принтер посылать данные с устройства, то выбираем его
    if device_temp != None:
        printer = db.query(PrinterService).filter(PrinterService.id == device_temp.printer_id,PrinterService.is_deleted == 0).all()
    else:
    # если не указано соответствие устройство-принтер, то отправляем на принтеры по умолчанию
        printer = db.query(PrinterService).filter(PrinterService.is_default == 1, PrinterService.is_deleted == 0).order_by(
            desc(PrinterService.is_online)).all()

    visitor_temp = db.query(Visitors).filter(Visitors.id == int(id)).first()
    visitor_temp.check_in = datetime.datetime.now().strftime('%y-%m-%d-%H-%M')
    visitor_temp.is_check = 1

    if printer != None:
        for i in range(len(printer)):
            if printer[i].type == 2:
                try:
                    r0 = requests.get(printer[i].url +':'+ str(printer[i].port) + str(CHECK_PRINTER_TYPE2),headers={},data={})
                    print(printer[i].url + str(printer[i].port) + CHECK_PRINTER_TYPE2)
                    print(r0.status_code)
                    if r0.status_code == 200:
                        printer[i].is_online = 1
                        db.commit()
                        if visitor_temp.regQR != None:
                            st2 = str(visitor_temp.regQR)
                        else:
                            st2 = str(START_NUM + visitor_temp.id)
                            dict_new = visitor_data_type2(str(visitor_temp.id) + str(visitor_temp.is_print),
                                                          str(visitor_temp.surname), str(visitor_temp.name),
                                                          str(visitor_temp.organization), st2,
                                                          str(visitor_temp.position))
                        payload = {'Content-Type': 'application/json'}
                        print(json.dumps(dict_new))
                        r1 = requests.post(
                            printer[i].url +':'+ str(printer[i].port)+str(ADD_TASK_TYPE2) + str(visitor_temp.id) + str(visitor_temp.is_print),
                            data=json.dumps(dict_new), headers=payload)
                        if r1.status_code == 200:
                            visitor_temp.is_print = visitor_temp.is_print + 1
                            visitor_temp.check_status = 'Зарегистрирован'
                            db.commit()
                            i = len(printer)
                            db.close()
                            return JSONResponse(status_code=200, content={'status': 'Success'})
                        else:
                            return JSONResponse(status_code=500, content={'status': 'Error'})
                except ConnectionError:
                    printer[i].is_online = 0
                    db.commit()
            # if printer[i].type == 1:
            #     try:
            #         a=4
            #     except ConnectionError:
            #         printer[i].is_online=0
            #         db.commit()
            #     return

# @router.get("/print")
# async def prints(id,re:Request, db: Session = Depends(deps.get_db)):
#     print('Is connected from:')
#     print(re.client.host)
#     visitor_temp = db.query(Visitors).filter(Visitors.id == int(id)).first()
#
#     visitor_temp.check_in = datetime.datetime.now().strftime('%y-%m-%d-%H-%M')
#     visitor_temp.is_check = 1
#
#     printer = db.query(PrinterService).filter(PrinterService.url == str('http://'+ str(re.client.host))).first()
#     if printer == None:
#         printer = db.query(PrinterService).filter(PrinterService.is_default== 1).first()
#     print(printer.url)
#     if printer != None:
#         try:
#             # проверка, что сервис доступен
#             r0 = requests.get(printer.url + ':' + str(printer.port) + '/api/v1/connect/printer?code=1',
#                               headers={}, data={})
#             print(printer.url +':'+ str(printer.port) + '/api/v1/connect/printer?code=1')
#             print(r0.status_code)
#             if r0.status_code == 200:
#                 printer.is_online = 1
#                 db.commit()
#                 st1 = str(visitor_temp.organization)
#                 if visitor_temp.regQR != None:
#                     st2 = str(visitor_temp.regQR)
#                 else:
#                     st2 = str(5000 + visitor_temp.id)
#                 dict_new = {
#                     "document": {
#                         "name": "documents",
#                         "protocol": "atolmsk",
#                         "details": [
#                             {
#                                 "type": "task",
#                                 "code": str(visitor_temp.id) + str(visitor_temp.is_print),
#                                 "count": "2",
#                                 "values": [
#                                     {
#                                         "id": "Surnam",
#                                         "data": str(visitor_temp.surname)
#                                     },
#                                     {
#                                         "id": "Name",
#                                         "data": str(visitor_temp.name)
#                                     },
#                                     {
#                                         "id": "org",
#                                         "data": str(visitor_temp.organization)
#                                     },
#                                     {
#                                         "id": "Barcode",
#                                         "data": st2
#                                     },
#                                     {
#                                         "id": "City",
#                                         "data": str(visitor_temp.position)
#                                     }
#                                 ]
#                             }
#                         ]
#                     }
#                 }
#                 payload = {'Content-Type': 'application/json'}
#                 print(json.dumps(dict_new))
#                 r1 = requests.post(
#                     printer.url + ':' + str(printer.port) + "/api/v1/add/task?code=" + str(visitor_temp.id) + str(
#                         visitor_temp.is_print),
#                     data=json.dumps(dict_new), headers=payload)
#                 if r1.status_code == 200:
#                     visitor_temp.is_print = visitor_temp.is_print + 1
#                     visitor_temp.check_status = 'Зарегистрирован'
#                     db.commit()
#                     db.close()
#                     return JSONResponse(status_code=200, content={'status': 'Success'})
#                 else:
#                     return JSONResponse(status_code=500, content={'status': 'Error'})
#         except ConnectionError:
#             print('IS not Connect')

# @router.get("/print")
# async def prints(id,re:Request, db: Session = Depends(deps.get_db)):
#     print('Is connected from:')
#     print(re.client.host)
#     visitor_temp = db.query(Visitors).filter(Visitors.id == int(id)).first()
#
#     visitor_temp.check_in = datetime.datetime.now().strftime('%y-%m-%d-%H-%M')
#     visitor_temp.is_check = 1
#
#     printer = db.query(PrinterService).filter(PrinterService.url == str('http://'+ str(re.client.host))).first()
#     if printer == None:
#         printer = db.query(PrinterService).filter(PrinterService.is_default== 1).first()
#     print(printer.url)
#     if printer != None:
#         try:
#             # проверка, что сервис доступен
#             r0 = requests.get(printer.url + ':' + str(printer.port) + '/api/v1/connect/printer?code=1',
#                               headers={}, data={})
#             print(printer.url +':'+ str(printer.port) + '/api/v1/connect/printer?code=1')
#             print(r0.status_code)
#             if r0.status_code == 200:
#                 printer.is_online = 1
#                 db.commit()
#                 st1 = str(visitor_temp.organization)
#                 if visitor_temp.regQR != None:
#                     st2 = str(visitor_temp.regQR)
#                 else:
#                     st2 = str(5000 + visitor_temp.id)
#                 dict_new = {
#                     "document": {
#                         "name": "documents",
#                         "protocol": "atolmsk",
#                         "details": [
#                             {
#                                 "type": "task",
#                                 "code": str(visitor_temp.id) + str(visitor_temp.is_print),
#                                 "count": "1",
#                                 "values": [
#                                     {
#                                         "id": "Barcode",
#                                         "data": st2
#                                     }
#                                 ]
#                             }
#                         ]
#                     }
#                 }
#                 payload = {'Content-Type': 'application/json'}
#                 print(json.dumps(dict_new))
#                 r1 = requests.post(
#                     printer.url + ':' + str(printer.port) + "/api/v1/add/task?code=" + str(visitor_temp.id) + str(
#                         visitor_temp.is_print),
#                     data=json.dumps(dict_new), headers=payload)
#                 if r1.status_code == 200:
#                     visitor_temp.is_print = visitor_temp.is_print + 1
#                     visitor_temp.check_status = 'Зарегистрирован'
#                     db.commit()
#                     db.close()
#                     return JSONResponse(status_code=200, content={'status': 'Success'})
#                 else:
#                     return JSONResponse(status_code=500, content={'status': 'Error'})
#         except ConnectionError:
#             print('IS not Connect')

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
