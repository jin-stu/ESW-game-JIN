import board
from digitalio import DigitalInOut, Direction
from adafruit_rgb_display import st7789


class Joystick:
    def __init__(self):
        # LCD (SPI)
        cs_pin = DigitalInOut(board.CE0)
        dc_pin = DigitalInOut(board.D25)
        reset_pin = DigitalInOut(board.D24)
        spi = board.SPI()
        self.disp = st7789.ST7789(spi, width=240, height=240, rotation=180,
                                  x_offset=0, y_offset=80,
                                  cs=cs_pin, dc=dc_pin, rst=reset_pin, baudrate=24000000)

        # 백라이트 켜기
        self.backlight = DigitalInOut(board.D26)
        self.backlight.switch_to_output()
        self.backlight.value = True

        # 버튼 (누르면 LOW)
        self.button_U = self.make_button(board.D17)
        self.button_D = self.make_button(board.D22)
        self.button_L = self.make_button(board.D27)
        self.button_R = self.make_button(board.D23)
        self.button_C = self.make_button(board.D4)
        self.button_A = self.make_button(board.D5)
        self.button_B = self.make_button(board.D6)

        self.buttons = {"up": self.button_U, "down": self.button_D, "left": self.button_L,
                        "right": self.button_R, "center": self.button_C,
                        "A": self.button_A, "B": self.button_B}
        self.held = {name: False for name in self.buttons}      # 지금 누르고 있는지
        self.pressed = {name: False for name in self.buttons}   # 이번 프레임에 막 눌렀는지

    def make_button(self, pin):
        button = DigitalInOut(pin)
        button.direction = Direction.INPUT
        return button

    def update(self):
        # 매 프레임 한 번 호출: 버튼 상태 읽기
        for name, button in self.buttons.items():
            now = not button.value                  # 누르면 LOW(False)
            self.pressed[name] = now and not self.held[name]
            self.held[name] = now
