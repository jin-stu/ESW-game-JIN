import os
from PIL import ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "assets", "fonts", "D2Coding.ttc")

FONT_SMALL  = ImageFont.truetype(FONT_PATH, 12, index=0)   # Regular
FONT_NORMAL = ImageFont.truetype(FONT_PATH, 14, index=0)   # Regular
FONT_BOLD   = ImageFont.truetype(FONT_PATH, 14, index=1)   # Bold (강조, 선택된 버튼)
FONT_LARGE  = ImageFont.truetype(FONT_PATH, 24, index=1)   # Bold (타이틀 제목)

FPS = 20
FRAME_TIME = 1 / FPS
SCREEN = 240
TILE = 16
SPEED = 5 # 플레이어 이동 속도
CHASER_SPEED = 5            # 술래 이동 속도 (플레이어와 같게 시작, 나중에 난이도·질주에 사용)
ENTER_DELAY = 7             # 플레이어가 방을 옮긴 뒤 술래가 따라 들어오기까지 (초)

# 지나갈 수 없는 칸 / 숨을 수 있는 칸
BLOCKED = {"X", "U", "L", "W", "B", "T", "D", "C", "K", "I", "G", "S", "s", "M", "P", "H"}
HIDE_SPOTS = {"T", "H"}

# 방 이름 : (맵 파일 이름, 타일 묶음)
# 기본교실은 같은 맵 파일을 쓰는 방이 2개
ROOMS = {
    "hallway":      ("hallway", "hallway"),
    "classroom1":   ("classroom", "classroom"),      # 복도 오른쪽 위
    "classroom2":   ("classroom", "classroom"),      # 복도 오른쪽 아래
    "classroomA":   ("classroomA", "classroom"),     # 복도 왼쪽 아래
    "computerroom": ("computerroom", "computerroom"),  # 복도 왼쪽 위
    "toilet":       ("toilet", "toilet"),
}

# (지금 방, 통로 칸 x, y) : (다음 방, 도착 칸 x, y)
# 도착 칸은 반드시 통로(E) 바로 안쪽 바닥
EXITS = {
    # 복도 오른쪽 (x=14) -> 기본교실1, 기본교실2, 화장실
    ("hallway", 14, 4):   ("classroom1", 1, 3),      # 기본교실1 앞문
    ("hallway", 14, 5):   ("classroom1", 1, 4),
    ("hallway", 14, 10):  ("classroom1", 1, 17),     # 기본교실1 뒷문
    ("hallway", 14, 11):  ("classroom1", 1, 18),
    ("hallway", 14, 22):  ("classroom2", 1, 3),      # 기본교실2 앞문
    ("hallway", 14, 23):  ("classroom2", 1, 4),
    ("hallway", 14, 34):  ("classroom2", 1, 17),     # 기본교실2 뒷문
    ("hallway", 14, 35):  ("classroom2", 1, 18),
    ("hallway", 14, 37):  ("toilet", 1, 3),          # 화장실
    ("hallway", 14, 38):  ("toilet", 1, 4),
    # 복도 왼쪽 (x=7) -> 컴퓨터실, 교실A
    ("hallway", 7, 4):    ("computerroom", 11, 3),   # 컴퓨터실 윗문
    ("hallway", 7, 5):    ("computerroom", 11, 4),
    ("hallway", 7, 10):   ("computerroom", 11, 13),  # 컴퓨터실 아랫문
    ("hallway", 7, 11):   ("computerroom", 11, 14),
    ("hallway", 7, 22):   ("classroomA", 26, 3),     # 교실A 윗문
    ("hallway", 7, 23):   ("classroomA", 26, 4),
    ("hallway", 7, 34):   ("classroomA", 26, 17),    # 교실A 아랫문
    ("hallway", 7, 35):   ("classroomA", 26, 18),

    # 각 방 -> 복도
    ("classroom1", 0, 3):    ("hallway", 13, 4),
    ("classroom1", 0, 4):    ("hallway", 13, 5),
    ("classroom1", 0, 17):   ("hallway", 13, 10),
    ("classroom1", 0, 18):   ("hallway", 13, 11),
    ("classroom2", 0, 3):    ("hallway", 13, 22),
    ("classroom2", 0, 4):    ("hallway", 13, 23),
    ("classroom2", 0, 17):   ("hallway", 13, 34),
    ("classroom2", 0, 18):   ("hallway", 13, 35),
    ("toilet", 0, 3):        ("hallway", 13, 37),
    ("toilet", 0, 4):        ("hallway", 13, 38),
    ("computerroom", 12, 3):  ("hallway", 8, 4),
    ("computerroom", 12, 4):  ("hallway", 8, 5),
    ("computerroom", 12, 13): ("hallway", 8, 10),
    ("computerroom", 12, 14): ("hallway", 8, 11),
    ("classroomA", 27, 3):   ("hallway", 8, 22),
    ("classroomA", 27, 4):   ("hallway", 8, 23),
    ("classroomA", 27, 17):  ("hallway", 8, 34),
    ("classroomA", 27, 18):  ("hallway", 8, 35),
}