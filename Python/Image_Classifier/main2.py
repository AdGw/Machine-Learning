from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
                help="path to input image")
ap.add_argument("-r", "--reference", required=True,
                help="path to reference OCR-A image")
args = vars(ap.parse_args())

FIRST_NUMBER = {
    "3": "American Express",
    "4": "Visa",
    "5": "MasterCard",
    "6": "Discover Card"
}
#
ref = cv2.imread(args["reference"])
ref = cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY)
ref = cv2.threshold(ref, 10, 255, cv2.THRESH_BINARY_INV)[1]

refCnts = cv2.findContours(ref.copy(), cv2.RETR_EXTERNAL,
                           cv2.CHAIN_APPROX_SIMPLE)
refCnts = imutils.grab_contours(refCnts)
refCnts = contours.sort_contours(refCnts, method="left-to-right")[0]
digits = {}

# Przejście pętli przez kontury zdjęcia referencyjnego
for (i, c) in enumerate(refCnts):
    # Wyszukiwanie liczb, wyodrębnianie ich i dopasowanie wielkości
    (x, y, w, h) = cv2.boundingRect(c)
    roi = ref[y:y + h, x:x + w]
    roi = cv2.resize(roi, (57, 88))

    # zaktualizowanie bazy cyfr, mapowanie nazw cyfr do ROI
    digits[i] = roi

# inicjalizacja kernela
rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 3))
sqKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

# Wczytanie zdjęcia, dopasowanie wielkości i konwersja do skali szarości
image = cv2.imread(args["image"])
height, width, channels = image.shape
print(image.shape)
image = imutils.resize(image, width=300)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

tophat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, rectKernel)

# obliczanie gradientu Scharra i przeskalowanie
# compute the Scharr gradient of the tophat image, then scale
gradX = cv2.Sobel(tophat, ddepth=cv2.CV_32F, dx=1, dy=0,
                  ksize=-1)
gradX = np.absolute(gradX)
(minVal, maxVal) = (np.min(gradX), np.max(gradX))
gradX = (255 * ((gradX - minVal) / (maxVal - minVal)))
gradX = gradX.astype("uint8")

# Zastosowanie operacji zamykania za pomocą Kernela w celu
# zamknięcia luk pomiędzy cyframi w kartach kredytowych
# binaryzacja obrazu metodą Otsu

gradX = cv2.morphologyEx(gradX, cv2.MORPH_CLOSE, rectKernel)
thresh = cv2.threshold(gradX, 0, 255,
                       cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

# Zastosowanie drugiej operacji zamykania dla zdjęcia zbinaryzowanego
# aby unikac luk między cyframi

thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, sqKernel)

# znajdywanie konturów na obrazie progowym, nastepnie inicjalizowanie
# listy lokalizacji cyfr

cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                        cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
locs = []

# przechodzenie pętli po konturach
for (i, c) in enumerate(cnts):
    # przejście pętli przez kontury nastepnie użycie ramki ograniczającej
    # i wyznaczenie współczynnika kształtu

    (x, y, w, h) = cv2.boundingRect(c)
    ar = w / float(h)

    # karty kredytowe używają czcionki o stałym rozmiarze i są w 4 grupach
    # przycinanie kontur na podstawie współczynnika kształtu
    if 2.5 < ar < 4.0:
        # kontury można przycinać przy różnej szerokości
        if (40 < w < 55) and (10 < h < 20):
            # dołączenie regionu ramki granicznej zawierającej grupy cyfr
            locs.append((x, y, w, h))

# posortowanie lokalizacji cyfr od lewej do prawej a następnie inicjalizowanie
# listy sklasyfikowanych cyfr

locs = sorted(locs, key=lambda x: x[0])
output = []

# Pętla przechodząca przez 4 cyfry 4 grup
for (i, (gX, gY, gW, gH)) in enumerate(locs):
    # inicjalizacja listy zgrupowanych cyfr
    groupOutput = []

    # wyodrębnienie grupy 4 cyfr ze zdjęcia w skali szarości
    # implementacja progu w celu oddzielenia cyfr od tła karty kredytowej

    group = gray[gY - 5:gY + gH + 5, gX - 5:gX + gW + 5]
    group = cv2.threshold(group, 0, 255,
                          cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # rozpoznawanie każdej pojedycznej liczby z grupy
    # sortowanie kontur od lewej do prawej
    digitCnts = cv2.findContours(group.copy(), cv2.RETR_EXTERNAL,
                                 cv2.CHAIN_APPROX_SIMPLE)
    digitCnts = imutils.grab_contours(digitCnts)
    digitCnts = contours.sort_contours(digitCnts,
                                       method="left-to-right")[0]

    # pętla po konturach cyfr
    for c in digitCnts:
        # obliczanie konturów dla pojedynczych cyfr, wyodręnienie
        # i dopasowanie do cyfr zdjęcia referencyjnego
        (x, y, w, h) = cv2.boundingRect(c)
        roi = group[y:y + h, x:x + w]
        roi = cv2.resize(roi, (57, 88))

        # inicjalizacja wyników pasujących do szablonu
        scores = []

        # przejście pętli przez zdjęcie referencyjne
        for (digit, digitROI) in digits.items():
            # zastosowanie dopasowania szablonu opertego na korelacji
            # zaktualizowanie listy wyników
            result = cv2.matchTemplate(roi, digitROI,
                                       cv2.TM_CCOEFF)
            (_, score, _, _) = cv2.minMaxLoc(result)
            scores.append(score)

        # klasyfikacja dla cyfr będzie odniesieniem
        # nazwa cyfry z najlepszym wynikiem dopasowania
        groupOutput.append(str(np.argmax(scores)))

    # wyrysowanie konturów rozróżniających grupy cyfr
    # wyświetlenie zczytanych wartości z karty
    # cv2.rectangle(image, (gX - 5, gY - 5),
    #               (gX + gW + 5, gY + gH + 5), (0, 0, 255), 2)
    # cv2.putText(image, "".join(groupOutput), (gX, gY - 15),
    #             cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)
        cv2.rectangle(image, (gX, gY),
        (gX + gW, gY + gH), (0, 0, 0), 15)

    output.extend(groupOutput)
password_provided = "".join(output)  # This is input in the form of a string

password = password_provided.encode()  # Convert to type bytes
salt = b'salt_'  # CHANGE THIS - recommend using a key from os.urandom(16), must be of type bytes
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100000,
    backend=default_backend()
)
key = base64.urlsafe_b64encode(kdf.derive(password))  # Can only use kdf once
# print("Credit Card #: {}".format("".join(output)))
# print("Credit Card Type: {}".format(FIRST_NUMBER[output[0]]))
typeOfCreditCard = FIRST_NUMBER[output[0]].encode()

message = "".join(output).encode()
Fernet.generate_key()  # Store this key or get if you already have it
f = Fernet(key)
encrypted = f.encrypt(message)
decrypted = f.decrypt(encrypted)

fileW = open('key.key', 'ab')
fileR = open('key.key','r')
path = args["image"].encode()
if args["image"] in fileR.read():
    pass
else:
    fileW.write(b"\n"+b"Path: " + path + b"\n" + b"\t" + b"Credit card number: " + encrypted + b"\n" + b"\t" + b"Credit card type: " + typeOfCreditCard)  # The key is type bytes still
    fileW.close()
cv2.imshow("Image", image)
cv2.waitKey(0)

from PIL import Image
import pytesseract
import argparse
import cv2
import os
import imutils

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

img = Image.open(r"images/Credit_Cards/03.png")
text = pytesseract.image_to_string(img)

print(text)
