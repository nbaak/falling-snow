# Falling Snow

## Description

A terminal-based interactive snow simulation. Move a cursor with arrow keys, place symbols with SPACE, and watch snowflakes fall and stack.

## Requirements

* Python 3.8+
* [blessed](https://pypi.org/project/blessed/) library

Install dependencies:

```bash
pip install -r requirements.txt
```

## How to Use

* Run the program:

```bash
python falling_snow.py
```

* **Arrow keys**: Move the cursor
* **s**: Spawn a single snowflake at the top
* **a**: Toggle automatic snowfall
* **c**: Clear all snowflakes
* **ESC**: Exit the program

Snowflakes fall automatically and become static when reaching the bottom or stacking on other flakes.

## Inspired By
[ysap.sh](https://github.com/bahamas10/xmas.ysap.sh)
