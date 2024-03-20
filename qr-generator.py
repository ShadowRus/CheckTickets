import pandas as pd
import qrcode
import os

# Загрузка файла Excel
participants_df = pd.read_excel('partcipiants.xlsx')

# Создание директории для QR кодов, если она не существует
os.makedirs('qr_codes', exist_ok=True)

# Функция для генерации QR кода
def generate_qr_code(data, file_name):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img.save(f'qr_codes/{file_name}.png')

# Итерация по строкам DataFrame
for index, row in participants_df.iterrows():
    # Генерация данных для QR кода
    qr_data = 5000 + row["number"]
    # Генерация QR кода и сохранение его с именем участника
    generate_qr_code(str(qr_data), row["NameSurname"])

print("QR коды были сгенерированы и сохранены в директории 'qr_codes'.")
