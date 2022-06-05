import time
import numpy as np
import pyautogui
import pyscreenshot as ImageGrab
import cv2
import os
import pytesseract
import keyboard
import time
import re
from mss import mss
import mss.tools

pytesseract.pytesseract.tesseract_cmd = "C:\\Users\\timka\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe"

file = open('costs.txt')
text = file.read()
print("waiting... press->'end'")
keyboard.wait('end')
acount = 0
Any = False


def Click(posx, posy):  # click(cost_1)    Клик , передается позиция нажатия
    if keyboard.is_pressed('home'):
        print("code turned off")
        os._exit(0)
    pyautogui.moveTo(posx, posy)
    pyautogui.mouseDown()
    time.sleep(0.01)
    pyautogui.mouseUp()


def Search(name, status=0):
    print('Ищу ' + name)
    if os.path.exists(name):
        template = cv2.imread(name, 0)
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            im = sct.grab(monitor)
            mss.tools.to_png(im.rgb, im.size, output="search.png")
        img_rgb = cv2.imread("search.png")
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        w, h = template.shape[::-1]
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.9
        loc = np.where(res >= threshold)
        last = [0, 0]
        for pt in zip(*loc[::-1]):
            print(pt)
            if pt[0] - last[0] > 8 or pt[1] - last[1] > 8:
                if status == 10:
                    return pt[0] - w * 2, pt[1]
                if status == 11:
                    return pt[0] - w, pt[1] + h * 2 // 3
                if status == 14:
                    Click(pt[0] - w * 2, pt[1] + h / 2)
                    time.sleep(0.2)
                if status == 2:
                    Click(pt[0] + w / 2, pt[1] + h / 2)
                    time.sleep(0.2)
                    return True
                if status == 1:
                    return pt[0] + w / 2, pt[1] + h / 2
                if status == 0:
                    return pt, w, h
            last = pt
    return 0


def SetPos():  # записывает координаты точек и окошка для проверки
    print("Первая цена в списке: ")
    print("Левый верхний угол: ")
    global cost_1
    cost_1 = Search('purchase.png', 10)
    print(cost_1)
    print("Правый нижний угол: ")
    global cost_2
    cost_2 = Search('purchase.png', 11)
    print(cost_2)
    print("Кнопка покупки этого предмета: ")  # buy
    global buy
    buy = Search('purchase.png', 1)
    print(buy)
    print("Кнопка обновить: ")  # refresh
    global refresh
    refresh = Search('refresh.png', 1)
    print(refresh)
    print("Фильтр: ")  # filter
    global filter
    filter = Search('filter.png', 0)
    print(filter)
    time.sleep(1)


def SetScreen(pos1x, pos1y, pos2x, pos2y, filename):  # Скрин рабочей поверхности
    screen = np.array(ImageGrab.grab(bbox=(pos1x, pos1y, pos2x, pos2y)))
    cv2.imwrite(filename, screen)
    cv2.destroyAllWindows()


def Read(name):  # считать значение скрина
    img = cv2.imread(name)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    newtext = pytesseract.image_to_string(rgb)
    if name == "cost.png":
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thr = cv2.threshold(rgb, 0, 255, cv2.THRESH_OTSU)[1]
        config = r'--oem 3 --psm 13 -c tessedit_char_whitelist=Pp0O123456789'
        newtext = pytesseract.image_to_string(thr, config=config)
        newtext = newtext[0:len(newtext) - 2]
        newtext = newtext.replace('P', '')
        newtext = newtext.replace('p', '')
        newtext = newtext.replace('', '')
        if newtext == '':
            newtext = 0
            return newtext
        return str(newtext)
    if name != 'okpanel.png':
        print(newtext)
    return newtext


def Update():  # Обновить если цена больше
    global refresh
    Click(refresh[0], refresh[1])
    time.sleep(0.1)

def Filter():
    global file
    global filter
    global text
    if text.find("=") == -1:
        file = open('costs.txt')
        text = file.read()
        file.close()
    item = text[0:text.find("=")]
    global cost_item
    cost_item = text[text.find("=") + 1:text.find(",")]
    Search('changefilter.png', 2)
    global Any
    if Any == False:
        Search('any.png', 2)
        Any = True
        Search('RUB.png', 2)
    Search('Rubfilter.png', 14)
    pyautogui.write(cost_item)
    Search("okfilter.png", 2)
    time.sleep(0.1)
    Click(filter[0][0] + filter[1] / 2, filter[0][1] + filter[2] / 2)
    pyautogui.write("")
    pyautogui.write(item)
    print("=" + cost_item)
    text = text[text.find(",") + 1:len(text)]
    time.sleep(2)
    Click(filter[0][0], filter[0][1] + filter[2] * 2)



def Check():
    Update()
    while Wait():
        if Search('purchase.png', 2) == True:
            time.sleep(0.1)
            pyautogui.keyDown("Y")
            time.sleep(0.05)
            pyautogui.keyUp("Y")
            time.sleep(0.5)
            OK()
            time.sleep(0.2)
            Check()
        else:
            print("цена выше")
            Filter()
            Working()


def OK():
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        left = monitor["left"] + monitor["width"] * 32 // 100  # % from the left
        top = monitor["top"] + monitor["height"] * 10 // 100  # % from the top
        right = left + 800  # px width
        lower = top + 800  # px height
        bbox = (left, top, right, lower)
        im = sct.grab(bbox)
        mss.tools.to_png(im.rgb, im.size, output="okpanel.png")
    textforok = Read("okpanel.png")
    if textforok.find("bot") != -1 or textforok.find("choose") != -1 or textforok.find("Confirm") != -1:
        Captch()

    elif textforok.find("don't") != -1 or textforok.find("have") != -1 or textforok.find(
            "money") != -1 or textforok.find("transaction") != -1:
        print('денег нет, но выдержитесь. Я пока не умею продавать сам')
        os._exit(0)

    elif textforok.find("offer") != -1 or textforok.find("has") != -1 or textforok.find(
            "already") != -1 or textforok.find("been") != -1 or textforok.find("Offer") != -1 or textforok.find(
        "was") != -1 or textforok.find("sold") != -1:
        Search('ok.png', 2)
        print('нажал на ок')
def Captch():
    pt = Search("notbot.png", 0)  # pt = pt[x,y],w,h
    if pt[0][0] != 0:
        temp = pt[2] // 2
        global cost_1
        global cost_2
        SetScreen(pt[0][0], pt[0][1], pt[0][0] + pt[1], pt[0][1] + pt[2] + temp, 'nameitem.png')
        text = Read('nameitem.png')
        text = text[text.find(':') + 2:len(text) - 2]
        text = text + '.png'
        text = text.replace('"', '')
        if os.path.exists(text):
            Search(text, 2)
        else:
            file = open('dontknow.txt', 'w')
            file.write(text + ',')
            Search('confirm.png', 2)
            Captch()
            return

        Search('confirm.png', 2)
        time.sleep(0.4)


def Wait():  # Ждать пока появится   # возращает True, когда обновился
    if keyboard.is_pressed('home'):
        print("code turned off")
        os._exit(0)
    global acount
    acount = acount + 1
    if acount > 5:
        Update()
        print('update in wait')
    if acount > 10:
        Filter()
    text=Search('purchase.png',1)
    if text != 0:
        print("true")
        acount = 0
        return True
    else:
        print("wait")
        acount = acount + 1
        time.sleep(0.5)
        Working()
        return False


def Working():
    OK()
    while Wait():
        Check()


SetPos()
Filter()
Working()
file.close()
