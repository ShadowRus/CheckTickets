from fastapi import APIRouter, UploadFile, File, Depends, Request,Body
from typing import Dict
from fastapi.responses import JSONResponse

from models.CrptDM import DMCode,CRPT
from sqlalchemy.orm import Session
import pandas as pd
from api import deps
import aiofiles as aiofiles
import datetime
import os
from decouple import config
import socket
import base64

router = APIRouter()
now = datetime.datetime.now()


def sgd_cmd(host,port,sgd):
    import socket
    mysocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        mysocket.connect((host,port))
        mysocket.settimeout(5)
        mysocket.send(sgd)
        a1 = b'\x00'
        a1 = a1.decode('utf-8')
        recv = mysocket.recv(4096).decode('utf-8')
        if recv[-1] == a1:
            return recv[:-1]
        else:
            return recv
    except:
        return None
    finally:
        mysocket.close()


def decode_base64(input_str):
    # Декодируем строку из base64
    bytes_str = base64.b64decode(input_str)
    print('decode_base64')
    print(f'base64.b64decode {bytes_str}')

    # Преобразуем каждый байт в его десятичное представление
    # или шестнадцатеричное, если это нечитаемый символ
    result = []
    for b in bytes_str:
        if 32 <= b <= 126:  # Проверяем, является ли символ читаемым
            print(str(b))
            result.append(str(b))
        else:
            result.append(hex(b))  # Преобразуем нечитаемый символ в шестнадцатеричный

    return ' '.join(result)

@router.get("/crpt", summary="Получаем DATAMATRIX",
             description="")
def template(code:str,db: Session = Depends(deps.get_db)):
    if 5 ==5 :
        import socket


        #data1= 'SGVsbG8gd29ybGQ='
        data1= code
        print(len(code))
        print(data1)

        #data1 = decode_base64(data1)
        # Декодируем строку из Base64
        data1 = base64.b64decode(data1).decode('utf-8')
        print(data1)

        # Преобразовываем декодированные байты в строку
        #data1 = data1.decode('utf-8')

        # Заменяем символы GS и FNC1 на их шестнадцатеричное представление
        data1 = data1.replace('@', '_1D')
        data1 = data1

        # Создаем сокет
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = '192.168.0.101'
        port = 9100
        # Подключаемся к принтеру этикеток (замените 'hostname' и 'port' на ваш принтер)
        s.connect((host, port))

        # Открываем файл
        with open('src/crpt_label.txt', 'r') as file:
            for line in file:
                # Заменяем DATA на пользовательское значение, если оно присутствует
                line = line.replace('DATA', data1)

                # Отправляем строку на принтер
                print(line.encode())
                s.send(line.encode())

        # Закрываем сокет
        s.close()

        return JSONResponse(status_code=200, content={'status': 'Success'})

@router.post("/scanner")
async def create_item(item: Dict = Body(...)):
    # Теперь `item` - это произвольный JSON объект (словарь в Python)
    print(item)
    return JSONResponse(status_code=200, content={'status': 'Success'})


@router.get("/templ", summary="Получаем DATAMATRIX",
             description="")
def template(name:str,db: Session = Depends(deps.get_db)):
    if 5 ==5 :
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = '192.168.0.112'
        port = 9100
        # Подключаемся к принтеру этикеток (замените 'hostname' и 'port' на ваш принтер)
        s.connect((host, port))
        # Открываем файл
        name = name+ str(',')
        data1 =str('вставай,')
        data2= str('мы все починили')
        with open('src/maria_white.txt', 'r') as file:
            for line in file:
                # Заменяем DATA на пользовательское значение, если оно присутствует
                line = line.replace('NAME', str(name))
                line = line.replace('DATA1', data1)
                line = line.replace('DATA2', data2)

                # Отправляем строку на принтер
                print(line.encode())
                s.send(line.encode())

        # Закрываем сокет
        s.close()

        return JSONResponse(status_code=200, content={'status': 'Success'})