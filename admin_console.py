import streamlit as st
import requests
import socket
import pandas as pd
import matplotlib.pyplot as plt


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


GET_VISITORS = 'http://'+str(extract_ip())+':'+str(8000)+ str('/visitors')

if st.checkbox('Показать статистику регистрации'):
    re = requests.get(GET_VISITORS)
    j1 = re.json()
    df = pd.DataFrame.from_records(j1)
    df.set_index('id', inplace=True)
    df = df[['check_status', 'surname', 'name', 'position', 'organization', 'check_in', 'is_print']]
    st.data_editor(df)




    # предположим, что df - это ваш DataFrame

    # фильтруем DataFrame по интересующим нас статусам
    filtered_df = df[df['check_status'].isin(['Зарегистрирован', 'На регистрации'])]

    # подсчитываем количество строк для каждого статуса
    counts = filtered_df['check_status'].value_counts()

    # определяем цвета для каждого статуса
    colors = ['green' if status == 'Зарегистрирован' else 'red' for status in counts.index]

    # строим гистограмму
    plt.bar(counts.index, counts.values, color=colors)
    plt.xlabel('Status')
    plt.ylabel('Count')
    plt.title('Number of visitors by status')

    # выводим гистограмму в Streamlit
    st.pyplot(plt)

    st.write(df['check_in'].dtype)
    df = df[df['check_in'].notna()]

    df['check_in'] = pd.to_datetime(df['check_in'], format='%y-%m-%d-%H-%M-%S', errors='coerce')

    st.write(df['check_in'].dtype)
    st.dataframe(df['check_in'])
    # Выполняем ресемплинг данных по минутам и считаем количество записей на каждую минуту
    resampled = df.resample('min', on='check_in').count()
    st.data_editor(resampled['check_status'])
