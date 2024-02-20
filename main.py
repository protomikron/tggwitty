import subprocess as sp
import curses
import random
import argparse
import numpy as np
import os
import json
import sys
import time
import datetime as dt
from PIL import Image, ImageDraw, ImageFont
from Xlib import display, X
from Xlib import X, XK, display
from Xlib.ext import xtest

def send_key_event(disp, window, keycode, press):
    if press:
        event = X.KeyPress
    else:
        event = X.KeyRelease

    xtest.fake_input(disp, event, keycode)

    #XXX: needed?
    #disp.sync()

def get_keycode_for_action(action, disp):
    keysym = {
        'left': XK.XK_Left,
        'h': XK.XK_Left,
        'right': XK.XK_Right,
        'l': XK.XK_Right,
        'up': XK.XK_Up,
        'k': XK.XK_Up,
        'down': XK.XK_Down,
        'j': XK.XK_Down,
        'escape': XK.XK_Escape,
        'x': XK.XK_X,
        'a': XK.XK_A,
        'v': XK.XK_V,
        'z': XK.XK_Z,
        'r': XK.XK_R,
        'c': XK.XK_C,
        'n': XK.XK_N,
        'y': XK.XK_Y,
        'space': XK.XK_space
    }.get(action, None)
    if keysym:
        return disp.keysym_to_keycode(keysym)
    return None

def start_virtual_display_and_application(config):
    ws = config['window_size']
    xvfb_command = ['Xvfb', ':99', '-screen', '0', f'{ws}x{ws}x24']
    xvfb_process = sp.Popen(xvfb_command, stdout=sp.PIPE, stderr=sp.PIPE)

    print('started Xvfb daemon ...', file=sys.stderr)

    os.environ['DISPLAY'] = ':99'

    time.sleep(config['init_sleep_seconds'])

    wine_command = ['wineconsole', 'tggw/The Ground Gives Way.exe']
    wine_process = sp.Popen(wine_command, stdout=sp.PIPE, stderr=sp.PIPE)

    print('started TGGW ...', file=sys.stderr)

    time.sleep(config['init_sleep_seconds'])

    return xvfb_process, wine_process

