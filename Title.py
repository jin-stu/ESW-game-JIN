import random
from PIL import Image, ImageDraw
from config import SCREEN, FONT_LARGE, FONT_BOLD, FONT_NORMAL, FONT_SMALL


class Title:
    def __init__(self, joystick):
        self.joystick = joystick
        self.menu = ["게임 시작", "게임 종료"]
        self.cursor = 0
        self.best = None                          # 최고 기록(초). 기록 저장은 나중에 추가
        self.background = self.build_background() # 바뀌지 않는 부분은 한 번만 그림

    def build_background(self):
        image = Image.new("RGB", (SCREEN, SCREEN), (14, 14, 34))
        draw = ImageDraw.Draw(image)

        # 밤하늘 별 (seed를 고정해서 매번 같은 위치)
        random.seed(7)
        for i in range(40):
            x = random.randint(0, SCREEN - 1)
            y = random.randint(0, 140)
            draw.point((x, y), fill=(200, 200, 230))

        # 제목
        draw.text((120, 80), "Hide on Bush", font=FONT_LARGE, fill=(236, 236, 250), anchor="mm")
        return image

    def update(self):
        # 위/아래로 메뉴 이동, A로 선택
        if self.joystick.pressed["up"]:
            self.cursor = (self.cursor - 1) % len(self.menu)
        if self.joystick.pressed["down"]:
            self.cursor = (self.cursor + 1) % len(self.menu)
        if self.joystick.pressed["A"]:
            if self.cursor == 0:
                return "start"
            else:
                return "quit"
        return None

    def draw(self):
        image = self.background.copy()
        draw = ImageDraw.Draw(image)

        for i in range(len(self.menu)):
            y = 160 + i * 24
            if i == self.cursor:
                draw.text((120, y), "> " + self.menu[i] + " <", font=FONT_BOLD, fill=(255, 210, 90), anchor="mm")
            else:
                draw.text((120, y), self.menu[i], font=FONT_NORMAL, fill=(140, 140, 160), anchor="mm")

        if self.best is None:
            best = "--"
        else:
            best = f"{self.best // 60:02d}:{self.best % 60:02d}"
        draw.text((120, 222), "최고 기록  " + best, font=FONT_SMALL, fill=(120, 120, 150), anchor="mm")
        return image
