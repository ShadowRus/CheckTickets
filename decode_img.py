import base64

# Откройте файл изображения в бинарном режиме
with open("600.png", "rb") as image_file:
    # Кодируйте данные в строку base64
    encoded_string = base64.b64encode(image_file.read()).decode()

# Выведите закодированную строку
print(len(encoded_string))
