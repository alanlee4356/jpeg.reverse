from hashlib import shake_128
from PIL import Image
from matplotlib import pyplot as plt
import numpy as np
im = Image.open('lena_gray.bmp', 'r')
width, height = im.size
pixel_values = list(im.getdata()) #이미지 데이터를 1차원리스트로 받아옴
s1 = np.zeros((512,512))
np.array(s1, dtype=np.uint8)
s = pixel_values
for i in range(0,512): #1차원리스트를 2차원배열로 변경
    for j in range(0,512):
        s1[i][j] = pixel_values[i*512+j]
    

newimg = Image.fromarray(s1)


plt.imshow(newimg)
plt.show()
print('rd')