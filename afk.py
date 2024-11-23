import os
import signal
import time
import datetime
from PIL import Image
from HumanCursor import *
import keyboard as kb
import pyautogui

AFK_CHECK_LOCATION_LIST = ["AFK_common.png", "AFK_unusual.png",
                           "AFK_rare.png", "AFK_epic.png",
                           "AFK_legendary.png", "AFK_mythic.png",
                           "AFK_ultra.png", "AFK_super.png"]
cursor = SystemCursor()

def florr_afk_check():
    try:
        for afk_check_location in AFK_CHECK_LOCATION_LIST:
            afk_check = Image.open("Images/afk_check/" + afk_check_location)
            box = pyautogui.locateOnScreen(afk_check, grayscale=False, confidence=0.72)
            if box is not None:
                x, y, w, h = box
                center_x = x + w / 2 + random.randint(-34, 34)
                center_y = y + h / 2 + random.randint(-7, 7)
                cursor.move_to([center_x, center_y])
                pyautogui.click()
                print("AFK Check found at " + datetime.datetime.now().strftime('%H:%M:%S') + " at location x=" + center_x + ", y=" + center_y)
    except:
        pass

def florr_afk_main():
    cnt = 0
    while True:
        if kb.is_pressed('v'):
            break
        if cnt == 0:  # Min 16s, Max 22.7s, Avg 19.3s, quite random lol
            florr_afk_check()
        sleep(0.4 + random.random() / 6)
        cnt = (cnt + 1) % 40  # 40 iterations

if __name__ == '__main__':
    time.sleep(3)
    florr_afk_main()
    pid = os.getpid()
    os.kill(pid, signal.SIGTERM)
    # Kill current process, terminate program
