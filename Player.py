from PIL import Image
from config import BASE_DIR, TILE, SPEED, HIDE_SPOTS

HIT_W, HIT_H = 10, 6                  # 발밑 충돌 박스
DOWN, UP, RIGHT, LEFT = 0, 1, 2, 3    # 스프라이트 시트 줄 순서
WALK = [1, 0, 2, 0]                   # 걷기 프레임 순서


class Player:
    def __init__(self, x, y):
        self.x, self.y = x, y                       # 그림 왼쪽 위 (픽셀)
        self.sheet = Image.open(f"{BASE_DIR}/assets/sprites/character_hangbung.png").convert("RGBA")
        self.facing = DOWN
        self.step = 0                               # 걸은 프레임 수 (애니메이션용)
        self.hidden = False

    def update(self, joystick, game_map):
        # 숨어 있으면 A로 나오기만 가능
        if self.hidden:
            if joystick.pressed["A"]:
                self.hidden = False
            return

        if joystick.pressed["A"]:
            self.try_hide(game_map)
            return
        
        # 이동 속도
        dx = dy = 0
        if joystick.held["left"]:  dx -= SPEED
        if joystick.held["right"]: dx += SPEED
        if joystick.held["up"]:    dy -= SPEED
        if joystick.held["down"]:  dy += SPEED

        # 바라보는 방향 (대각선이면 좌우 우선)
        if dx < 0:   self.facing = LEFT
        elif dx > 0: self.facing = RIGHT
        elif dy < 0: self.facing = UP
        elif dy > 0: self.facing = DOWN

        moved = False
        if dx != 0 and self.can_move(game_map, self.x + dx, self.y):
            self.x += dx                            # x만 먼저
            moved = True
        if dy != 0 and self.can_move(game_map, self.x, self.y + dy):
            self.y += dy                            # 그다음 y만
            moved = True
        self.step = self.step + 1 if moved else 0

    def hitbox(self, x, y):
        left = x + (16 - HIT_W) // 2
        top = y + 24 - HIT_H
        return left, top, left + HIT_W - 1, top + HIT_H - 1

    def foot_tile(self):
        # 발 가운데가 있는 칸
        left, top, right, bottom = self.hitbox(self.x, self.y)
        return (left + right) // 2 // TILE, (top + bottom) // 2 // TILE

    def set_tile(self, tx, ty): 
        # 발이 (tx, ty) 칸에 오도록 위치 맞추기
        self.x, self.y = tx * TILE, ty * TILE - 8

    def can_move(self, game_map, x, y):
        left, top, right, bottom = self.hitbox(x, y)
        for px, py in [(left, top), (right, top), (left, bottom), (right, bottom)]:
            if game_map.is_blocked(px // TILE, py // TILE):
                return False
        return True

    def try_hide(self, game_map):
        # 바라보는 방향 한 칸 앞이 숨는 곳이면 숨기
        tx, ty = self.foot_tile()
        front = {DOWN: (0, 1), UP: (0, -1), RIGHT: (1, 0), LEFT: (-1, 0)}[self.facing]
        if game_map.get(tx + front[0], ty + front[1]) in HIDE_SPOTS:
            self.hidden = True

    def draw(self, image, camera_x, camera_y):
        if self.hidden:
            return                                  # 숨으면 안 그림
        col = WALK[self.step // 4 % 4] if self.step > 0 else 0
        frame = self.sheet.crop((col * 16, self.facing * 24, col * 16 + 16, self.facing * 24 + 24))
        image.alpha_composite(frame, (self.x - camera_x, self.y - camera_y))
