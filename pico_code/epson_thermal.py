# Constants as byte arrays
LF = b"\x0A"
ASCII_TAB = b"\t"  # Horizontal tab
ASCII_FF = b"\f"  # Form feed
ASCII_CR = b"\r"  # Carriage return

# Command Prefixes
ESC_BANG = b"\x1B!"  # Command to change print mode
ESC_AT = b"\x1B@"  # Command to reset printer
ESC_V = b"\x1BV"  # Command to rotate text 90 degrees
ESC_a = b"\x1Ba"  # Justification
ESC_CURLY = b"\x1B{"  # Command to print upside down
GS_BANG = b"\x1D!"  # Command to set magnification

# PrintMode Masks
# See https://download4.epson.biz/sec_pubs/pos/reference_en/escpos/esc_exclamation.html

FONT_MASK = 0x01  # Select character font A or B
BOLD_MASK = 0x08  # Turn on/off bold printing mode
DOUBLE_HEIGHT_MASK = 0x10  # Turn on/off double-height printing mode
DOUBLE_WIDTH_MASK = 0x20  # Turn on/off double-width printing mode
UNDERLINE_MASK = 0x80  # Turn on/off deleteline mode


class ThermalPrinter:
    # Class for a simple thermal printer
    # The printer has a bytearray buffer
    # Various objects can be added to the buffer
    def __init__(self, uart):
        self.uart = uart
        # Start a buffer
        self.buff = bytearray()
        # Clear everything
        self.printmode = 0x00
        self.upside_down = False
        self.direct_reset()

    def direct_reset(self):
        self.uart.write(ESC_AT)

    def direct_write(self, data, feed=3):
        # Write to the uart without using (or changing) the buffer
        self.uart.write(data)
        if feed:
            self.uart.write(LF * feed)

    def clear_buffer(self):
        self.buff = bytearray()

    def add_bytes(self, data, feed=0):
        self.buff.extend(data)
        if feed:
            self.buff.extend(LF * feed)

    def add_text(self, text, feed=1):
        self.buff.extend(text.encode())
        if feed:
            self.buff.extend(LF * feed)

    def reset_print_mode(self):
        self.printmode = 0
        self.buff.extend(ESC_BANG + bytes([self.printmode]))

    def write_buffer(self, feed=3, clear=True):
        self.direct_write(self.buff, feed=feed)
        if clear:
            self.clear_buffer()

    def set_font(self, font="A"):
        if font == "A":
            self.printmode &= ~FONT_MASK
        elif font == "B":
            self.printmode |= FONT_MASK
        else:
            print("Font must be A or B")
        # Add command to buffer
        self.buff.extend(ESC_BANG + bytes([self.printmode]))

    def newline(self, feed=1):
        self.buff.extend(LF * feed)

    # The following print modes all use ESC ! <mode>, and allow for toggling
    def _set_mode(self, setting, mask):
        if setting is None:
            self.printmode ^= mask
        elif setting:
            self.printmode |= mask
        else:
            self.printmode &= ~mask
        # Add command to buffer
        self.buff.extend(ESC_BANG + bytes([self.printmode]))

    def set_bold(self, bold=None):
        self._set_mode(bold, BOLD_MASK)

    def set_double_height(self, double_height=None):
        self._set_mode(double_height, DOUBLE_HEIGHT_MASK)

    def set_double_width(self, double_width=None):
        self._set_mode(double_width, DOUBLE_WIDTH_MASK)

    def set_underline(self, strike=None):
        self._set_mode(strike, UNDERLINE_MASK)

    def set_rotate_90(self, rotate_code=1):
        # Sets the character by character rotation
        # 0 = 0 degrees
        # 1 = 90 degrees
        # 2 = 90 degrees with wider spacing
        self.buff.extend(ESC_V + bytes([rotate_code]))

    def set_upside_down(self, upside_down=None):
        if upside_down is None:
            self.upside_down = not self.upside_down
        else:
            self.upside_down = upside_down
        if self.upside_down:
            self.buff.extend(ESC_CURLY + b"\x01")
        else:
            self.buff.extend(ESC_CURLY + b"\x00")

    def set_magnification(self, height=None, width=None):
        if width is None:
            width = 1
        if height is None:
            height = 1

        value = ((width - 1) << 4) | (height - 1)
        # print(width, height, value)
        self.buff.extend(GS_BANG + bytes([value]))

    def set_justification(self, justify="L"):
        # If buffer doesn't end in a newline, add one
        if len(self.buff) > 0 and self.buff[-1] != LF:
            self.buff.extend(LF)
        # Set justification as Center, Right or Left (all else)
        if justify.lower()[0] == "c":
            self.buff.extend(ESC_a + b"\x01")
        elif justify.lower()[0] == "r":
            self.buff.extend(ESC_a + b"\x02")
        else:
            self.buff.extend(ESC_a + b"\x00")

    def add_horizontal_line(self, width=32, feed=2):
        # Note this is a bit of a hack, just
        # printing 32 underscores
        line_char = b"_"
        line = line_char * width
        self.buff.extend(line)
        if feed:
            self.buff.extend(LF * feed)
