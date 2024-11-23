import threading
import keyboard
import time
import random

def Foo():
    while not keyboard.is_pressed("v"):
        print("Foo!")
        time.sleep(random.random())

def Boo():
    while not keyboard.is_pressed("v"):
        print("Boo!")
        time.sleep(random.random())

if __name__ == "__main__":
    foo = threading.Thread(target=Foo)
    boo = threading.Thread(target=Boo)
    foo.start()
    boo.start()
    while not keyboard.is_pressed("v"):
        print("Hoo!")
        time.sleep(random.random())
    foo.join()
    boo.join()
