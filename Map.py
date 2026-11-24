from PIL import Image
from config import BASE_DIR, TILE, SCREEN, BLOCKED, ROOMS

TILE_DIR = f"{BASE_DIR}/assets/tiles"

# 타일 묶음별 16x16 타일
TILESETS = {
    "classroom": {
        "X": "classroom/classroom_wall_top.png",
        "U": "classroom/classroom_wall_upper.png",
        "L": "classroom/classroom_wall_lower.png",
        ".": "classroom/classroom_floor.png",
        "D": "classroom/classroom_desk.png",
        "C": "classroom/classroom_chair.png",
    },
    "hallway": {
        "X": "classroom/classroom_wall_top.png",
        "U": "classroom/classroom_wall_upper.png",
        "L": "classroom/classroom_wall_lower.png",
        ".": "hallway/hallway_floor.png",
    },
    "toilet": {
        "X": "classroom/classroom_wall_top.png",
        "U": "toilet/toilet_wall_upper.png",
        "L": "toilet/toilet_wall_lower.png",
        ".": "toilet/toilet_floor.png",
    },
    "computerroom": {                     
        "X": "classroom/classroom_wall_top.png",
        "W": "computerroom/computerroom_wall.png",
        "U": "computerroom/computerroom_wall_upper.png",
        "L": "computerroom/computerroom_wall_lower.png",
        ".": "classroom/classroom_floor.png",
        "K": "computerroom/computerroom_table.png",
        "I": "computerroom/computerroom_chair.png",
    },
}

# 물건 칸 밑에 깔 바탕 타일
BASE_OF = {"B": "U", "G": "U", "M": "L", "P": "L",
           "T": ".", "H": ".", "S": ".", "s": ".", "E": "."}

# 타일보다 큰 물건 -> (그림, 가로 칸 수, 세로 칸 수, y 보정)
OBJECTS = {
    "B": ("classroom/classroom_blackboard.png", 4, 1, -4),
    "T": ("classroom/classroom_lectern.png", 2, 2, 0),
    "G": ("hallway/hallway_glassdoor.png", 2, 2, 0),
    "S": ("hallway/hallway_stairs_up.png", 2, 2, 0),
    "s": ("hallway/hallway_stairs_down.png", 2, 2, 0),
    "M": ("toilet/toilet_sinks.png", 3, 1, 0),
    "P": ("toilet/toilet_urinal.png", 1, 1, 0),
    "H": ("toilet/toilet_stall.png", 2, 2, 0),
}


def load_image(path):
    return Image.open(f"{TILE_DIR}/{path}").convert("RGBA")


class Map:
    def __init__(self, room):
        file_name, tileset = ROOMS[room]
        self.grid = self.load(file_name)
        self.width = max(len(row) for row in self.grid)
        self.height = len(self.grid)
        self.grid = [row.ljust(self.width, "X") for row in self.grid]   # 짧은 줄은 오른쪽을 벽으로 채움

        self.tiles = {ch: load_image(path) for ch, path in TILESETS[tileset].items()}
        self.exit_shadow = load_image("common/exit_shadow.png")                     # 왼쪽 통로용
        self.exit_shadow_right = self.exit_shadow.transpose(Image.FLIP_LEFT_RIGHT)  # 오른쪽 통로용

        self.background = self.build_background()   # 방 들어올 때 한 번만 그림

    def load(self, name):
        path = f"{BASE_DIR}/data/maps/{name}.txt"
        grid = []
        with open(path, encoding="utf-8-sig") as f:     # -sig: 파일 앞 BOM 자동 제거
            for line in f:
                line = line.rstrip("\n")
                if line.strip() == "" or line.strip().startswith("#"):
                    continue                             # 빈 줄과 주석 줄은 건너뜀
                grid.append(line)
        return grid

    def is_anchor(self, x, y, w, h):
        # 같은 문자가 이어진 덩어리의 왼쪽 위부터 w x h 칸마다 한 번씩 그림
        ch = self.grid[y][x]
        left = x
        while left > 0 and self.grid[y][left - 1] == ch:
            left -= 1
        top = y
        while top > 0 and self.grid[top - 1][x] == ch:
            top -= 1
        return (x - left) % w == 0 and (y - top) % h == 0

    def build_background(self):
        bg = Image.new("RGBA", (self.width * TILE, self.height * TILE))

        # 바닥/벽 깔기
        for y, row in enumerate(self.grid): 
            for x, ch in enumerate(row):
                base = BASE_OF.get(ch, ch)
                bg.alpha_composite(self.tiles[base], (x * TILE, y * TILE))

        # 통로 그림자와 큰 물건 덮어 그리기
        for y, row in enumerate(self.grid):
            for x, ch in enumerate(row):
                if ch == "E":
                    # 오른쪽이 벽이면 오른쪽 통로, 아니면 왼쪽 통로
                    shadow = self.exit_shadow_right if self.get(x + 1, y) == "X" else self.exit_shadow
                    bg.alpha_composite(shadow, (x * TILE, y * TILE))
                elif ch in OBJECTS:
                    path, w, h, dy = OBJECTS[ch]
                    if self.is_anchor(x, y, w, h):
                        bg.alpha_composite(load_image(path), (x * TILE, y * TILE + dy))
                        if ch == "M": # 세면대 위 벽에 거울
                            bg.alpha_composite(load_image("toilet/toilet_mirror.png"), (x * TILE, (y - 1) * TILE))
        return bg

    def get(self, tx, ty):
        if tx < 0 or ty < 0 or tx >= self.width or ty >= self.height:
            return "X"
        return self.grid[ty][tx]

    def is_blocked(self, tx, ty):
        return self.get(tx, ty) in BLOCKED # 맵 밖은 "X"라서 막힘

    def draw(self, camera_x, camera_y):
        return self.background.crop((camera_x, camera_y, camera_x + SCREEN, camera_y + SCREEN))
