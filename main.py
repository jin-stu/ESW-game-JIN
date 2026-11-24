import time
from Joystick import Joystick
from Chase import Chase
from config import FRAME_TIME

def main():
    joystick = Joystick()
    chase = Chase(joystick)
    while True:
        start = time.time()
        joystick.update()
        chase.update()
        image = chase.draw()
        joystick.disp.image(image.convert("RGB"))
        time.sleep(max(0, FRAME_TIME - (time.time() - start)))

if __name__ == "__main__":
    main()