import os
from PIL import ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "assets", "fonts", "D2Coding.ttc")

FONT_SMALL  = ImageFont.truetype(FONT_PATH, 12, index=0)   # Regular
FONT_NORMAL = ImageFont.truetype(FONT_PATH, 14, index=0)   # Regular
FONT_BOLD   = ImageFont.truetype(FONT_PATH, 14, index=1)   # Bold (강조, 선택된 버튼)
FONT_LARGE  = ImageFont.truetype(FONT_PATH, 24, index=1)   # Bold (타이틀 제목)