import collections
import pyautogui
import pytesseract
import pyscreeze
import mss
import mss.tools
import multiprocessing
import pygame
import numpy as np
import keyboard
import signal
import time
import os
import math
import cv2

class Constants:
    SCREENSHOT_LOCATION = 'screenshot.png'
    MAP_LOCATION = 'map.png'
    XP_LOCATION = 'xp.png'
    FLOWER_LOCATION = 'flower.png'
    FIRST_PETAL_LOCATION = 'FirstPetal.png'
    DEBUGGING = True
    IMG_LEN = 300
    ERR = 2147483647
    USE_SCREENSHOT = True
    MOVE_LEN = 3
    EPSILON = math.pi / 4
    DIST_XP_RATIO = 100  # TODO: tweak parameters
    ROTATING_SPEED = 4


class Utils:
    @staticmethod
    def distance_squared(point1, point2):
        return (int(point1[0]) - int(point2[0])) ** 2 + (int(point1[1]) - int(point2[1])) ** 2

    @staticmethod
    def mse(arr1, arr2):
        if len(arr1) != len(arr2):
            print("MSE function parameters has different lengths!")
            raise Exception
        cnt = 0
        for i in range(len(arr1)):
            cnt += (int(arr1[i]) - int(arr2[i])) * (int(arr1[i]) - int(arr2[i]))
        return cnt

    @staticmethod
    def mse_image(img1, img2):
        h1, w1 = img1.shape[:2]
        h2, w2 = img2.shape[:2]
        if h1 != h2 or w1 != w2:
            print("Two images does not have same size!")
            raise Exception
        count = 0
        for i in range(h1):
            for j in range(w1):
                pixel1 = img1[i][j]
                pixel2 = img2[i][j]
                count += Utils.mse(pixel1, pixel2)
        count /= (h1 * w1)
        return count

    @staticmethod
    def calculate_average_rad(coord_list):
        force = [0, 0]
        for coord in coord_list:
            force[0] += coord[0]
            force[1] += coord[1]
        return Utils.get_rad_by_coord(force[0], force[1])

    @staticmethod
    def close_to(color1, color2, sum_diff=1000):
        return Utils.mse(color1, color2) <= sum_diff

    @staticmethod
    def is_grey_or_white(color):
        return 0.8 < color[0] / color[1] < 1.2 and 0.8 < color[1] / color[2] < 1.2

    @staticmethod
    def get_rad_by_coord(x, y):
        rad = math.atan(y / x)
        if x < 0:
            rad += math.pi
        return (rad + math.pi * 2) % (math.pi * 2)


class Images:
    @staticmethod
    def get_screenshot():
        # Complexity: 28ms
        if Constants.USE_SCREENSHOT:
            pyautogui.screenshot(Constants.SCREENSHOT_LOCATION)
        return cv2.imread(Constants.SCREENSHOT_LOCATION)

    @staticmethod
    def get_region(top, left, width, height, location):
        # Complexity: 28ms
        if Constants.USE_SCREENSHOT:
            with mss.mss() as sct:
                region = {'top': top, 'left': left, 'width': width, 'height': height}
                img = sct.grab(region)
                mss.tools.to_png(img.rgb, img.size, output=location)
        return cv2.imread(location)  # (y, x)

    @staticmethod
    def get_map():
        # Complexity: 28ms
        return Images.get_region(129, 1600, 300, 300, Constants.MAP_LOCATION)

    @staticmethod
    def get_first_petal():
        return Images.get_region(925, 565, 70, 70, Constants.FIRST_PETAL_LOCATION)

    @staticmethod
    def get_flower():
        flower = (960, 593)
        radius = 40
        return Images.get_region(flower[1] - radius, flower[0] - radius, 2 * radius, 2 * radius, Constants.FLOWER_LOCATION)

    @staticmethod
    def get_xp_line():
        # Complexity: 28ms
        xp_line = Images.get_region(242, 126, 139, 13, Constants.XP_LOCATION)
        empty = np.array([14, 25, 4])
        h, w = xp_line.shape[:2]
        for y in range(0, h):
            for x in range(0, w):
                pixel = xp_line[y][x]
                if not Utils.is_grey_or_white(pixel):
                    xp_line[y][x] = empty
        return xp_line

    @staticmethod
    def save_all_exit_code():
        Images.get_screenshot()
        Images.get_map()
        Images.get_first_petal()
        Images.get_flower()
        Images.get_xp_line()
        _pid = os.getpid()
        os.kill(_pid, signal.SIGTERM)


