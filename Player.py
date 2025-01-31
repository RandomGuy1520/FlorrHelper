from Helper import *
from afk import *
import sys

vis = np.zeros((100, 200))

def get_screenshot():
    screenshot = Images.get_region(110, 0, 1920, 970, "Florr.png")
    filtered = np.zeros((screenshot.shape[0] // 10, screenshot.shape[1] // 10, 3))
    egg_colors = [[99, 231, 255], [80, 187, 207], [45, 45, 45], [159, 212, 222], [246, 234, 168], [115, 0, 156], [52, 221, 117], [94, 191, 210], [203, 209, 226], [88, 205, 226], [44, 122, 96]]
    garden_colors = [[97, 167, 30], [91, 158, 28], [100, 173, 31], [114, 61, 221], [99, 231, 255], [97, 166, 30], [153, 153, 153], [46, 70, 105], [204, 145, 63]]
    desert_colors = [[39, 59, 90], [184, 220, 236], [190, 226, 243], [175, 210, 225], [168, 201, 215], [46, 70, 105], [34, 52, 79]]
    for i in range(0, len(screenshot), 10):
        line = screenshot[i]
        for j in range(0, len(screenshot[i]), 10):
            pixel = line[j]
            flag = False
            if i >= 810 and 560 <= j <= 1360:
                flag = True
            if i >= 910 and j <= 420:
                flag = True
            if i <= 410 and j <= 330:
                flag = True
            if i >= 740 and j <= 80:
                flag = True
            if i <= 330 and j >= 1590:
                flag = True
            if not flag:
                for k in desert_colors:
                    if abs(k[0] - pixel[0]) + abs(k[1] - pixel[1]) + abs(k[2] - pixel[2]) <= 20:
                        flag = True
                        break
            if not flag:
                for k in egg_colors:
                    if abs(k[0] - pixel[0]) + abs(k[1] - pixel[1]) + abs(k[2] - pixel[2]) <= 20:
                        flag = True
                        break
            if flag:
                filtered[i // 10][j // 10] = [0, 0, 0]
            else:
                filtered[i // 10][j // 10] = pixel
    cv2.imwrite("Filter.png", filtered)
    print(filtered.shape[0], filtered.shape[1])

sum_x, sum_y, num = 0, 0, 0
def dfs(image, i, j):
    global sum_x, sum_y, num, vis
    if i < 0 or j < 0 or i >= image.shape[0] or j >= image.shape[1]:
        return
    if (image[i][j] == [0, 0, 0]).all() or vis[i][j] == 1:
        return
    vis[i][j] = 1
    sum_x += i
    sum_y += j
    num += 1
    dfs(image, i - 1, j)
    dfs(image, i + 1, j)
    dfs(image, i, j - 1)
    dfs(image, i, j + 1)

vec = []

def get_mobs():
    global sum_x, sum_y, num, vis, vec
    vec.clear()
    image = cv2.imread("Filter.png")
    vis = np.zeros((100, 200))
    for i in range(len(image)):
        for j in range(len(image[i])):
            if (image[i][j] != [0, 0, 0]).any() and vis[i][j] == 0:
                sum_x, sum_y, num = 0, 0, 0
                dfs(image, i, j)
                # Filter out false positives
                if num >= 10:
                    vec.append((sum_x // num, sum_y // num, num))
                    print("Found mob at:", sum_x // num, sum_y // num, "with size", num)


lud, llr, cud, clr = None, None, None, None

def move():
    global lud, llr, cud, clr
    force = [0, 0]
    player = [48, 96]
    mx = 0
    for mob in vec:
        if mob[2] > mx and mob[2] > 60:
            mx = mob[2]
            force = [mob[0], mob[1]]
    force[0] -= player[0]
    force[1] -= player[1]
    print("Max mob:", force)
    # for mob in vec:
    #     dist = int(math.sqrt((mob[0] - player[0]) * (mob[0] - player[0]) + (mob[1] - player[1]) * (mob[1] - player[1])))
    #     rad = Utils.get_rad_by_coord(mob[1] - player[1], player[0] - mob[0])
    #     print("Dist, rad:", dist, rad)
    #     weight = mob[2]
    #     # if dist < 15:
    #     #     weight = 3 * math.atan((dist - 15) / 5) * mob[2]
    #     # else:
    #     #     weight = math.atan((dist - 15) / 5) * mob[2]
    #     force[0] += weight * math.sin(rad)
    #     force[1] += weight * math.cos(rad)
    dist = math.sqrt(force[0] * force[0] + force[1] * force[1])
    if dist != 0:
        force[0] /= dist
        force[1] /= dist
    else:
        Florr.move()
        return
    print(force)
    if force[0] > 0.5:
        clr = 's'
    elif force[0] < -0.5:
        clr = 'w'
    else:
        clr = None
    if force[1] > 0.5:
        cud = 'd'
    elif force[1] < -0.5:
        cud = 'a'
    else:
        cud = None
    print("Pressed:", clr, cud)
    if lud != cud:
        if lud is not None:
            pyautogui.keyUp(lud)
        if cud is not None:
            pyautogui.keyDown(cud)
    if llr != clr:
        if llr is not None:
            pyautogui.keyUp(llr)
        if clr is not None:
            pyautogui.keyDown(clr)
    lud = cud
    llr = clr

if __name__ == "__main__":
    sys.setrecursionlimit(1500)

    pyscreeze.USE_IMAGE_NOT_FOUND_EXCEPTION = False
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    time.sleep(3)
    t = time.time_ns()
    Florr.init_distance_matrix()

    # Florr.visualize_distance()
    while True:
        get_screenshot()
        get_mobs()
        move()
        # Florr.move()
        # time.sleep(0.1)
        if keyboard.is_pressed('q'):
            break
        # break
        print((time.time_ns() - t) / 1000000)
        t = time.time_ns()
    Florr.init_distance_matrix()
    while True:
        t = time.time_ns()
        GetScreenshot()
        if Constants.DEBUGGING:
            print("Main loop used time(ms):", (time.time_ns() - t) / 1000000)
            print()
        if keyboard.is_pressed('v'):
            break
    pyautogui.keyUp(Florr.last_move)
    pid = os.getpid()
    os.kill(pid, signal.SIGTERM)
