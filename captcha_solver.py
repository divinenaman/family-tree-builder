import pytesseract
import cv2
from PIL import Image
from operator import itemgetter
import time


def manual(img_path):

    im = Image.open(img_path)
    im.show()
    time.sleep(5)
    im.close()

    text = input('captcha: ')

    return text

# pytesseract.pytesseract.tesseract_cmd = r'<full_path_to_your_tesseract_executable>'


def text_captcha(img_path, config=""):

    im = Image.open(img_path)
    im = im.convert("P")
    his = im.histogram()
    im2 = Image.new("P", im.size, 255)
    values = {}

    for i in range(256):
        values[i] = his[i]

    for j, k in sorted(values.items(), key=itemgetter(1), reverse=True)[:10]:
        print(j, k)

    temp = {}

    for x in range(im.size[1]):
        for y in range(im.size[0]):
            pix = im.getpixel((y, x))
            temp[pix] = pix
            if pix > 3:
                im2.putpixel((y, x), 0)

    im2.save("output.gif")

    img = cv2.imread(img_path)

    img = cv2.GaussianBlur(img, (1, 1), cv2.BORDER_CONSTANT)

    #cv2.imshow("gen", img)
    # cv2.waitKey(0)

    gry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    (h, w) = gry.shape[:2]
    gry = cv2.resize(gry, (w*5, h*5))

    cls = cv2.morphologyEx(gry, cv2.MORPH_CLOSE, None)
    #neg = cv2.bitwise_not(cls)
    _, thr = cv2.threshold(cls, 0, 255, cv2.THRESH_OTSU |
                           cv2.THRESH_BINARY_INV)

    thr = (255-thr)

    cv2.imshow("gen", thr)

    cv2.imwrite("out.jpg", thr)

    cv2.waitKey(0)

    return pytesseract.image_to_string(im2, lang="eng", config=config)


if __name__ == "__main__":
    print(text_captcha("o.png", config="--psm 8"))
