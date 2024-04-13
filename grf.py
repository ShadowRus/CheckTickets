from PIL import Image
import numpy as np

# Открываем изображение
im = Image.open('600.png').convert('1')
im = im.resize((im.width // 8 * 8, im.height // 8 * 8))  # размер должен быть кратным 8
im = np.array(im)

grf = []
for i in range(0, im.shape[1], 8):
    for j in range(im.shape[0]):
        byte = 0
        for k in range(8):
            byte = byte << 1 | im[j, i + k]
        grf.append(byte)

with open('your_image.grf', 'wb') as f:
    f.write(bytes(grf))
