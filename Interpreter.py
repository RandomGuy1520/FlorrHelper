import pyautogui
import pyscreeze
import cv2
from Helper import Constants, Utils, Images, Florr

# TODO: Fill rest of ocean and sewer mob pics
# e.g. Sewer spider, ocean jellyfish.

Garden = [
    "Images/Mobs/Garden/Worker_Ant.png",
    "Images/Mobs/Garden/Baby_Ant.png",
    "Images/Mobs/Garden/Soldier_Ant.png",
    "Images/Mobs/Garden/Queen_Ant.png",
    "Images/Mobs/Garden/Ant_Hole.png",
    "Images/Mobs/Garden/Bee.png",
    "Images/Mobs/Garden/Bumble_Bee.png",
    "Images/Mobs/Garden/Centipede.png",
    "Images/Mobs/Garden/Dandelion.png",
    "Images/Mobs/Garden/Hornet.png",
    "Images/Mobs/Garden/Rock.png",
    "Images/Mobs/Garden/Spider.png",
    "Images/Mobs/Garden/Ladybug.png"
]

Desert = [
    "Images/Mobs/Desert/Baby_Fire_Ant.png",
    "Images/Mobs/Desert/Worker_Fire_Ant.png",
    "Images/Mobs/Desert/Soldier_Fire_Ant.png",
    "Images/Mobs/Desert/Queen_Fire_Ant.png",
    "Images/Mobs/Desert/Desert_Centipede.png",
    "Images/Mobs/Desert/Beetle.png",
    "Images/Mobs/Desert/Cactus.png",
    "Images/Mobs/Desert/Evil_Centipede.png",
    "Images/Mobs/Desert/Fire_Ant_Burrow.png",
    "Images/Mobs/Desert/Sandstorm.png",
    "Images/Mobs/Desert/Shiny_Ladybug.png"
]

Ocean = [
    "Images/Mobs/Ocean/Crab.png",
    "Images/Mobs/Ocean/Leech.png",
    "Images/Mobs/Ocean/Shell.png",
    "Images/Mobs/Ocean/Sponge.png",
    "Images/Mobs/Ocean/Starfish.png"
]

Jungle = [
    "Images/Mobs/Jungle/Soldier_Termite.png",
    "Images/Mobs/Jungle/Baby_Termite.png",
    "Images/Mobs/Jungle/Worker_Termite.png",
    "Images/Mobs/Jungle/Jungle_Ladybug.png",
    "Images/Mobs/Jungle/Bush.png",
    "Images/Mobs/Jungle/Firefly.png",
    "Images/Mobs/Jungle/Mantis.png",
    "Images/Mobs/Jungle/Termite_Mound.png",
    "Images/Mobs/Jungle/Wasp.png",
    "Images/Mobs/Jungle/Leafbug.png",
    "Images/Mobs/Jungle/Termite_Overmind.png"
]

Ant_Hell = [
    "Images/Mobs/Ant/Egg.png",
    "Images/Mobs/Ant/Baby_Ant.png",
    "Images/Mobs/Ant/Worker_Ant.png",
    "Images/Mobs/Ant/Soldier_Ant.png",
    "Images/Mobs/Ant/Queen_Ant.png",
    "Images/Mobs/Ant/Fire_Ant_Egg.png",
    "Images/Mobs/Ant/Baby_Fire_Ant.png",
    "Images/Mobs/Ant/Soldier_Fire_Ant.png",
    "Images/Mobs/Ant/Worker_Fire_Ant.png",
    "Images/Mobs/Ant/Queen_Fire_Ant.png",
    "Images/Mobs/Ant/Baby_Termite.png",
    "Images/Mobs/Ant/Worker_Termite.png",
    "Images/Mobs/Ant/Soldier_Termite.png",
    "Images/Mobs/Ant/Termite_Overmind.png"
]

Sewers = [
    "Images/Mobs/Sewers/Fly.png",
    "Images/Mobs/Sewers/Moth.png",
    "Images/Mobs/Sewers/Roach.png",
]

Hel = [
    "Images/Mobs/Hel/Gambler.png",
    "Images/Mobs/Hel/Hel_Centipede.png",
    "Images/Mobs/Hel/Hel_Wasp.png",
    "Images/Mobs/Hel/Hel_Beetle.png",
    "Images/Mobs/Hel/Hel_Spider.png"
]

Biomes = [Garden, Desert, Ocean, Jungle, Ant_Hell, Sewers, Hel]

if __name__ == "__main__":
    pyscreeze.USE_IMAGE_NOT_FOUND_EXCEPTION = False
    mobs_location = Biomes[Florr.get_biome()]
    for location in mobs_location:
        print(location)
        results = pyautogui.locateOnScreen(cv2.imread(location)[5:45, 5:45], confidence=0.4)
        print(results)
        if results is not None:
            cv2.imshow("LOL", Images.get_screenshot()[results.top:results.top+results.height, results.left:results.left + results.width])
            cv2.waitKey(0)
