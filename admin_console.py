import streamlit as st
import requests
import socket
import pandas as pd
#import matplotlib.pyplot as plt
from decouple import config
import os

def extract_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP

def str_to_num(s):
    try:
        return int(s)  # пробуем преобразовать в целое число
    except ValueError:
        return s

SRC_DIR = config('SRC_DIR',default='./src')
PORT= config('PORT',default=8000)
GET_VISITORS = config('GET_VISITORS',default = '/visitors')
NEW_VISITORS=config('NEW_VISITORS',default='/register')
PRINT=config('GET_PRINT',default='/print')
SERVER_URL = 'http://'+str(extract_ip())+':'+str(PORT)
SEARCH_SURNAME = config('SEARCH_SURNAME',default='/search')
SEARCH_BARCODE = config('SEARCH_BARCODE',default='/barcode')

st.image(os.path.join(SRC_DIR,'Logo_cyrillic_red.png'))

with st.sidebar:
    st.selectbox('Выберите действие',['Показать статистику','Поиск и Зарегистрировать участника','Настройки сервиса'],index=1,key='action')
if st.session_state['action'] == 'Показать статистику':
    re = requests.get(str(SERVER_URL+GET_VISITORS))
    j1 = re.json()
    df = pd.DataFrame.from_records(j1)
    df.set_index('id', inplace=True)
    df = df[['check_status', 'surname', 'name', 'position', 'organization', 'check_in', 'is_print']]
    c1,c2 = st.columns(2)
    with c1:
        if st.button('Обновить'):
            st.rerun()
    with c2:
        df.to_excel('Статус регистраций на БПК-2024.xlsx', index=False)
        with open('src/Статус регистраций на БПК-2024.xlsx', "rb") as f:
            bytes_data = f.read()
        st.download_button(
            label="Скачать отчет о регистрациях",
            data=bytes_data,
            file_name='src/Статус регистраций на БПК-2024.xlsx',
            mime='application/vnd.ms-excel',
        )

    my_bar = st.progress(int(df[df['check_status']=='Зарегистрирован']['check_status'].count())/int(df[['check_status']].count()),
                         text=f"**Зарегистрировано** участников:"
                              f" **:green[{int(df[df['check_status']=='Зарегистрирован']['check_status'].count())}]** из **:red[{int(df[['check_status']].count())}]**")
    st.data_editor(df)




    # # фильтруем DataFrame по интересующим нас статусам
    # filtered_df = df[df['check_status'].isin(['Зарегистрирован', 'На регистрации'])]
    # # подсчитываем количество строк для каждого статуса
    # counts = filtered_df['check_status'].value_counts()
    # # определяем цвета для каждого статуса
    # colors = ['green' if status == 'Зарегистрирован' else 'red' for status in counts.index]
    # # строим гистограмму
    # plt.bar(counts.index, counts.values, color=colors)
    # plt.xlabel('Статус участника')
    # plt.ylabel('Количество, чел')
    # plt.title('На регистрации/Зарегистрировано')
    # # выводим гистограмму в Streamlit
    # st.pyplot(plt)

    # df = df[df['check_in'].notna()]
    # df['check_in'] = pd.to_datetime(df['check_in'], format='%y-%m-%d-%H-%M', errors='coerce')
    # # Выполняем ресемплинг данных по минутам и считаем количество записей на каждую минуту
    # resampled = df.resample('min', on='check_in').count()
    # st.data_editor(resampled['check_status'])
if 'visit' not in st.session_state:
    st.session_state['visit'] = {}
if st.session_state['action'] == 'Поиск и Зарегистрировать участника':
    j1={}
    if st.checkbox('Новый участник',value=False,key = 'new_visit'):
        st.session_state['visit'] = {}
        st.markdown(
            "Если к вам обратился гость :red[**без QR-кода для регистрации**] и его :red[**фамилии** нет в списках],"
            "то необходимо **сразу же обратиться к организаторам** мероприятия со стороны АТОЛ. \r\n"
            " ##### Контактное лицо: Ангелина Трайт + 7 915 495 45 87", unsafe_allow_html=True)

        st.text_input('Фамилия',key ='surname')
        st.text_input('Имя', key='name')
        st.text_input('Организация', key='organization')
        st.text_input('Город участника', key='position')
        if st.button('Зарегистрировать'):

            params = {
                'surname': st.session_state['surname'],
                'name': st.session_state['name'],
                'organization': st.session_state['organization'],
                'position': st.session_state['position']
            }
            # Отправляем GET запрос
            response = requests.get(str(SERVER_URL+NEW_VISITORS), params=params)
            j1 = [response.json()]
    else:
        st.text_input('Поиск по фамилии или номеру участника', key='search_data')
        if st.button('Поиск'):
            #if 'visit' in st.session_state:
            st.session_state['visit'] = {}
            if type(str_to_num(st.session_state['search_data'])) == int:
                response = requests.get(str(SERVER_URL + SEARCH_BARCODE),
                                        params={'code': str_to_num(st.session_state['search_data'])})
            else:
                response = requests.get(str(SERVER_URL + SEARCH_SURNAME),
                                        params={'surname': st.session_state['search_data']})

            j1 = response.json()

    for i in range(len(j1)):
        if 'name' in j1[i]:

            name = j1[i]['name']
            surname = j1[i]['surname']
            if surname[-1] == ' ':
                surname = surname[:-1]
            organization = j1[i]['organization']
            position = j1[i]['position']
            id_visitor = j1[i]['id']
            status = j1[i]['check_status']
            if status == 'Зарегистрирован':
                color = 'green'
            else:
                color='red'
            st.session_state['visit'][f" {name} **{surname}** ({organization}, {position} ) :{color}[**{status}**]"] = id_visitor
    st.radio(' ',st.session_state['visit'].keys(),label_visibility='hidden',key='print_ch')
    if st.button('Распечать бейдж', key='print'):
        response = requests.get(str(SERVER_URL + PRINT), params={'id': int(st.session_state['visit'][st.session_state['print_ch']])})
        st.session_state['visit'] = {}






