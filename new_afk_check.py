import cv2
from HumanCursor import *
import numpy as np
import sys
import pyautogui
import time

grey_colors = [[107, 149, 157], [104, 142, 149], [93, 101, 113], [100, 112, 128], [111, 157, 165], [116, 144, 153], [108, 130, 139], [114, 143, 150], [94, 94, 94]]
def is_grey(px):
    if 130 >= px[2] >= 100 >= px[0] >= 85 and 95 <= px[1] <= 115:
        return True
    for gc in grey_colors:
        if abs(px[0] - gc[0]) + abs(px[1] - gc[1]) + abs(px[2] - gc[2]) <= 30:
            return True
    return False

time.sleep(3)
sys.setrecursionlimit(5000)
rarities = [[109, 239, 126], [93, 230, 255], [227, 82, 77], [222, 31, 134], [31, 31, 222], [222, 200, 15], [117, 43, 255], [163, 255, 43]]
white = [255, 255, 254]
jump = 5
cursor = SystemCursor()
count = 0

def dfs(x, y):
    global count
    if x < 0 or y < 0 or x >= img.shape[0] or y >= img.shape[1]:
        return
    if not (img[x][y] == white).all():
        return
    if vis[x][y]:
        return
    vis[x][y] = True
    count += 1
    next_coords = [(x - jump, y), (x + jump, y), (x, y - jump), (x, y + jump),
                   (x - 2 * jump, y), (x + 2 * jump, y), (x, y - 2 * jump), (x, y + 2 * jump),
                   (x - jump, y - jump), (x + jump, y - jump), (x - jump, y + jump), (x + jump, y + jump)]
    for coord in next_coords:
        dfs(coord[0], coord[1])

time.sleep(3)
while True:
    imgObj = pyautogui.screenshot()
    imgArr = cv2.cvtColor(np.array(imgObj), cv2.COLOR_RGB2BGR)
    img = np.zeros((1400, 2200, 3))
    img[:imgArr.shape[0], :imgArr.shape[1]] = imgArr
    cv2.imwrite("new.PNG", img)
    vis = np.zeros((1400, 2200))
    for i in range(0, 300, jump):
        for j in range(0, 400, jump):
            img[i][j] = [0, 0, 0]
    for i in range(0, len(img), jump):
        for j in range(0, len(img[i]), jump):
            pixel = img[i][j]
            if is_grey(pixel):
                img[i][j] = white
    cv2.imwrite("new.PNG", img)
    max_cluster = 0
    max_coord = (0, 0)
    for i in range(0, len(img), jump):
        for j in range(0, len(img[i]), jump):
            if (img[i][j] == white).all():
                if not vis[i][j]:
                    count = 0
                    dfs(i, j)
                    if count > max_cluster:
                        max_cluster = count
                        max_coord = (i, j)
    if max_cluster <= 15:
        continue
        # pass
    vis = np.zeros((2000, 2000))
    dfs(max_coord[0], max_coord[1])
    sum_start, num_start = [0, 0], 0
    for i in range(0, len(img), 10):
        for j in range(0, len(img[i]), 10):
            pixel = img[i][j]
            flag = False
            for rarity in rarities:
                if abs(rarity[0] - pixel[0]) + abs(rarity[1] - pixel[1]) + abs(rarity[2] - pixel[2]) <= 40:
                    for k in range(i - 25, i + 30, 5):
                        for l in range(j - 25, j + 30, 5):
                            if vis[k][l]:
                                flag = True
                                sum_start[0] += i
                                sum_start[1] += j
                                num_start += 1
                                break
                        if flag:
                            break
                    if flag:
                        break
    if num_start == 0:
        continue
    start = ((sum_start[0] // num_start // 5) * 5, (sum_start[1] // num_start // 5) * 5)
    print("Detected:", start)
    cur = start
    stack = [cur]
    recur = 0
    while True:
        recur += 1
        if recur > 100:
            print("Maximum recursive exceeded!")
            break
        sum_cur, num_cur = [0, 0], 0
        for i in range(-25, 30, jump):
            for j in range(-25, 30, jump):
                if i * i + j * j <= 625 and vis[cur[0] + i][cur[1] + j]:
                    img[cur[0] + i][cur[1] + j] = [0, 255, 0]
                    sum_cur[0] += i
                    sum_cur[1] += j
                    num_cur += 1
        if num_cur == 0:
            break
        next_cur = ((cur[0] + sum_cur[0] // num_cur) // jump * jump, (cur[1] + sum_cur[1] // num_cur) // jump * jump)
        for i in range(-20, 25, jump):
            for j in range(-20, 25, jump):
                if i * i + j * j <= 400:
                    img[cur[0] + i][cur[1] + j] = [0, 0, 0]
                    vis[cur[0] + i][cur[1] + j] = False
        cur = next_cur
        stack.append(next_cur)
    cursor.move_to([stack[0][1], stack[0][0]])
    img[stack[0][0]][stack[0][1]] = [0, 255, 0]
    pyautogui.mouseDown()
    duration = 0.5
    for i in range(1, len(stack)):
        duration += random.uniform(-0.1, 0.1)
        if duration < 0.2:
            duration = 0.2
        if duration > 0.6:
            duration = 0.6
        cursor.move_to_short([stack[i][1], stack[i][0]], steady=True, duration=duration)
        img[stack[i][0]][stack[i][1]] = [0, 255, 0]
    pyautogui.mouseUp()
    cv2.imwrite("new.PNG", img)
