import time
from PIL import Image
from Joystick import Joystick
from Title import Title
from Chase import Chase
from config import FRAME_TIME, SCREEN


def main():
    joystick = Joystick()
    title = Title(joystick)
    chase = None
    state = "TITLE"                           # 지금 화면: TITLE 또는 CHASE

    while True:
        start = time.time()
        joystick.update()                     # 버튼 상태 읽기

        if state == "TITLE":
            result = title.update()           # "start" / "quit" / None
            if result == "start":
                chase = Chase(joystick)       # 새 게임이니까 새로 만듦
                state = "CHASE"
            elif result == "quit":
                break
            image = title.draw()

        elif state == "CHASE":
            chase.update()
            image = chase.draw()

        joystick.disp.image(image.convert("RGB"))
        time.sleep(max(0, FRAME_TIME - (time.time() - start)))   # 프레임 속도 고정

    # 종료: 화면을 검게 지우고 백라이트 끄기
    joystick.disp.image(Image.new("RGB", (SCREEN, SCREEN)))
    joystick.backlight.value = False


if __name__ == "__main__":
    main()
