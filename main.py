import time
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
    rows_speed: typing.Union[float, int] = -0.3,
    columns_speed: typing.Union[float, int] = 0,
) -> None:
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


async def rocket_flight(canvas: curses.window, max_y: int, max_x: int):
    rocket_y = max_y // 2
    rocket_x = max_x // 2

    while True:
        rocket_y, rocket_x = change_rocket_coordinates(
            canvas, rocket_y, rocket_x, max_y, max_x
        )
        draw_frame(canvas, rocket_y, rocket_x, rocket_frame_1)
        await asyncio.sleep(0)

        draw_frame(canvas, rocket_y, rocket_x, rocket_frame_1, negative=True)

        rocket_y, rocket_x = change_rocket_coordinates(
            canvas, rocket_y, rocket_x, max_y, max_x
        )
        draw_frame(canvas, rocket_y, rocket_x, rocket_frame_2)
        await asyncio.sleep(0)

        draw_frame(canvas, rocket_y, rocket_x, rocket_frame_2, negative=True)


def draw(canvas: curses.window):
    canvas.border()
    canvas.nodelay(True)

    rows, columns = canvas.getmaxyx()
    # rows and columns greater by one then real window size
    max_y, max_x = rows - 1, columns - 1

    curses.curs_set(False)

    stars_max_y = rows - 2
    stars_max_x = columns - 2
    coroutines = [
        blink(
            canvas,
            random.randint(1, stars_max_y),
            random.randint(1, stars_max_x),
            delay=random.randint(1, 20),
        )
        for _ in range(random.randint(100, 200))
    ]

    coroutines.append(rocket_flight(canvas, max_y, max_x))

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
