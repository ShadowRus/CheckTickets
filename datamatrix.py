from pylibdmtx.pylibdmtx import encode
from PIL import Image

# GS1 DataMatrix начинается с FNC1 символа, ASCII значение которого - 232
data = chr(232) + '0104606745004004215?TlNHUTeDisT'+chr(29)+'93aKaN'
encoded = encode(data)

# Преобразование в изображение и сохранение
img = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)
img.save('datamatrix.png')

