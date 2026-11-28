from PIL import Image, ImageDraw
from Map import Map
from Player import Player
from Chaser import Chaser
from config import SCREEN, TILE, FPS, EXITS, ENTER_DELAY, FONT_SMALL


class Chase:
    def __init__(self, joystick):
        self.joystick = joystick
        self.maps = {}                      # 한 번 만든 방은 저장해 두고 다시 씀
        self.player = Player(0, 0)
        self.change_room("classroom1", 13, 13)
        self.chaser = Chaser("classroom1", 24, 4)   # 1단계: 시작할 때 같은 교실 앞쪽에 있음
        self.frames = 0                     # 버틴 프레임 수 (FPS로 나누면 초)
        self.enter_timer = 0                # 술래가 따라 들어오기까지 남은 프레임 (0이면 따라오는 중 아님)
        self.enter_room = None              # 술래가 들어올 방
        self.enter_door = None              # 술래가 들어올 문 칸 (E)
        self.enter_spot = None              # 플레이어가 그 방에 들어온 칸
        self.veil = Image.new("RGBA", (SCREEN, SCREEN), (0, 0, 10, 200))   # 숨었을 때 시야 제한

    def change_room(self, room, tx, ty):
        if room not in self.maps:
            self.maps[room] = Map(room)
        self.room = room
        self.map = self.maps[room]
        self.player.set_tile(tx, ty)

    def update(self):
        # 반환값: 게임이 끝났으면 엔딩 종류("caught"), 아니면 None
        self.frames += 1
        self.player.update(self.joystick, self.map)
        self.check_exit()

        self.update_enter_timer()

        # 술래는 자기가 있는 방의 맵에서 움직임 (다른 방에 있어도 문 쪽으로 걸어감)
        visible = self.chaser.room == self.room and not self.player.hidden
        self.chaser.update(self.maps[self.chaser.room], self.player.foot_tile(), visible)
        if visible and self.is_caught():
            return "caught"
        return None

    def is_caught(self):
        # 두 발밑 박스가 겹치면 잡힘
        pl, pt, pr, pb = self.player.hitbox(self.player.x, self.player.y)
        cl, ct, cr, cb = self.chaser.hitbox(self.chaser.x, self.chaser.y)
        return pl <= cr and cl <= pr and pt <= cb and ct <= pb

    def check_exit(self):
        # 발이 통로 칸에 닿으면 연결된 방으로 이동
        tx, ty = self.player.foot_tile()
        key = (self.room, tx, ty)
        if key in EXITS:
            next_room, nx, ny = EXITS[key]
            if self.chaser.room == self.room:
                self.chaser.follow((tx, ty))        # 같은 방에 있던 술래는 나간 문 쪽으로
            self.change_room(next_room, nx, ny)
            self.player_entered(next_room, nx, ny)

    def player_entered(self, room, tx, ty):
        # 플레이어가 room의 (tx, ty)로 들어옴 -> 술래가 따라 들어올 준비
        if self.chaser.room == room:
            self.enter_timer = 0                    # 술래가 있는 방으로 돌아옴: 따라오기 취소
            return
        self.enter_room = room
        self.enter_door = self.door_next_to(tx, ty)
        self.enter_spot = (tx, ty)
        if self.enter_timer == 0:                   # 이미 세고 있으면 시간은 그대로, 들어올 곳만 바꿈
            self.enter_timer = ENTER_DELAY * FPS

    def door_next_to(self, tx, ty):
        # 도착 칸 바로 옆의 통로(E) 칸 (문은 모두 방의 왼쪽/오른쪽 벽에 있음)
        for dx in (-1, 1):
            if self.map.get(tx + dx, ty) == "E":
                return (tx + dx, ty)
        return (tx, ty)

    def update_enter_timer(self):
        if self.enter_timer > 0:
            self.enter_timer -= 1
            if self.enter_timer == 0:
                self.chaser.enter(self.enter_room, self.enter_door, self.enter_spot)

    def draw_bubble(self, image, x, y, text):
        # (x, y): 말풍선 꼬리 끝 위치 (화면 좌표)
        draw = ImageDraw.Draw(image)
        w = int(draw.textlength(text, font=FONT_SMALL)) + 8
        left = min(max(x - w // 2, 2), SCREEN - w - 2)        # 화면 밖으로 안 나가게
        top = max(y - 20, 2)
        draw.rounded_rectangle((left, top, left + w, top + 16), 4, fill=(245, 240, 245), outline=(40, 20, 40))
        draw.polygon([(x - 3, top + 16), (x + 3, top + 16), (x, top + 20)], fill=(245, 240, 245))
        draw.text((left + 4, top + 2), text, font=FONT_SMALL, fill=(150, 20, 50))

    def seconds(self):
        return self.frames // FPS

    def camera(self, center, map_size):
        if map_size <= SCREEN:
            return (map_size - SCREEN) // 2                  # 맵이 화면보다 작으면 가운데 정렬
        return min(max(center - SCREEN // 2, 0), map_size - SCREEN)

    def draw(self):
        # 카메라: 플레이어를 가운데에 두되 맵 밖은 안 보이게
        cx = self.camera(self.player.x + 8, self.map.width * TILE)
        cy = self.camera(self.player.y + 12, self.map.height * TILE)
        image = self.map.draw(cx, cy)

        # 화면 아래쪽(y가 큰) 캐릭터를 나중에 그려야 앞에 서 있는 것처럼 보임
        if self.chaser.room == self.room and self.chaser.y < self.player.y:
            self.chaser.draw(image, cx, cy)
            self.player.draw(image, cx, cy)
        elif self.chaser.room == self.room:
            self.player.draw(image, cx, cy)
            self.chaser.draw(image, cx, cy)
        else:
            self.player.draw(image, cx, cy)

        if self.player.hidden:
            image.alpha_composite(self.veil)

        # 두리번거릴 때 말풍선 (시야 제한 위에 그려서 숨어 있어도 보임)
        if self.chaser.room == self.room and self.chaser.look > 0:
            self.draw_bubble(image, self.chaser.x - cx + 8, self.chaser.y - cy - 4, "어디 있어?")

        # 버틴 시간 (화면 좌표에 바로 그림 -> 카메라와 상관없이 항상 왼쪽 위)
        s = self.seconds()
        ImageDraw.Draw(image).text((6, 4), f"{s // 60:02d}:{s % 60:02d}", font=FONT_SMALL, fill=(255, 255, 255))
        return image
