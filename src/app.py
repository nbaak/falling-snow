from blessed import Terminal
import random


def draw_char(term: Terminal, x: int, y: int, char: str) -> None:
    print(term.move(y, x) + char, end="", flush=True)


def clear_char(term: Terminal, x: int, y: int) -> None:
    print(term.move(y, x) + " ", end="", flush=True)


def write_info(term: Terminal, x: int, y: int, text: str) -> None:
    blank = " " * 20
    print(term.move(y, x) + blank, end="", flush=True)
    print(term.move(y, x) + text, end="", flush=True)


def can_fall_through(snow_static: dict, x: int, y: int) -> bool:
    if (y, x) not in snow_static:
        return True
    if snow_static[(y, x)] == ".":
        return True
    return False


def animate_snow(term: Terminal, snow: dict, snow_static: dict, height: int, x: int, y: int) -> dict:
    new_snow = {}
    for (fy, fx), flake in snow.items():
        clear_char(term, fx, fy)

        below_pos = (fy + 1, fx)

        # Check if the flake should become static
        if fy == height - 1 or not can_fall_through(snow_static, fx, fy + 1):
            draw_char(term, fx, fy, flake)
            snow_static[(fy, fx)] = flake
        else:
            # remove dot if falling into it
            if below_pos in snow_static and snow_static[below_pos] == ".":
                del snow_static[below_pos]

            # Move down
            new_pos = (fy + 1, fx)
            draw_char(term, fx, fy + 1, flake)
            new_snow[new_pos] = flake

    print(term.move(y, x), end="", flush=True)
    return new_snow


def empty_dict(term: Terminal, _dict: dict) -> dict:
    new_dict = {}
    for (y, x) in _dict.keys():
        clear_char(term, x, y)
    return new_dict


def main() -> None:
    terminal: Terminal = Terminal()
    width: int = 40
    height: int = 10

    info_x = 1
    info_y = height + 3

    x: int = 0
    y: int = 0

    print(terminal.clear, end="", flush=True)
    print(terminal.move(y, x), end="", flush=True)

    flakes = [".", "+", "*", "o", "@"]
    snow: dict = {}
    snow_static: dict = {}
    auto_snow: bool = False

    with terminal.cbreak(), terminal.keypad():
        while True:
            key = terminal.inkey(timeout=0.1)
            
            snow = animate_snow(terminal, snow, snow_static, height, x, y)

            if auto_snow:
                fy, fx = (0, random.randint(0, width - 1))
                flake = random.choice(flakes)
                snow[(fy, fx)] = flake

            if not key:
                continue

            if key.name == "KEY_ESCAPE":
                break

            if key == "s":
                fy, fx = (0, random.randint(0, width - 1))
                flake = random.choice(flakes)
                write_info(terminal, info_x, info_y, f"{(fy, fx)} {flake}")
                draw_char(terminal, fx, fy, flake)
                print(terminal.move(y, x), end="", flush=True)
                snow[(fy, fx)] = flake
                continue

            if key == "a":
                auto_snow = not auto_snow

            if key == "c":
                snow = empty_dict(terminal, snow)
                snow_static = empty_dict(terminal, snow_static)

            if key.name == "KEY_UP":
                y = (y - 1) % height
            elif key.name == "KEY_DOWN":
                y = (y + 1) % height
            elif key.name == "KEY_LEFT":
                x = (x - 1) % width
            elif key.name == "KEY_RIGHT":
                x = (x + 1) % width
            else:
                continue

            print(terminal.move(y, x), end="", flush=True)


if __name__ == "__main__":
    main()