class Bubbler:
    last_time_since_checked = time.time_ns() / 1000000000  # Seconds since epoch
    last_bubble_rad = 0
    is_update_radians = False
    is_update = True
    is_clockwise = True
    pressed_shift = False
    lt = time.time_ns()

    @staticmethod
    def stop_updating():
        Bubbler.is_update = False

    @staticmethod
    def update_bubble_rad():
        # Complexity: 260ms
        bubble_img = cv2.imread("Images/Bubble.PNG")
        radius = 40
        screenshot = Images.get_flower()
        # for i in range(63, 68):
        #     for j in range(20, 61):
        #         flag1, flag2 = False, False
        #         color_list = [(52, 221, 117), (255, 255, 255), (30, 22, 9), (75, 66, 197), (40, 93, 71), (65, 99, 32), (93, 115, 72)]
        #         for k in color_list:
        #             if Utils.close_to(k, screenshot[i][j]):
        #                 flag1 = True
        #         for m in range(i - 5, i + 6):
        #             for n in range(j - 5, j + 6):
        #                 if screenshot[m][n][0] >= 160 and screenshot[m][n][1] >= 200 and screenshot[m][n][2] >= 160:
        #                     flag2 = True
        #                     break
        #             if flag2:
        #                 break
        #         if flag1 and flag2:
        #             screenshot[i][j] = (152, 198, 109)
        cv2.imwrite(Constants.FLOWER_LOCATION, screenshot)
        bubble_list = []
        coord_list = []
        # cnt = 0
        for bubble in pyautogui.locateAll(bubble_img, screenshot, confidence=0.57):
            coord = pyautogui.center(bubble)
            # cv2.imwrite("Bubble" + str(cnt) + ".png", cv2.imread(Constants.FLOWER_LOCATION)[coord.y - 13:coord.y + 13, coord.x - 13:coord.x + 13])
            # cnt += 1
            is_new_bubble = True
            for prev_bubble in bubble_list:
                if Utils.distance_squared(coord,
                                          (prev_bubble[0] / prev_bubble[2], prev_bubble[1] / prev_bubble[2])) <= 50:
                    prev_bubble[0] += coord.x
                    prev_bubble[1] += coord.y
                    prev_bubble[2] += 1
                    is_new_bubble = False
                    break
            if is_new_bubble:
                bubble_list.append([coord.x, coord.y, 1])
        for bubble in bubble_list:
            coord = (bubble[0] / bubble[2] - radius, radius - bubble[1] / bubble[2])
            # Since y is reversed in computer coordinates
            coord_list.append(coord)
        if len(coord_list) != 0:
            Bubbler.last_bubble_rad = Utils.calculate_average_rad(coord_list)
            Bubbler.last_time_since_checked = time.time_ns() / 1000000000
            return True
        else:
            return False

    @staticmethod
    def update_clockwise_rotation():
        # Complexity: 39ms
        img = Images.get_first_petal()
        yin_yang = cv2.imread("Images/Petals/MYinYang.PNG")
        Bubbler.is_clockwise = (Utils.mse_image(img, yin_yang) > 1200)
        if Constants.DEBUGGING:
            print("Bubble orientation:", "Clockwise" if Bubbler.is_clockwise else "Anticlockwise")

    @staticmethod
    def forever_update_bubble_rad():
        while Bubbler.is_update:
            Bubbler.update_bubble_rad()
            Bubbler.update_clockwise_rotation()

    @staticmethod
    def get_rad():
        return (Bubbler.last_bubble_rad + 2 * math.pi - (2 * int(Bubbler.is_clockwise) - 1) * Constants.ROTATING_SPEED * (
                time.time_ns() / 1000000000 - Bubbler.last_time_since_checked)) % (2 * math.pi)

    @staticmethod
    def auto_bubble_with_keyboard():
        # Complexity: 227ms
        c = time.time_ns()
        last_move = open("log.txt").read()
        if last_move == "":
            return
        move_to_rad = {'a': 0, 's': math.pi / 2, 'd': math.pi, 'w': math.pi * 3 / 2}
        goal_rad = move_to_rad[last_move]
        rad = Bubbler.get_rad()
        if goal_rad == 0:
            is_bubble = (2 * math.pi - Constants.EPSILON <= rad or rad <= Constants.EPSILON)
        else:
            is_bubble = (goal_rad - Constants.EPSILON <= rad <= goal_rad + Constants.EPSILON)
        Bubbler.lt = time.time_ns()
        if is_bubble:
            if not Bubbler.pressed_shift:
                Bubbler.pressed_shift = True
                pyautogui.keyDown("shift")
                if Constants.DEBUGGING:
                    print("KEYDOWN: shift")
            l_bound = (goal_rad - Constants.EPSILON + 2 * math.pi) % (2 * math.pi)
            r_bound = (goal_rad + Constants.EPSILON) % (2 * math.pi)
            if (goal_rad == 0 and l_bound <= rad and Bubbler.is_clockwise) or \
                    (goal_rad == 0 and rad <= r_bound and not Bubbler.is_clockwise) or \
                    (goal_rad != 0 and l_bound <= rad <= goal_rad and Bubbler.is_clockwise) or \
                    (goal_rad != 0 and goal_rad <= rad <= r_bound + Constants.EPSILON and not Bubbler.is_clockwise):
                pyautogui.keyDown("1")
                if Constants.DEBUGGING:
                    print("Switch bubble orientation")
                Bubbler.last_bubble_rad = Bubbler.get_rad()
                Bubbler.last_time_since_checked = time.time_ns() / 1000000000
                Bubbler.is_clockwise = not Bubbler.is_clockwise
                pyautogui.keyUp("1")
        else:
            if Bubbler.pressed_shift:
                Bubbler.pressed_shift = False
                pyautogui.keyUp("shift")
                if Constants.DEBUGGING:
                    print("KEYUP: shift")

    @staticmethod
    def bubble_helper():
        # pygame.init()
        # bubble_screen = pygame.display.set_mode((500, 500))
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pyscreeze.USE_IMAGE_NOT_FOUND_EXCEPTION = False
        while not keyboard.is_pressed('v'):
            c = time.time_ns()
            # Florr.visualize_bubble_position(bubble_screen)
            Bubbler.auto_bubble_with_keyboard()
            Bubbler.is_update_radians = Bubbler.update_bubble_rad()
            Bubbler.update_clockwise_rotation()
            if Constants.DEBUGGING:
                print("Current radians:", Bubbler.get_rad())
                print("Is update radians:", Bubbler.is_update_radians)
                print("Bubble helper used time:", (time.time_ns() - c) / 1000000)
                print()