def init_colors():
    rgb_colors = [
        (0, 0, 0),
        (0, 0, 255),
        (0, 128, 0),
        (0, 128, 128),
        (0, 255, 0),
        (0, 255, 255),
        (128, 0, 0),
        (128, 0, 128),
        (128, 128, 0),
        (128, 128, 128),
        (192, 192, 192),
        (255, 0, 0),
        (255, 0, 255),
        (255, 255, 0),
        (255, 255, 255),
        (0, 0, 128), # new 1
    ]

    color_pair_start = 1
    color_map = {}

    for i, (r, g, b) in enumerate(rgb_colors, start=color_pair_start):
        curses.init_color(i, r * 1000 // 255, g * 1000 // 255, b * 1000 // 255)
        curses.init_pair(i, i, curses.COLOR_BLACK)
        color_map[(r, g, b)] = i

    return color_map

def numpy_array_to_hash(arr):
    return hash(arr.tobytes())

def find_non_black_pixel(subset):
    for y in range(subset.shape[0]):
        for x in range(subset.shape[1]):
            if subset[y, x] == 1:
                return (x, y)
    return (0, 0)

def numpy_array_to_char2(arr, char_map):
    h = numpy_array_to_hash(arr)

    #XXX: why again here ... ?
    if h in char_map:
        return char_map[h]

    return '?',(0,0) #XXX?

char_cache = {}
def numpy_array_to_char(arr, char_map):
    h = numpy_array_to_hash(arr)
    if h in char_cache:
        return char_cache[h]
    # Processing to determine char
    (char, non_black_pixel_coord) = numpy_array_to_char2(arr, char_map)
    char_cache[h] = (char, non_black_pixel_coord)
    return (char, non_black_pixel_coord)

def loop(stdscr, config, unique_frames_dir):
    char_map = {}

    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    stdscr.clear()

    stdscr.nodelay(1)
    stdscr.keypad(1)

    curses.curs_set(0)

    image = Image.open('font.png')
    image_bw = np.array(image) // 255
    image_bw_2d = image_bw[:, :, 0]

    char_width, char_height = 8, 16
    top_left_offset_x, top_left_offset_y = 4, 31
    rows, cols = 38, 92 #XXX: check again

    for k, char in enumerate((chr(i) for i in range(32, 127))):
        offset_x = k % 16 * char_width
        offset_y = k // 16 * char_height
        subset = image_bw_2d[offset_y:offset_y+char_height, offset_x:offset_x+char_width]
    
        non_black_pixel_coord = find_non_black_pixel(subset)

        char_map[numpy_array_to_hash(subset)] = (char, non_black_pixel_coord)

    disp = display.Display(':99')
    root = disp.screen().root
    geom = root.get_geometry()
    width = geom.width
    height = geom.height

    color_map = init_colors()

    frame_idx = 0
    last_frame = np.zeros((config['window_size'], config['window_size'], 3), np.uint8)

    while True:
        start_frame_time = dt.datetime.now()

        c = stdscr.getch()
        action = None

        if c == curses.KEY_LEFT:
            action = 'left'
        elif c == ord('h'):
            action = 'left'
        elif c == curses.KEY_RIGHT:
            action = 'right'
        elif c == ord('l'):
            action = 'right'
        elif c == curses.KEY_UP:
            action = 'up'
        elif c == ord('k'):
            action = 'up'
        elif c == curses.KEY_DOWN:
            action = 'down'
        elif c == ord('j'):
            action = 'down'
        elif c == ord('x'):
            action = 'x'
        elif c == ord('v'):
            action = 'v'
        elif c == ord('z'):
            action = 'z'
        elif c == ord('a'):
            action = 'a'
        elif c == ord('y'):
            action = 'y'
        elif c == ord('r'):
            action = 'r'
        elif c == ord('n'):
            action = 'n'
        elif c == ord('c'):
            action = 'c'
        elif c == ord(' '):
            action = 'space'
        elif c == 27:
            action = 'escape'

        if action:
            keycode = get_keycode_for_action(action, disp)
            if keycode:
                send_key_event(disp, root, keycode, True)
                send_key_event(disp, root, keycode, False)

        raw_image = root.get_image(0, 0, width, height, X.ZPixmap, 0xffffffff)
        image = Image.frombytes('RGB', (width, height), raw_image.data, 'raw', 'BGRX')
        image_rgb = np.array(image)
        image_arr = (~np.all(image_rgb == 0, axis=-1)).astype(np.uint8)

        if (image_rgb != last_frame).any():
            last_frame = image_rgb
            image.save(f'{unique_frames_dir}/frame_{frame_idx}.png')

        frame_idx += 1

        for row in range(0, rows):
            for col in range(0, cols):
                x = col * char_width + top_left_offset_x
                y = row * char_height + top_left_offset_y

                char_image_mask = image_arr[y:y+char_height, x:x+char_width].astype(np.uint8)
                char_image_rgb = image_rgb[y:y+char_height, x:x+char_width].astype(np.uint8)

                #XXX: why shape (15, 8)
                if char_image_mask.shape == (16, 8):
                    char, (x,y) = numpy_array_to_char(char_image_mask, char_map)
                    (r,g,b) = char_image_rgb[y,x]

                    pair_i = color_map[(r,g,b)]

                    #XXX: investigate (195,195,195) ... error?

                stdscr.addch(row, col, char, curses.color_pair(pair_i))

        frame_time = (dt.datetime.now() - start_frame_time).total_seconds()
        stdscr.addstr(rows, 0, f'TGGWITTY v2024.03 [{int(1 / frame_time)} fps]', curses.color_pair(15))

        stdscr.refresh()

    disp.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Tggwitty: The Ground Gives Way in tty')
    parser.add_argument('config', type=str, help='path to the config.json file')
    parser.add_argument('--write-unique-frames', type=str, dest='unique_frames_dir', help='Directory to write unique frames', default=None)

    args = parser.parse_args()

    with open(args.config, 'r') as config_file:
        config = json.load(config_file)

    xvfb_process, wine_process = start_virtual_display_and_application(config)

    if args.unique_frames_dir:
        os.makedirs(args.unique_frames_dir, exist_ok=True)

    curses.wrapper(loop, config, args.unique_frames_dir)

    wine_process.terminate()
    xvfb_process.terminate()

