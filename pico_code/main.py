import machine
import utime
import random
from textwrap import wrap

from epson_thermal import ThermalPrinter

# initialize random number generator
random.seed()

# red_button is on Pico GPIO 2, connected to ground
brb = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)

# debounce timer for brb in ms
bounce_time = 200
db_timer = machine.Timer()

# Wait time after printing ticket in seconds
wait_time = 5

# seutup uart for printer
uart = machine.UART(0, 9600, tx=machine.Pin(0), rx=machine.Pin(1))

# create printer object
pr = ThermalPrinter(uart)

# Read questions
from party_qs import party_qs, specials, players

n_players = len(players)
n_specials = len(specials)
n_qs = len(party_qs)
special_freq = 5  # 5 = 20% of time, e.g. 1 in 5
special_array = [True] + [False] * (special_freq - 1)
curr_player = random.randint(0, n_players - 1)
# print(curr_player)


# Wait for 5 seconds, then print welcome message
utime.sleep(5)
pr.add_horizontal_line()
pr.set_magnification(2, 2)
pr.add_text("NYE Ticket Game!")
pr.set_magnification(1, 1)
rules = """
In this game the goal is to end the evening with the most number of tickets.
You will either be asked a question or receive a special ticket.
If you get a question, answer it as best you can.
The other players will decide if you have answered the question in an interesting and fun way.
If they think you have, then you get the ticket. If not, it is discarded.
The Special Tickets are played as they are described.
Remember - the goal is to enter 2025 with the most tickets!

Press the Red Button to begin! Good Luck!

[Tear these rules off now!]"""
for line in rules.split("\n"):
    pr.add_text(wrap(line, width=30), feed=2)
pr.newline()
pr.add_horizontal_line(feed=3)
pr.write_buffer()


# Set up interrupt to run when button is pressed
def rb_debounce(pin):
    brb.irq(handler=None)
    # print(f"Button Pressed on {pin} at {utime.ticks_ms()}")
    db_timer.init(period=bounce_time, mode=machine.Timer.ONE_SHOT, callback=rb_action)


def rb_action(timer):
    # advance player
    global curr_player
    curr_player = (curr_player + 1) % n_players
    player = players[curr_player]
    pr.direct_reset()
    pr.add_horizontal_line()
    if random.choice(special_array):
        pr.set_justification("C")
        pr.add_text("Special Ticket for")
        pr.set_magnification(1, 2)
        pr.add_text(player)
        pr.set_justification("L")
        pr.set_magnification(1, 1)
        s = random.choice(specials)
        pr.newline()
        pr.add_text(wrap(s, width=30))
    else:
        pr.set_justification("C")
        pr.add_text("Question for")
        pr.set_magnification(1, 2)
        pr.add_text(player)
        pr.set_justification("L")
        pr.set_magnification(1, 1)
        q = random.choice(party_qs)
        # print(q)
        pr.newline()
        pr.add_text(wrap(q, width=30))
    pr.add_horizontal_line()
    pr.write_buffer()
    utime.sleep(wait_time)
    brb.irq(handler=rb_debounce)


brb.irq(trigger=machine.Pin.IRQ_FALLING, handler=rb_debounce)

while True:
    utime.sleep(1)
