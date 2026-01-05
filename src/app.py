from blessed import Terminal
import random
import sys
import signal


class Flake:

    def __init__(self, symbol: str, color: str="white", term: Terminal=None):
        self.symbol = symbol
        self.color = color
        self.term = term

    def __str__(self):
        if self.term:
            r, g, b = self.color
            return self.term.color_rgb(r, g, b) + self.symbol + self.term.normal
        return self.symbol

    def __eq__(self, other):
        if isinstance(other, Flake):
            return self.symbol == other.symbol
        elif isinstance(other, str):
            return self.symbol == other
        return False


def draw_char(term: Terminal, x: int, y: int, char: str) -> None:
    print(term.move(y, x) + str(char), end="", flush=True)


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


def animate_snow(term: Terminal, snow: dict, snow_static: dict, height: int, x: int, y: int, mode: str="pile") -> dict:
    new_snow = {}
    for (fy, fx), flake in snow.items():
        clear_char(term, fx, fy)

        below_pos = (fy + 1, fx)

        if mode == "pile" and (fy == height - 1 or not can_fall_through(snow_static, fx, fy + 1)):
            # Check if the flake should become static
            draw_char(term, fx, fy, flake)
            snow_static[(fy, fx)] = flake
            
        elif mode == "burn" and (fy == height - 1):
            # snow will disappear after ground line
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


def random_color() -> tuple[int, int, int]:
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


def replace_ansi(text:str, old:str, new:str) -> str:
    import re
    ansi_escape = re.compile(r'(\x1b\[[0-9;]*[a-zA-Z])')
    parts = ansi_escape.split(text)
    
    for i, part in enumerate(parts):
        if not ansi_escape.match(part):
            parts[i] = part.replace(old, new)
    
    return ''.join(parts)


def render_tree(term: Terminal, x: int, y: int, tree_colors:dict) -> None: 
    tree = """
              *
             / \\
            / 0 \\
           / 1   \\
          /       \\
         /_ 2  1  _\\
          /       \\
         /  1   2  \\
        /           \\
       /   0  3  0   \\
      /_        1    _\\
       /    2        \\
      /  1   0   0    \\
     /    3         3  \\
    /  2        1       \\
   /---------------------\\
             |||
             |||~
        ~  ~~~~~~~ ~~ ~
        """
    
    for num, (symbol, color) in tree_colors.items():
        tree = replace_ansi(tree, num, term.color_rgb(*color) + f"{symbol}" + term.normal) 
    
    print(term.move(y, x) + tree, end="", flush=True)
    
    
def write_controls_help(term: Terminal, x:int, y: int, mode: str) -> None:
    write_info(term, x, y + 1, f"a: auto snow")
    write_info(term, x, y + 2, f"s: place snow flake")
    write_info(term, x, y + 3, f"c: clear snow")
    write_info(term, x, y + 4, f"r: recolor the tree")
    write_info(term, x, y + 5, f"m: game mode burn or pile current: [{mode}]")
    write_info(term, x, y + 6, f"ESC: Exit")
    

def write_line(term: Terminal, y: int, width: int, symbol: str="~") -> None:
    line = symbol * width
    print(term.move(y, 0) + line, end="", flush=True)
    

def main() -> None:
    terminal: Terminal = Terminal()
    width: int = terminal.width
    height: int = terminal.height // 2

    info_x = 1
    info_y = height + 2

    x: int = 0
    y: int = 0

    print(terminal.clear, end="", flush=True)
    print(terminal.move(y, x), end="", flush=True)

    flakes = [".", "+", "*", "o", "@", "❄"]
    colors = [
        (255, 255, 255),  # white
        (192, 192, 192),  # grey
        (211, 211, 211),  # light_grey
        (173, 216, 230),  # light_blue
        (0, 0, 255),  # blue
        (0, 255, 255),  # cyan
        (224, 255, 255),  # light_cyan
        (106, 90, 205),  # slate_blue
        (176, 224, 230),  # powder_blue
        (240, 248, 255)  # alice_blue
    ]
    orbs = ["o", "O", "0", "@"]
    tree_colors = {str(i): (random.choice(orbs), random_color()) for i in range(10)}
    tree_colors["*"] = ("*", (255, 255, 51))
    tree_colors["/"] = ("/", (1, 141, 105))
    tree_colors["\\"] = ("\\", (1, 141, 105))
    tree_colors["-"] = ("-", (1, 141, 105))
    tree_colors["_"] = ("_", (1, 141, 105))
    tree_colors["|"] = ("|", (101, 67, 33))
    
    snow: dict = {}
    snow_static: dict = {}
    auto_snow: bool = False
    mode = "burn"
    
    def exit_gracefully(signum, frame):
        print(terminal.normal + terminal.clear + terminal.move(0, 0))
        sys.exit(0)

    signal.signal(signal.SIGINT, exit_gracefully)
    
    # controls
    write_controls_help(terminal, info_x, info_y, mode)
    
    # line
    write_line(terminal, height, width, "~")
    
    with terminal.cbreak(), terminal.keypad():
        while True:
            key = terminal.inkey(timeout=0.1)
            
            render_tree(terminal, width // 2, height // 2 - 7, tree_colors=tree_colors)
            
            snow = animate_snow(terminal, snow, snow_static, height, x, y, mode=mode)
            
            snow_flakes_on_screen = len(snow) + len(snow_static)
            write_info(terminal, info_x, info_y, f"current snow: {snow_flakes_on_screen}")
            print(terminal.move(y, x), end="", flush=True)
            
            if auto_snow:
                fy, fx = (0, random.randint(0, width - 1))
                flake = Flake(random.choice(flakes), color=random.choice(colors), term=terminal)
                snow[(fy, fx)] = flake

            if not key:
                continue

            if key.name == "KEY_ESCAPE":
                break

            if key == "s":
                # fy, fx = (0, random.randint(0, width - 1))
                fy, fx = y, x
                flake = Flake(random.choice(flakes), color=random.choice(colors), term=terminal)
                # write_info(terminal, info_x, info_y, f"{(fy, fx)} {flake}")
                draw_char(terminal, fx, fy, flake)
                print(terminal.move(y, x), end="", flush=True)
                snow[(fy, fx)] = flake
                continue

            if key == "a":
                auto_snow = not auto_snow

            if key == "c":
                snow = empty_dict(terminal, snow)
                snow_static = empty_dict(terminal, snow_static)
                
            if key == "m":
                if mode == "pile": mode = "burn"
                else: mode = "pile"
                write_controls_help(terminal, info_x, info_y, mode)
            
            if key == "r":
                for i in range(10):
                    tree_colors[f"{i}"] = (random.choice(orbs), random_color())
                    write_info(terminal, info_x, info_y, " " * width)

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

            # print(terminal.move(y, x), end="", flush=True)
    
    print(terminal.normal + terminal.clear) 
            
            
def test():
    print(Flake("F"))


if __name__ == "__main__":
    main()
