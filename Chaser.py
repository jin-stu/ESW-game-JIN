import random
from collections import deque
from PIL import Image
from config import BASE_DIR, TILE, CHASER_SPEED

HIT_W, HIT_H = 10, 6                  # 발밑 충돌 박스 (플레이어와 같은 크기)
DOWN, UP, RIGHT, LEFT = 0, 1, 2, 3    # 스프라이트 시트 줄 순서
# BFS에서 갈 수 있는 8방향
DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

LOOK_FRAMES = 40                      # 한 자리에서 두리번거리는 시간 (20fps -> 2초)
SEARCH_RADIUS = 4                     # 마지막으로 본 곳에서 몇 칸 안쪽을 찾아다닐지


class Chaser:
    def __init__(self, room, tx, ty):
        self.room = room                    # 술래가 지금 있는 방
        self.sheet = Image.open(f"{BASE_DIR}/assets/sprites/character_areum_yandere.png").convert("RGBA")
        self.speed = CHASER_SPEED           # 나중에 난이도·질주 능력에서 바꿀 값
        self.facing = DOWN
        self.step = 0                       # 걸은 프레임 수 (애니메이션용)
        self.state = "chase"                # chase: 쫓는 중 / search: 놓쳐서 찾는 중 / follow: 나간 문으로 가는 중
        self.last_seen = (tx, ty)           # 플레이어를 마지막으로 본 칸
        self.look = 0                       # 두리번거린 프레임 수 (0이면 걷는 중)
        self.set_tile(tx, ty)

    def set_tile(self, tx, ty):
        # 발이 (tx, ty) 칸에 오도록 위치 맞추기 (Player와 같은 방식)
        self.x, self.y = tx * TILE, ty * TILE - 8
        self.target = (tx, ty)              # 지금 걸어가는 다음 칸
        self.goal = (tx, ty)                # 최종 목적지 칸

    def hitbox(self, x, y):
        left = x + (16 - HIT_W) // 2
        top = y + 24 - HIT_H
        return left, top, left + HIT_W - 1, top + HIT_H - 1

    def foot_tile(self):
        left, top, right, bottom = self.hitbox(self.x, self.y)
        return (left + right) // 2 // TILE, (top + bottom) // 2 // TILE

    def bfs(self, game_map, start):
        # start에서 갈 수 있는 모든 칸을 가까운 순서로 방문
        # 반환: {칸: 어디서 왔는지} -> 경로 찾기와 근처 칸 고르기에 같이 사용
        queue = deque([start])
        came_from = {start: None}
        while queue:
            cur = queue.popleft()
            for dx, dy in DIRS:
                nx, ny = cur[0] + dx, cur[1] + dy
                if (nx, ny) in came_from:   # 이미 방문한 칸
                    continue
                if game_map.is_blocked(nx, ny):
                    continue
                # 대각선은 양옆 두 칸이 모두 비어 있을 때만 (책상 모서리 끼기 방지)
                if dx != 0 and dy != 0:
                    if game_map.is_blocked(cur[0] + dx, cur[1]) or game_map.is_blocked(cur[0], cur[1] + dy):
                        continue
                came_from[(nx, ny)] = cur
                queue.append((nx, ny))
        return came_from

    def next_tile(self, game_map, start, goal):
        # start에서 goal까지 가장 짧은 길의 첫 칸
        if start == goal:
            return start
        came_from = self.bfs(game_map, start)
        if goal not in came_from:           # 갈 수 없으면 제자리
            return start
        tile = goal                         # goal에서 거꾸로 따라가서 start 바로 다음 칸 찾기
        while came_from[tile] != start:
            tile = came_from[tile]
        return tile

    def random_tile_near(self, game_map, center):
        # center에서 SEARCH_RADIUS칸 안쪽, 걸어서 갈 수 있는 바닥 칸 하나를 무작위로
        came_from = self.bfs(game_map, self.target)
        candidates = []
        for (tx, ty) in came_from:
            near = abs(tx - center[0]) <= SEARCH_RADIUS and abs(ty - center[1]) <= SEARCH_RADIUS
            if near and game_map.get(tx, ty) == "." and (tx, ty) != self.target:
                candidates.append((tx, ty))
        if len(candidates) == 0:
            return self.target
        return random.choice(candidates)

    def update(self, game_map, player_tile, player_visible):
        # player_visible: 같은 방에 있고 숨지 않았으면 True
        if player_visible:
            # 보이면 쫓아감
            self.state = "chase"
            self.last_seen = player_tile
            self.goal = player_tile
            self.look = 0
        elif self.state == "chase":
            # 방금 놓침 -> 마지막으로 본 곳으로
            self.state = "search"
            self.goal = self.last_seen

        if self.at_target():
            if self.target == self.goal and self.state == "search":
                self.look_around(game_map)  # 목적지에 도착: 두리번
                return
            if self.target == self.goal and self.state == "follow":
                self.step = 0               # 문 앞에 도착: 따라 들어갈 때까지 대기
                return
            self.target = self.next_tile(game_map, self.target, self.goal)
        self.move_to_target()

    def follow(self, door):
        # 플레이어가 이 방에서 나감 -> 나간 문 쪽으로 걸어감
        self.state = "follow"
        self.goal = door
        self.look = 0

    def enter(self, room, door, spot):
        # 다른 방의 문(door)으로 들어와서, 플레이어가 들어온 자리(spot)부터 찾기 시작
        self.room = room
        self.set_tile(door[0], door[1])
        self.state = "search"
        self.last_seen = spot
        self.goal = spot
        self.look = 0

    def look_around(self, game_map):
        # 제자리에서 방향을 바꿔 가며 두리번, 시간이 지나면 근처 다른 칸으로
        self.step = 0
        self.look += 1
        if self.look % 10 == 1:                 # 0.5초마다 고개 돌리기
            self.facing = random.choice([DOWN, UP, RIGHT, LEFT])
        if self.look >= LOOK_FRAMES:
            self.look = 0
            self.goal = self.random_tile_near(game_map, self.last_seen)

    def at_target(self):
        return self.x == self.target[0] * TILE and self.y == self.target[1] * TILE - 8

    def move_to_target(self):
        # 목표 칸 쪽으로 speed만큼 이동 (남은 거리가 더 짧으면 딱 그만큼만)
        target_x, target_y = self.target[0] * TILE, self.target[1] * TILE - 8
        dx = max(-self.speed, min(self.speed, target_x - self.x))
        dy = max(-self.speed, min(self.speed, target_y - self.y))
        self.x += dx
        self.y += dy

        # 바라보는 방향 (대각선이면 좌우 우선)
        if dx < 0:   self.facing = LEFT
        elif dx > 0: self.facing = RIGHT
        elif dy < 0: self.facing = UP
        elif dy > 0: self.facing = DOWN

        if dx != 0 or dy != 0:
            self.step += 1
        else:
            self.step = 0

    def draw(self, image, camera_x, camera_y):
        if self.step > 0:
            col = self.step // 4 % 4
        else:
            col = 1
        frame = self.sheet.crop((col * 16, self.facing * 24, col * 16 + 16, self.facing * 24 + 24))
        image.alpha_composite(frame, (self.x - camera_x, self.y - camera_y))
