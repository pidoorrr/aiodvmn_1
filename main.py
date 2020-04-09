import time
import random
import curses
import asyncio

from curses_tools import draw_frame, read_controls

TIC_TIMEOUT = 0.1


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot. Direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), "*")
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), "O")
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), " ")

    row += rows_speed
    column += columns_speed

    symbol = "-" if columns_speed else "|"

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), " ")
        row += rows_speed
        column += columns_speed


async def blink(canvas, row, column, symbols="+*.:"):
    while True:
        delay = random.randint(1, 20)
        symbol = random.choice(symbols)

        canvas.addstr(row, column, symbol, curses.A_DIM)

        for _ in range(delay):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(delay):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(delay):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(delay):
            await asyncio.sleep(0)


async def rocket_flight(canvas, max_y, max_x):
    rocket_y = max_y // 2
    rocket_x = max_x // 2

    while True:
        rows_direction, columns_direction, _ = read_controls(canvas)

        rocket_y += rows_direction
        rocket_x += columns_direction

        if rocket_y > max_y - 10 or rocket_y < 0:
            rocket_y -= rows_direction
        elif rocket_x > max_x - 6 or rocket_x < 0:
            rocket_x -= columns_direction

        draw_frame(canvas, rocket_y, rocket_x, ROCKET_FRAME_1)
        await asyncio.sleep(0)
        draw_frame(canvas, rocket_y, rocket_x, ROCKET_FRAME_1, negative=True)

        draw_frame(canvas, rocket_y, rocket_x, ROCKET_FRAME_2)
        await asyncio.sleep(0)
        draw_frame(canvas, rocket_y, rocket_x, ROCKET_FRAME_2, negative=True)


def draw(canvas):
    canvas.border()
    canvas.nodelay(True)

    max_y, max_x = canvas.getmaxyx()

    curses.curs_set(False)
    coroutines = [
        blink(canvas, random.randint(1, max_y - 2), random.randint(1, max_x - 2))
        for _ in range(random.randint(100, 200))
    ]

    coroutines.append(rocket_flight(canvas, max_y, max_x))

    while True:
        for coro in coroutines.copy():
            try:
                coro.send(None)
                canvas.refresh()
            except StopIteration:
                coroutines.remove(coro)
        time.sleep(TIC_TIMEOUT)

        if not coroutines:
            break


if __name__ == "__main__":
    with open("rocket_frame_1.txt") as f:
        ROCKET_FRAME_1 = f.read()
    with open("rocket_frame_2.txt") as f:
        ROCKET_FRAME_2 = f.read()

    curses.update_lines_cols()
    curses.wrapper(draw)
