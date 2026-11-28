from PIL import Image, ImageDraw
from config import SCREEN, FONT_LARGE, FONT_NORMAL, FONT_SMALL

# 엔딩 종류 -> (제목, 설명). 탈출 엔딩 등은 여기에 한 줄씩 추가
ENDINGS = {
    "caught": ("오늘은 이제 안녕", "아름이에게 잡혔다"),
}


class Ending:
    def __init__(self, joystick, kind, seconds, new_best):
        self.joystick = joystick
        self.title, self.message = ENDINGS[kind]
        self.seconds = seconds
        self.new_best = new_best            # 최고 기록을 새로 세웠는지

    def update(self):
        if self.joystick.pressed["A"]:
            return "title"
        return None

    def draw(self):
        image = Image.new("RGB", (SCREEN, SCREEN), (10, 0, 6))
        draw = ImageDraw.Draw(image)
        s = self.seconds
        draw.text((120, 70), self.title, font=FONT_LARGE, fill=(230, 60, 90), anchor="mm")
        draw.text((120, 104), self.message, font=FONT_NORMAL, fill=(200, 180, 190), anchor="mm")
        draw.text((120, 146), f"버틴 시간  {s // 60:02d}:{s % 60:02d}", font=FONT_NORMAL, fill=(230, 230, 240), anchor="mm")
        if self.new_best:
            draw.text((120, 168), "최고 기록!", font=FONT_SMALL, fill=(255, 210, 90), anchor="mm")
        draw.text((120, 214), "A: 타이틀로", font=FONT_SMALL, fill=(150, 150, 170), anchor="mm")
        return image
