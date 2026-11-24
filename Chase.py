from PIL import Image
from Map import Map
from Player import Player
from config import SCREEN, TILE, EXITS


class Chase:
    def __init__(self, joystick):
        self.joystick = joystick
        self.maps = {}                      # 한 번 만든 방은 저장해 두고 다시 씀
        self.player = Player(0, 0)
        self.change_room("classroom1", 13, 13)
        self.veil = Image.new("RGBA", (SCREEN, SCREEN), (0, 0, 10, 200))   # 숨었을 때 시야 제한

    def change_room(self, room, tx, ty):
        if room not in self.maps:
            self.maps[room] = Map(room)
        self.room = room
        self.map = self.maps[room]
        self.player.set_tile(tx, ty)

    def update(self):
        self.player.update(self.joystick, self.map)
        self.check_exit()

    def check_exit(self):
        # 발이 통로 칸에 닿으면 연결된 방으로 이동
        tx, ty = self.player.foot_tile()
        key = (self.room, tx, ty)
        if key in EXITS:
            next_room, nx, ny = EXITS[key]
            self.change_room(next_room, nx, ny)

    def camera(self, center, map_size):
        if map_size <= SCREEN:
            return (map_size - SCREEN) // 2                  # 맵이 화면보다 작으면 가운데 정렬
        return min(max(center - SCREEN // 2, 0), map_size - SCREEN)

    def draw(self):
        # 카메라: 플레이어를 가운데에 두되 맵 밖은 안 보이게
        cx = self.camera(self.player.x + 8, self.map.width * TILE)
        cy = self.camera(self.player.y + 12, self.map.height * TILE)

        image = self.map.draw(cx, cy)
        self.player.draw(image, cx, cy)
        if self.player.hidden:
            image.alpha_composite(self.veil)
        return image