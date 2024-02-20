# Overview

Tggwitty (The Ground Gives Way in tty) is a wrapper that runs TGGW using Wine in
a headless X framebuffer, parses its output and renders it via curses.

# Install

You need `wine` and `Xvfb` which usually ship with your distribution. After that

    $ python3 main.py

should work.

# FAQ

Q: Why?
A: Why not? But seriously - TGGW's native ASCII art maps quite well to Linux
   terminal capabilities (it's a `cmd.exe` terminal application after all).

# License

- This code: MIT
- TGGW: A roguelike game by BtS [Copyright 2014-2022]