class Florr:
    last_move = ""
    last_location = None
    current_biome = None
    dist = np.full((Constants.IMG_LEN, Constants.IMG_LEN), Constants.ERR, dtype=int)
    dist_to_goal = np.full((Constants.IMG_LEN, Constants.IMG_LEN), Constants.ERR, dtype=int)

    @staticmethod
    def visualize_bubble_position(screen):
        pygame.event.get()
        screen.fill((255, 255, 255))
        if Bubbler.is_update_radians:
            pygame.draw.circle(screen, (0, 0, 255), [250, 250], 50, 50)
        else:
            pygame.draw.circle(screen, (0, 255, 0), [250, 250], 50, 50)
        rad = Bubbler.get_rad()
        pygame.draw.circle(screen, (255, 0, 0), [250 + math.cos(rad) * 80, 250 - math.sin(rad) * 80], 10, 5)
        pygame.display.update()

    @staticmethod
    def get_last_move():
        return Florr.last_move

    @staticmethod
    def get_current_location():
        # Complexity: 56ms
        florr_map = Images.get_map()
        h, w = florr_map.shape[:2]
        self_color = np.array([75, 222, 188])
        sumx, numx, sumy, numy = 0, 0, 0, 0
        if Florr.last_location is not None:
            for y in range(max(Florr.last_location[1] - 100, 0), min(Florr.last_location[1] + 100, 300)):
                for x in range(max(Florr.last_location[0] - 100, 0), min(Florr.last_location[0] + 100, 300)):
                    pixel = florr_map[y][x]
                    if Utils.close_to(pixel, self_color):
                        sumx += x
                        sumy += y
                        numx += 1
                        numy += 1
        else:
            for y in range(0, h):
                for x in range(0, w):
                    pixel = florr_map[y][x]
                    if Utils.close_to(pixel, self_color):
                        sumx += x
                        sumy += y
                        numx += 1
                        numy += 1
        if numx == 0 or numy == 0:
            print("Flower self not found in map!")
            raise Exception
        avg_x, avg_y = round(sumx / numx), round(sumy / numy)
        if Constants.DEBUGGING:
            print("Flower coordinates:", avg_x, avg_y)
        Florr.last_location = (avg_x, avg_y)
        return avg_x, avg_y

    @staticmethod
    def get_xp():
        # Complexity: 228ms
        xp_line = Images.get_xp_line()
        if Constants.DEBUGGING:
            cv2.imwrite(Constants.XP_LOCATION, xp_line)
        text = pytesseract.image_to_string(xp_line, config='--psm 7 -c tessedit_char_whitelist=0123456789/kmbXP')
        xp = ""
        for char in text:
            if char != '/':
                xp += char
            else:
                break
        if Constants.DEBUGGING:
            print("XP:", int(xp))
        return int(xp)

    @staticmethod
    def get_reward():
        # Complexity: 544ms
        # Calculate Distance Reward
        location = Florr.get_current_location()
        distance = Florr.dist[location[0]][location[1]]
        # Calculate XP Reward
        xp = Florr.get_xp()
        if Constants.DEBUGGING:
            print("Distance:", distance)
        return Constants.DIST_XP_RATIO * distance + int(xp)

    @staticmethod
    def visualize_distance():
        # Complexity: 315ms
        florr_map = Images.get_map()
        max_dist = 0
        for i in range(Constants.IMG_LEN):
            for j in range(Constants.IMG_LEN):
                if Florr.dist[i][j] != Constants.ERR:
                    max_dist = max(max_dist, Florr.dist[i][j])
        ratio = max_dist / 230
        if Constants.DEBUGGING:
            print("Maximum Distance:", max_dist)
        for i in range(0, Constants.IMG_LEN):
            for j in range(0, Constants.IMG_LEN):
                if Florr.dist[i][j] == Constants.ERR:
                    florr_map[j][i] = np.array([0, 0, 0])
                else:
                    florr_map[j][i] = np.array([Florr.dist[i][j] / ratio + 25, Florr.dist[i][j] / ratio + 25,
                                                Florr.dist[i][j] / ratio + 25])
        cv2.imshow("Pic", florr_map)
        cv2.waitKey(0)
        max_dist = 0
        for i in range(Constants.IMG_LEN):
            for j in range(Constants.IMG_LEN):
                if Florr.dist_to_goal[i][j] != Constants.ERR:
                    max_dist = max(max_dist, Florr.dist_to_goal[i][j])
        ratio = max_dist / 230
        if Constants.DEBUGGING:
            print("Maximum Distance:", max_dist)
        for i in range(0, Constants.IMG_LEN):
            for j in range(0, Constants.IMG_LEN):
                if Florr.dist_to_goal[i][j] == Constants.ERR:
                    florr_map[j][i] = np.array([0, 0, 0])
                else:
                    florr_map[j][i] = np.array([Florr.dist_to_goal[i][j] / ratio + 25, Florr.dist_to_goal[i][j] / ratio + 25,
                                                Florr.dist_to_goal[i][j] / ratio + 25])
        cv2.imshow("Pic", florr_map)
        cv2.waitKey(0)

    @staticmethod
    def get_biome_map_list():
        garden_map = cv2.imread("Images/Maps/GardenAntHell.PNG")
        desert_map = cv2.imread("Images/Maps/DesertMain.PNG")
        ocean_map = cv2.imread("Images/Maps/OceanMain.PNG")
        jungle_map = cv2.imread("Images/Maps/JungleMain.PNG")
        ant_hell_map = cv2.imread("Images/Maps/AntHellMain.PNG")
        sewer_map = cv2.imread("Images/Maps/SewersMain.PNG")
        map_list = [garden_map, desert_map, ocean_map, jungle_map, ant_hell_map, sewer_map]
        return map_list

    @staticmethod
    def get_biome():
        if Florr.current_biome is not None:
            return Florr.current_biome
        map_list = Florr.get_biome_map_list()
        florr_map = Images.get_map()
        current_map_index = -1
        for index, biome_map in enumerate(map_list):
            if Utils.mse_image(florr_map, biome_map) <= 15000:
                current_map_index = index
                break
        Florr.current_biome = current_map_index
        return current_map_index

    @staticmethod
    def get_biome_map():
        map_list = Florr.get_biome_map_list()
        return map_list[Florr.get_biome()]

    @staticmethod
    def get_origin():
        biome_index = Florr.get_biome()
        origin = [(72, 144), (157, 234), (140, 142), (100, 72), (0, 0), (0, 0)]
        return origin[biome_index]

    @staticmethod
    def is_death():
        pass  # TODO

    @staticmethod
    def init_distance_matrix():
        # Complexity: 685ms
        florr_map = Florr.get_biome_map()
        white = np.array([231, 242, 221])
        green = np.array([121, 226, 123])
        origin = Florr.get_origin()
        max_dist = -1
        max_coord = None
        q = collections.deque()
        q.append(origin)
        Florr.dist[origin[0]][origin[1]] = 0
        first_iteration = True
        while len(q) > 0:
            coord = q.popleft()
            if not first_iteration:
                pixel = florr_map[coord[1]][coord[0]]
                if Florr.dist[coord[0]][coord[1]] != Constants.ERR:
                    continue
                if not Utils.close_to(pixel, white) and \
                   not Utils.close_to(pixel, green) and \
                   not 120 <= pixel[0] == pixel[1] == pixel[2]:
                    continue
                Florr.dist[coord[0]][coord[1]] = min(Florr.dist[coord[0] + 1][coord[1]],
                                                     Florr.dist[coord[0] - 1][coord[1]],
                                                     Florr.dist[coord[0]][coord[1] + 1],
                                                     Florr.dist[coord[0]][coord[1] - 1],
                                                     Florr.dist[coord[0] - 1][coord[1] - 1],
                                                     Florr.dist[coord[0] - 1][coord[1] + 1],
                                                     Florr.dist[coord[0] + 1][coord[1] - 1],
                                                     Florr.dist[coord[0] + 1][coord[1] + 1]) + 1
            if Florr.dist[coord[0]][coord[1]] > max_dist:
                max_dist = Florr.dist[coord[0]][coord[1]]
                max_coord = coord
            q.append((coord[0] + 1, coord[1]))
            q.append((coord[0] - 1, coord[1]))
            q.append((coord[0], coord[1] + 1))
            q.append((coord[0], coord[1] - 1))
            q.append((coord[0] - 1, coord[1] - 1))
            q.append((coord[0] - 1, coord[1] + 1))
            q.append((coord[0] + 1, coord[1] - 1))
            q.append((coord[0] + 1, coord[1] + 1))
            first_iteration = False
        q.append(max_coord)
        Florr.dist_to_goal[max_coord[0]][max_coord[1]] = 0
        first_iteration = True
        while len(q) > 0:
            coord = q.popleft()
            if not first_iteration:
                pixel = florr_map[coord[1]][coord[0]]
                if Florr.dist_to_goal[coord[0]][coord[1]] != Constants.ERR:
                    continue
                if not Utils.close_to(pixel, white) and \
                   not Utils.close_to(pixel, green) and \
                   not 120 <= pixel[0] == pixel[1] == pixel[2]:
                    continue
                Florr.dist_to_goal[coord[0]][coord[1]] = min(Florr.dist_to_goal[coord[0] + 1][coord[1]],
                                                             Florr.dist_to_goal[coord[0] - 1][coord[1]],
                                                             Florr.dist_to_goal[coord[0]][coord[1] + 1],
                                                             Florr.dist_to_goal[coord[0]][coord[1] - 1],
                                                             Florr.dist_to_goal[coord[0] - 1][coord[1] - 1],
                                                             Florr.dist_to_goal[coord[0] - 1][coord[1] + 1],
                                                             Florr.dist_to_goal[coord[0] + 1][coord[1] - 1],
                                                             Florr.dist_to_goal[coord[0] + 1][coord[1] + 1]) + 1
            q.append((coord[0] + 1, coord[1]))
            q.append((coord[0] - 1, coord[1]))
            q.append((coord[0], coord[1] + 1))
            q.append((coord[0], coord[1] - 1))
            q.append((coord[0] - 1, coord[1] - 1))
            q.append((coord[0] - 1, coord[1] + 1))
            q.append((coord[0] + 1, coord[1] - 1))
            q.append((coord[0] + 1, coord[1] + 1))
            first_iteration = False

    @staticmethod
    def move():
        # Complexity: 550ms
        coord = Florr.get_current_location()
        min_dist_to_goal, min_index = Constants.ERR, 0
        new_movements = ['d', 'a', 's', 'w']
        move_len = Constants.MOVE_LEN
        while min_dist_to_goal == Constants.ERR and move_len >= 1:
            new_coords = [(coord[0] + move_len, coord[1]), (coord[0] - move_len, coord[1]),
                          (coord[0], coord[1] + move_len), (coord[0], coord[1] - move_len)]
            for index, new_coord in enumerate(new_coords):
                new_dist = Florr.dist_to_goal[new_coord[0]][new_coord[1]]
                if new_movements[index] == Florr.last_move:
                    new_dist -= 1.5
                if new_dist < min_dist_to_goal:
                    min_dist_to_goal = new_dist
                    min_index = index
            if min_dist_to_goal == 0:
                move_len -= 1
        choice = new_movements[min_index]
        if Florr.last_move != choice:
            if Florr.last_move != "":
                if Constants.DEBUGGING:
                    print("KEYUP:", Florr.last_move)
                pyautogui.keyUp(Florr.last_move)
            if Constants.DEBUGGING:
                print("KEYDOWN:", choice)
            pyautogui.keyDown(choice)
        if Constants.DEBUGGING:
            print("Current direction:", choice)
        Florr.last_move = choice
        with open("log.txt", "w") as file:
            file.write(Florr.last_move)
            file.close()


if __name__ == "__main__":
    pyscreeze.USE_IMAGE_NOT_FOUND_EXCEPTION = False
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    time.sleep(3)
    # Images.save_all_exit_code()
    Florr.init_distance_matrix()
    # Florr.visualize_distance()
    auto_bubble = multiprocessing.Process(target=Bubbler.bubble_helper)
    auto_bubble.start()
    while True:
        t = time.time_ns()
        Florr.move()
        if Constants.DEBUGGING:
            print("Main loop used time(ms):", (time.time_ns() - t) / 1000000)
            print()
        if keyboard.is_pressed('v'):
            break
    pyautogui.keyUp(Florr.last_move)
    if Bubbler.pressed_shift:
        pyautogui.keyUp("shift")
    auto_bubble.join()
    pid = os.getpid()
    os.kill(pid, signal.SIGTERM)

'''

'''
