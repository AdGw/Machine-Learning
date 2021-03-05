import os
import imageio
from PIL import Image


path = os.listdir("./")
arr = []
for i in path:
    try:
        path2 = os.listdir("./"+i)
        for j in path2:
            # print(j+"/"+i)
            # pic = imageio.imread(i+"/"+j)
            img = Image.open(i+"/"+j)
            s_img = str(img)
            if s_img.count("RGBA"):
                pass
                # print(img)
                # arr.append(i+"/"+j)
            else:
                print(img)
    except NotADirectoryError:
        pass
print(arr)
for i in arr:
    os.remove(i)