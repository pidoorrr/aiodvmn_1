import time
import itertools
import typing
import random
import curses
import asyncio

from curses_tools import draw_frame, read_controls

TIC_TIMEOUT = 0.1


async def fire(
    canvas: curses.window,
    start_row: typing.Union[float, int],
    start_column: typing.Union[float, int],
    max_y: int,
    max_x: int,
    rows_speed: typing.Union[float, int] = -0.3,
    columns_speed: typing.Union[float, int] = 0,
):
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

    curses.beep()

    while 0 < row < max_y and 0 < column < max_x:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), " ")
        row += rows_speed
        column += columns_speed


async def blink(
    canvas: curses.window,
    row: int,
    column: int,
    delay: int,
    symbols: typing.Sequence[str] = "+*.:",
):
    while True:
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


def change_rocket_coordinates(
    canvas: curses.window, rocket_y: int, rocket_x: int, max_y: int, max_x: int
) -> typing.Tuple[int, int]:
    rocket_height = 9
    rocket_width = 5

    rows_direction, columns_direction, _ = read_controls(canvas)

    rocket_y += rows_direction
    rocket_x += columns_direction

    if rocket_y > max_y - rocket_height or rocket_y <= 0:
        rocket_y -= rows_direction
    elif rocket_x > max_x - rocket_width or rocket_x <= 0:
        rocket_x -= columns_direction

    return rocket_y, rocket_x


async def animate_rocket_flight(canvas: curses.window, max_y: int, max_x: int):
    rocket_y = max_y // 2
    rocket_x = max_x // 2

    for frame in itertools.cycle([rocket_frame_1, rocket_frame_2]):
        rocket_y, rocket_x = change_rocket_coordinates(
            canvas, rocket_y, rocket_x, max_y, max_x
        )
        draw_frame(canvas, rocket_y, rocket_x, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, rocket_y, rocket_x, frame, negative=True)


def draw(canvas: curses.window):
    canvas.border()
    canvas.nodelay(True)

    # https://docs.python.org/3/library/curses.html#curses.window.getmaxyx
    window_height, window_width = canvas.getmaxyx()
    # rows and columns greater by one then real window size
    max_y, max_x = window_height - 1, window_width - 1

    curses.curs_set(False)

    # Reducing max dimensions by 2 allows to avoid "curses.error"
    stars_max_y = window_height - 2
    stars_max_x = window_width - 2
    coroutines = [
        blink(
            canvas,
            random.randint(1, stars_max_y),  # stars mustn't appear on border
            random.randint(0, stars_max_x),
            delay=random.randint(1, 20),
        )
        for _ in range(random.randint(100, 200))
    ]

    coroutines.append(animate_rocket_flight(canvas, max_y, max_x))

    while coroutines:
        for coro in coroutines.copy():
            try:
                coro.send(None)
            except StopIteration:
                coroutines.remove(coro)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == "__main__":
    with open("rocket_frame_1.txt") as f:
        rocket_frame_1 = f.read()
    with open("rocket_frame_2.txt") as f:
        rocket_frame_2 = f.read()

    curses.update_lines_cols()
    curses.wrapper(draw)
