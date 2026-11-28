import time
from PIL import Image
from Joystick import Joystick
from Title import Title
from Chase import Chase
from Ending import Ending
from config import FRAME_TIME, SCREEN


def main():
    joystick = Joystick()
    title = Title(joystick)
    chase = None
    ending = None
    state = "TITLE"                           # 지금 화면: TITLE, CHASE, ENDING

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
            result = chase.update()           # 엔딩 종류("caught") / None
            image = chase.draw()
            if result is not None:
                seconds = chase.seconds()
                new_best = title.best is None or seconds > title.best
                if new_best:
                    title.best = seconds      # 최고 기록 갱신 (파일 저장은 나중에)
                ending = Ending(joystick, result, seconds, new_best)
                state = "ENDING"

        elif state == "ENDING":
            if ending.update() == "title":
                state = "TITLE"
            image = ending.draw()

        joystick.disp.image(image.convert("RGB"))
        time.sleep(max(0, FRAME_TIME - (time.time() - start)))   # 프레임 속도 고정

    # 종료: 화면을 검게 지우고 백라이트 끄기
    joystick.disp.image(Image.new("RGB", (SCREEN, SCREEN)))
    joystick.backlight.value = False


if __name__ == "__main__":
    main()
