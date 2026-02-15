import webhook
import time
import pyautogui
import sys
import os
import subprocess
import json

from Tools import botTools as bt
from Tools import winTools as wt
from Tools import avMethods as avM


from datetime import datetime
from threading import Thread
from pynput import keyboard as pynput_keyboard
from pynput.keyboard import Controller
from pathlib import Path


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__)) 
RESOURCES_DIR = os.path.join(PROJECT_ROOT, "Resources")
WINTER_DIR = os.path.join(RESOURCES_DIR, "Winter")
PROJECT_ROOT = Path(__file__).resolve().parent
RESOURCES_DIR = PROJECT_ROOT / "Resources"

# print("PROJECT_ROOT:", PROJECT_ROOT)
# print("RESOURCES_DIR:", RESOURCES_DIR, "exists=", os.path.exists(RESOURCES_DIR))
# print("WINTER_DIR:", WINTER_DIR, "exists=", os.path.exists(WINTER_DIR))
# print("TEST IMAGE PATH:", os.path.exists(bt._resource_path("Winter/Bunny_hb.png")))

def asset_path(rel: str) -> str:
    """
    Convert 'Winter/Bunny_hb.png' → absolute path inside Resources folder
    """
    rel = rel.replace("/", "/")   # normalize Windows slashes
    return str((RESOURCES_DIR / rel).resolve())

class Cur_Settings: pass

global Settings
Settings = Cur_Settings()

Settings_Path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"Settings")
WE_Json = os.path.join(Settings_Path,"Winter_Event.json")

VERSION_N = '1.49'

ROBLOX_PLACE_ID = 16146832113

PRIVATE_SERVER_CODE = "" # Not in settings so u dont accidently share ur ps lol

USE_KAGUYA = False # "its faster to lowkey not use kaguya lol" ~LoxerEx

USE_BUU = False #Best unit for highest curency gain

TAK_FINDER = False # turn off if it runs into a wall while trying to find tak

ROUND_RESTART = 140 # 0 will make it so this doesnt happen, change it to what round u want it to restart

AINZ_SPELLS = False #Keep FALSE!

SLOT_ONE = (495, 789, 570, 866)
REG_SPEED = (495, 789, 570, 866)
REG_TAK = (495, 789, 570, 866)

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0
keyboard_controller = Controller()


# Settings JSON
def load_json_data():
    JSON_DATA = None
    if os.path.isfile(WE_Json):
        with open(WE_Json, 'r') as f:
            JSON_DATA = json.load(f)
    return JSON_DATA
if os.path.exists(Settings_Path):
    if os.path.exists(WE_Json):
        data = load_json_data()
        for variable in data:
            value = data.get(variable)
            try:
                if variable == "Unit_Positions" or variable == "Unit_Placements_Left":
                    if type(value[0]) == dict:
                        setattr(Settings, variable, value[0])
                else:
                    setattr(Settings, variable, value)
            except Exception as e:
                print(e)
else:
    print("Failed to find settings file. Closing in 10 seconds")
    time.sleep(10)
    sys.exit()
    
    
    
print("Loaded settings")
Settings.Units_Placeable.append("Doom")

if not USE_KAGUYA:
    Settings.Units_Placeable.remove("Kag")

# Failsafe key
global g_toggle
g_toggle = False
def toggle():
    global g_toggle
    g_toggle = not g_toggle
    if g_toggle == False:
        args = list(sys.argv)
        try:
            if "--restart" in args:
                args.remove("--restart")
            if "--stopped" in args:
                args.remove("--stopped")
        except Exception as e:
            print(e)
        sys.stdout.flush()
        subprocess.Popen([sys.executable, *args, "--stopped"])
        os._exit(0)



# -------------------------
# Hotkey System (Mac Safe)
# -------------------------
def toggle():
    global g_toggle
    g_toggle = not g_toggle
    print(f"Macro running: {g_toggle}")

    if not g_toggle:
        args = list(sys.argv)
        if "--restart" in args:
            args.remove("--restart")
        if "--stopped" in args:
            args.remove("--stopped")

        subprocess.Popen([sys.executable] + args + ["--stopped"])
        os._exit(0)


def kill():
    os._exit(0)


def on_press(key):
    try:
        if hasattr(key, "char") and key.char:
            if key.char.lower() == Settings.STOP_START_HOTKEY.lower():
                toggle()
            elif key.char.lower() == "k":
                kill()
    except:
        pass


listener = pynput_keyboard.Listener(on_press=on_press)
listener.daemon = True
listener.start()


# -------------------------
# Click Function (Mac Safe)
# -------------------------
def click(x, y, delay=None, right_click=False, dont_move=False):
    if delay is None:
        delay = 0.3

    if not dont_move:
        pyautogui.moveTo(x, y)

    time.sleep(delay)

    if right_click:
        pyautogui.rightClick()
    else:
        pyautogui.click()


# -------------------------
# Key Press Helpers
# -------------------------
def press(key):
    keyboard_controller.press(key)


def release(key):
    keyboard_controller.release(key)


def tap(key):
    keyboard_controller.press(key)
    keyboard_controller.release(key)

def write_text(text, interval=0.2):
    for char in text:
        keyboard_controller.press(char)
        keyboard_controller.release(char)
        time.sleep(interval)

# -------------------------
# Scroll Replacement
# -------------------------
def scroll(amount):
    pyautogui.scroll(amount)

# -------------------------
# Screenshot Capture and Pixel Detection (Mac Rendering Layer)
# -------------------------

def _seen_pixel_from_screenshot(img, x: int, y: int, sample_half: int = 1):
    # Map pyautogui coords -> screenshot pixel coords using THIS screenshot
    sw, sh = pyautogui.size()
    iw, ih = img.size
    sx = iw / sw
    sy = ih / sh

    xp = int(x * sx)
    yp = int(y * sy)

    w, h = img.size
    left = max(0, xp - sample_half)
    top = max(0, yp - sample_half)
    right = min(w - 1, xp + sample_half)
    bottom = min(h - 1, yp + sample_half)

    px = []
    for yy in range(top, bottom + 1):
        for xx in range(left, right + 1):
            p = img.getpixel((xx, yy))
            if isinstance(p, tuple) and len(p) >= 3:
                px.append((p[0], p[1], p[2]))

    if not px:
        return (0, 0, 0)

    # median per channel
    rs = sorted(p[0] for p in px)
    gs = sorted(p[1] for p in px)
    bs = sorted(p[2] for p in px)
    mid = len(px) // 2
    return (rs[mid], gs[mid], bs[mid])

def pixel_color_seen(x: int, y: int, sample_half: int = 1):
    img = pyautogui.screenshot()
    return _seen_pixel_from_screenshot(img, x, y, sample_half=sample_half)

def pixel_matches_seen(x: int, y: int, rgb: tuple[int, int, int], tol: int = 20, sample_half: int = 1) -> bool:
    img = pyautogui.screenshot()
    r, g, b = _seen_pixel_from_screenshot(img, x, y, sample_half=sample_half)
    return (abs(r - rgb[0]) <= tol and abs(g - rgb[1]) <= tol and abs(b - rgb[2]) <= tol)

def wait_for_pixel(
    x: int,
    y: int,
    rgb: tuple[int, int, int],
    tol: int = 20,
    timeout: float = 10.0,
    interval: float = 0.1,
    sample_half: int = 1
) -> bool:
    """
    Waits until pixel matches RGB within tolerance.
    Returns True if matched, False if timeout.
    """
    start = time.time()

    while time.time() - start < timeout:
        img = pyautogui.screenshot()

        if pixel_matches_seen(x, y, rgb,tol=tol,sample_half=sample_half):
            return True

        time.sleep(interval)

    return False


# -------------------------
# Safe Restart (Mac)
# -------------------------
def safe_restart():
    print("Restarting script...")
    args = list(sys.argv)

    if "--stopped" in args:
        args.remove("--stopped")

    if "--restart" in args:
        args.remove("--restart")

    subprocess.Popen([sys.executable] + args)
    os._exit(0)


# -------------------------
# Screen Debug Info
# -------------------------
SCREEN_W, SCREEN_H = pyautogui.size()
print(f"Screen size detected: {SCREEN_W} x {SCREEN_H}")

# Wait for start screen
def wait_start(delay: int | None = None):
    i = 0
    if delay is None:
        delay = 1

    target = (99, 214, 63)

    while i < 90:
        i += 1
        try:
            seen = pixel_color_seen(816, 231, sample_half=2)  # 5x5 median
            print(f"Looking for start screen... seen={seen}")

            if pixel_matches_seen(816, 231, target, tol=35, sample_half=2):
                print("✅ Start screen detected")
                return True

        except Exception as e:
            print(f"e {e}")

        time.sleep(delay)

    print("❌ Start screen NOT detected (timeout)")
    return False


def quick_rts(): # Returns to spawn
    locations =[(232, 873), (1153, 503), (1217, 267)]
    for loc in locations:
        click(loc[0], loc[1], delay =0.1)
        time.sleep(0.2)
        
def directions(area: str, unit: str | None=None): # This is for all the pathing
    '''
    This is the pathing for all the areas: 1 [rabbit, nami, hero (trash gamer)], 2 [speed, tak], 3: Mystery box, 4: Upgrader, 5: Monarch upgradern
    '''
    # All this does is set up camera whenever it's the first time running, disable if needed
        
    #Contains rabbit, nami, and hero
    if Settings.USE_NIMBUS:
        if area == '1':  
            #DIR_PATHING
            # Pathing
            if not Settings.CTM_P1_P2:
                press('a')
                time.sleep(0.4)
                release('a')
                time.sleep(1)
                tap('v')
                time.sleep(1.5)
                press('w')
                time.sleep(1.5)
                release('w')
                press('a')
                time.sleep(1.1)
                release('a')
            else:
                tap('v')
                time.sleep(1)
                for p in Settings.CTM_AREA_1:
                    click(p[0],p[1],delay =0.1,right_click=True)
                    time.sleep(1.9)
                time.sleep(1.5)
            if unit == 'rabbit':
                #[(558, 334)
                click(Settings.CTM_AREA_1_UNITS[0][0], Settings.CTM_AREA_1_UNITS[0][1], delay =0.1,right_click=True) # Click to move
                time.sleep(1)
            if unit == "nami":
                click(Settings.CTM_AREA_1_UNITS[1][0], Settings.CTM_AREA_1_UNITS[1][1], delay =0.1,right_click=True)
                time.sleep(1)
            if unit == "hero":
                click(Settings.CTM_AREA_1_UNITS[2][0], Settings.CTM_AREA_1_UNITS[2][1], delay =0.1,right_click=True)
                time.sleep(1)
            tap('v') 
            time.sleep(2)
        # Speed wagon + Tak
        if area == '2':
            if not Settings.CTM_P1_P2:
                press('a')
                time.sleep(0.4)
                release('a')
                time.sleep(1)
                tap('v')
                time.sleep(1.5)
                press('w')
                time.sleep(1.5)
                release('w')
            else:
                tap('v')
                time.sleep(1.3)
                for p in Settings.CTM_AREA_2:
                    click(p[0],p[1],delay =0.1,right_click=True)
                    time.sleep(1.5)
                time.sleep(1.5)
            #(534, 706), (535, 546)
            if unit == 'speed':
                click(Settings.CTM_AREA_2_UNITS[0][0], Settings.CTM_AREA_2_UNITS[0][1], delay =0.1,right_click=True)
                time.sleep(1)
            if unit == 'tak':
                click(Settings.CTM_AREA_2_UNITS[1][0], Settings.CTM_AREA_2_UNITS[1][1], delay =0.1,right_click=True)
                time.sleep(1)
            tap('v')
            time.sleep(2)
        # Gambling time
        if area == '3': 
            tap('v')
            time.sleep(1)
            press('a')
            time.sleep(Settings.AREA_3_DELAYS[0])
            release('a')

            press('s')
            time.sleep(Settings.AREA_3_DELAYS[1])
            release('s')

            press('d')
            time.sleep(Settings.AREA_3_DELAYS[2])
            release('d')

            press('s')
            time.sleep(Settings.AREA_3_DELAYS[3])
            release('s')
            tap('v')
            time.sleep(2)
            e_delay = 0.7
            timeout = 2.5/e_delay
            at_location = False
            while not at_location:
                tap('e')
                time.sleep(e_delay)
                if bt.does_exist("Winter/LootBox.png",confidence=0.7,grayscale=True):
                    at_location = True
                if  bt.does_exist("Winter/Full_Bar.png",confidence=0.7,grayscale=True):
                    at_location = True
                if  bt.does_exist("Winter/NO_YEN.png",confidence=0.7,grayscale=True):
                    at_location = True
                if timeout < 0:
                    quick_rts()
                    tap('v')
                    time.sleep(1)
                    press('a')
                    time.sleep(Settings.AREA_3_DELAYS[0])
                    release('a')

                    press('s')
                    time.sleep(Settings.AREA_3_DELAYS[1])
                    release('s')

                    press('d')
                    time.sleep(Settings.AREA_3_DELAYS[2])
                    release('d')

                    press('s')
                    time.sleep(Settings.AREA_3_DELAYS[3])
                    release('s')
                    tap('v')
                    time.sleep(2)
                    timeout = 3/e_delay
                timeout-=1
            print("At lootbox")

        if area == '4': #  Upgrader location
            tap('v')
            time.sleep(1)
            press('a')
            time.sleep(Settings.AREA_4_DELAYS[0])
            release('a')

            press('s')
            time.sleep(Settings.AREA_4_DELAYS[1])
            release('s')
            tap('v')
            time.sleep(2)
            
        if area == '5': # This is where it buys monarch
            tap('v')
            time.sleep(1)
            press('a')
            time.sleep(Settings.AREA_5_DELAYS[0])
            release('a')

            press('w')
            time.sleep(Settings.AREA_5_DELAYS[1])
            release('w')
            tap('v')
            time.sleep(2)
        
def upgrader(upgrade: str):
    """
    Buys the upgrades for the winter event: fortune, range, damage, speed, armor
    mac-friendly + Retina-safe pixel checks (screenshot-based)
    """

    def seen(x, y, rgb, tol=40, sample_half=2) -> bool:
        # wrapper so we can tune tol/sample_half in one place
        return pixel_matches_seen(x, y, rgb, tol=tol, sample_half=sample_half)

    e_delay = 0.2
    timeout = 3 / e_delay

    tap('e')

    # Wait until the upgrade UI is open (white pixel check)
    while True:
        if seen(524, 324, (235, 235, 235), tol=30, sample_half=2):
            break

        if timeout < 0:
            quick_rts()
            directions('4')
            timeout = 3 / e_delay

        timeout -= 1
        tap('e')
        time.sleep(e_delay)

    click(607, 381, delay =0.1)
    time.sleep(0.5)

    # ---------- UI NAV OFF ----------
    if not Settings.USE_UI_NAV:

        if upgrade == 'fortune':
            pyautogui.moveTo(775, 500)  # ensure scroll is inside panel
            time.sleep(0.2)
            pyautogui.scroll(100)
            time.sleep(0.5)

            pos = (955, 475)
            while not seen(pos[0], pos[1], (24, 24, 24), tol=50, sample_half=2):
                if not g_toggle:
                    break
                click(pos[0], pos[1], delay =0.1)
                time.sleep(0.8)

            click(1112, 309, delay =0.1)
            print("Fortune complete")


        elif upgrade == "damage":
            pyautogui.moveTo(775, 500)  # ensure scroll is inside panel
            time.sleep(0.2)

            for _ in range(6):
                pyautogui.scroll(-1)
                time.sleep(0.2)

            pos = (955, 635)
            while not seen(pos[0], pos[1], (24, 24, 24), tol=50, sample_half=2):
                if not g_toggle:
                    break
                click(pos[0], pos[1], delay =0.1)
                time.sleep(0.8)

            pyautogui.moveTo(775, 500)  # ensure scroll is inside panel
            pyautogui.scroll(100)
            click(1112, 309, delay =0.1)
            print("Damage complete")


        elif upgrade == 'range':
            pyautogui.moveTo(775, 500)  # ensure scroll is inside panel
            time.sleep(0.2)

            for _ in range(3):
                pyautogui.scroll(-1)
                time.sleep(0.2)


            pos = (955, 635)
            while not seen(pos[0], pos[1], (24, 24, 24), tol=50, sample_half=2):
                if not g_toggle:
                    break
                click(pos[0], pos[1], delay =0.1)
                time.sleep(0.8)

            pyautogui.moveTo(775, 500)  # ensure scroll is inside panel
            pyautogui.scroll(100)   
            click(1112, 309, delay =0.1)
            print("Range complete")


        elif upgrade == "speed":
            pyautogui.moveTo(775, 500)  # ensure scroll is inside panel
            time.sleep(0.2)

            pos = (955, 635)
            while not seen(pos[0], pos[1], (24, 24, 24), tol=50, sample_half=2):
                if not g_toggle:
                    break
                click(pos[0], pos[1], delay =0.1)
                time.sleep(0.8)

            pyautogui.moveTo(775, 500)  # ensure scroll is inside panel
            pyautogui.scroll(100)
            click(1112, 309, delay =0.1)
            print("Speed complete")

        elif upgrade == "armor":
            pyautogui.moveTo(775, 500)  # ensure scroll is inside panel
            time.sleep(0.2)

            
            for _ in range(9):
                pyautogui.scroll(-1)
                time.sleep(0.2)

            pos = (955, 635)
            while not seen(pos[0], pos[1], (24, 24, 24), tol=50, sample_half=2):
                if not g_toggle:
                    break
                click(pos[0], pos[1], delay =0.1)
                time.sleep(0.8)

            pyautogui.moveTo(775, 500)  # ensure scroll is inside panel
            pyautogui.scroll(100)
            click(1112, 309, delay =0.1)
            print("Armor complete")



    # ---------- UI NAV ON ----------
    else:
        # These are your UI navigation versions, just swapped to screenshot-based pixel checks

        if upgrade == 'fortune':
            pos = (960, 406)
            click(765, 497, delay=0.1)
            scroll(-1000)
            time.sleep(0.2)
            tap('/')
            tap('/')

            while not seen(pos[0], pos[1], (24, 24, 24), tol=50, sample_half=2):
                if not g_toggle:
                    break
                click(pos[0], pos[1], delay =0.1)
                time.sleep(0.8)

            scroll(1000)
            click(1112, 309, delay =0.1)

        elif upgrade == 'range':
            pos = (955, 562)
            click(765, 497, delay=0.1)
            scroll(-1000)
            time.sleep(0.2)
            tap('/')
            tap('/')

            while not seen(pos[0], pos[1], (24, 24, 24), tol=50, sample_half=2):
                if not g_toggle:
                    break
                click(pos[0], pos[1], delay =0.1)
                time.sleep(0.8)

            scroll(1000)
            click(1112, 309, delay =0.1)

        elif upgrade == "damage":
            pos = (954, 415)
            click(765, 497, delay=0.1)
            scroll(-1000)
            time.sleep(0.2)
            tap('/')
            tap('down'); tap('down'); tap('down'); tap('down')
            tap('/')

            while not seen(pos[0], pos[1], (24, 24, 24), tol=50, sample_half=2):
                if not g_toggle:
                    break
                click(pos[0], pos[1], delay =0.1)
                time.sleep(0.8)

            scroll(1000)
            click(1112, 309, delay =0.1)

        elif upgrade == "speed":
            pos = (956, 566)
            click(765, 497, delay=0.1)
            scroll(-1000)
            time.sleep(0.2)
            tap('/')
            tap('down'); tap('down'); tap('down'); tap('down')
            tap('/')

            while not seen(pos[0], pos[1], (24, 24, 24), tol=50, sample_half=2):
                if not g_toggle:
                    break
                click(pos[0], pos[1], delay =0.1)
                time.sleep(0.8)

            scroll(1000)
            click(1112, 309, delay =0.1)

        elif upgrade == "armor":
            pos = (954, 561)
            click(765, 497, delay=0.1)
            scroll(-1000)
            time.sleep(0.2)
            tap('/')
            tap('down'); tap('down'); tap('down'); tap('down'); tap('down')
            tap('/')

            while not seen(pos[0], pos[1], (24, 24, 24), tol=50, sample_half=2):
                if not g_toggle:
                    break
                click(pos[0], pos[1], delay =0.1)
                time.sleep(0.8)

            scroll(1000)
            click(1112, 309, delay =0.1)

    print(f"Purchased {upgrade}")


def secure_select(pos: tuple[int, int]):
    click(pos[0], pos[1], delay =0.1)
    time.sleep(0.5)

    # Wait until the “selected” UI pixel is white
    while not pixel_matches_seen(607, 381, (255, 255, 255), tol=25, sample_half=2):
        if bt.does_exist('Winter/Erza_Armor.png', confidence=0.8, grayscale=True):
            click(752, 548, delay =0.1)
            time.sleep(0.6)

        click(pos[0], pos[1], delay =0.1)
        time.sleep(0.8)

    print(f"Selected unit at {pos}")

#Image recognition
def find_image_center(img_path: str, confidence: float = 0.8, grayscale: bool = False, region=None):
    """
    Returns (cx, cy, box) where box=(left, top, width, height), or (None, None, None) if not found.
    region is (left, top, width, height)
    """
    box = pyautogui.locateOnScreen(img_path, confidence=confidence, grayscale=grayscale, region=region)
    if not box:
        return None, None, None
    cx, cy = pyautogui.center(box)
    return int(cx), int(cy), box


def place_unit(unit: str, pos: tuple[int, int], close: bool | None = None, region: tuple | None = None):
    """
    Places a unit found in Winter/UNIT_hb.png at location given in pos.
    mac/Retina-safe: uses screenshot-based pixel checks.
    """

    # Tunables
    time_out = 20          # placement loop attempts
    time_out_2 = 50        # time to wait for hotbar icon to appear
    white_ui = (255, 255, 255)

    # 1) Wait for the unit icon to exist, then click it
    if region is None:
        while not bt.does_exist(f"Winter/{unit}_hb.png", confidence=0.8, grayscale=False):
            if time_out_2 <= 0:
                break
            time_out_2 -= 1
            time.sleep(0.1)
        bt.click_image(f"Winter/{unit}_hb.png", confidence=0.8, grayscale=False, offset=(0, 0))
    else:
        while not bt.does_exist(f"Winter/{unit}_hb.png", confidence=0.8, grayscale=False, region=region):
            if time_out_2 <= 0:
                break
            time_out_2 -= 1
            time.sleep(0.1)
        bt.click_image(f"Winter/{unit}_hb.png", confidence=0.8, grayscale=False, offset=(0, 0), region=region)

    time.sleep(0.2)

    # 2) Try to place it
    click(pos[0], pos[1], delay=0.67)
    time.sleep(0.5)

    # Keep attempting until the “close/back” pixel becomes white (means menu closed / placement done)
    while not pixel_matches_seen(607, 381, white_ui, tol=25, sample_half=2):
        time_out -= 1
        if time_out <= 0:
            print("timed out")
            break
        if not g_toggle:
            break

        click(pos[0], pos[1], delay=0.67)

        seen = pixel_color_seen(607, 381, sample_half=2)
        print(f"Target Color: {white_ui}, seen: {seen}")

        time.sleep(0.1)
        tap('q')  # your “cancel/rotate/nudge” behaviour
        time.sleep(0.5)

        click(pos[0], pos[1], delay=0.1)
        time.sleep(1)

        # If the game shows “UnitExists” we’re done (unit placed)
        if bt.does_exist("Winter/UnitExists.png", confidence=0.9, grayscale=True):
            break

        # If we *now* see the UI pixel is white, also done
        if pixel_matches_seen(607, 381, white_ui, tol=25, sample_half=2):
            break

        # Re-click hotbar icon to re-arm placement if needed
        print("Retrying placement...")
        try:
            if region is None:
                bt.click_image(f"Winter/{unit}_hb.png", confidence=0.8, grayscale=False, offset=(0, 0))
            else:
                bt.click_image(f"Winter/{unit}_hb.png", confidence=0.8, grayscale=False, offset=(0, 0), region=region)
            time.sleep(0.2)
        except Exception as e:
            print(f"Error {e}")

        time.sleep(0.2)

    if close:
        click(607, 381, delay =0.1)

    print(f"Placed {unit} at {pos}")

def place_unit(unit: str, pos: tuple[int, int], close: bool | None = None, region: tuple | None = None):
    # -----------------------
    # Debug helpers
    # -----------------------
    DEBUG = False
    DEBUG_EVERY_N_LOOPS = 3          # save a screenshot every N placement loops
    UI_PIXEL = (607, 381)            # your “close/back” pixel
    UI_TARGET = (255, 255, 255)      # expected color when closed/ready
    UI_TOL = 25
    SAMPLE_HALF = 2

    script_dir = os.path.dirname(os.path.abspath(__file__))
    debug_dir = os.path.join(RESOURCES_DIR, "DebugShots")
    os.makedirs(debug_dir, exist_ok=True)

    def lt_rb_to_region(l, t, r, b):
        return (l, t, r - l, b - t)

    def stamp():
        return datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    def ui_seen():
        """Return the current seen RGB for UI pixel."""
        try:
            return pixel_color_seen(UI_PIXEL[0], UI_PIXEL[1], sample_half=SAMPLE_HALF)
        except Exception as e:
            print(f"[DEBUG] ui_seen error: {e}")
            return None

    def ui_is_target():
        """Return True if UI pixel matches target."""
        try:
            return pixel_matches_seen(UI_PIXEL[0], UI_PIXEL[1], UI_TARGET, tol=UI_TOL, sample_half=SAMPLE_HALF)
        except Exception as e:
            print(f"[DEBUG] ui_is_target error: {e}")
            return False


    # Tunables
    time_out_place = 20     # placement loop attempts
    time_out_icon = 50      # time to wait for hotbar icon to appear

    if DEBUG:
        print(f"\n[place_unit] unit={unit} pos={pos} close={close} region={region}")
        print(f"[place_unit] starting UI pixel seen={ui_seen()} target={UI_TARGET} tol={UI_TOL}")


    # 1) Wait for hotbar icon to exist
    icon_path = asset_path(f"Winter/{unit}_hb.png")

    if DEBUG:
        print(f"[place_unit] waiting for icon: {icon_path} (timeout={time_out_icon})")

    icon_found = False
    while time_out_icon > 0 and g_toggle:
        try:
            icon_found = bt.does_exist(icon_path, confidence=0.8, grayscale=False, region=region) if region else \
                         bt.does_exist(icon_path, confidence=0.8, grayscale=False)
        except Exception as e:
            print(f"[DEBUG] bt.does_exist(icon) error: {e}")
            icon_found = False

        if icon_found:
            break

        time_out_icon -= 1
        time.sleep(0.3)

    if not icon_found:
        print(f"[place_unit][WARN] icon NOT found for {unit} (giving up icon stage).")
        # snap("ICON_NOT_FOUND")
    else:
        if DEBUG:
            print(f"[place_unit] icon found -> clicking icon now")

        try:
            # Some bt.click_image implementations return True/False — log it either way
            clicked = bt.click_image(icon_path, confidence=0.8, grayscale=False, offset=(0, 0), region=region) if region else \
                      bt.click_image(icon_path, confidence=0.8, grayscale=False, offset=(0, 0))
            if DEBUG:
                print(f"[place_unit] bt.click_image returned: {clicked}")
        except Exception as e:
            print(f"[place_unit][ERROR] bt.click_image failed: {e}")
            # snap("ICON_CLICK_ERROR")

    time.sleep(0.2)

    # -----------------------
    # 2) Initial placement click
    # -----------------------
    if DEBUG:
        print(f"[place_unit] initial click at placement position {pos}")
        # snap("BEFORE_PLACE_CLICK")

    click(pos[0], pos[1], delay=0.67)
    time.sleep(0.5)

    if DEBUG:
        print(f"[place_unit] after initial click, UI pixel seen={ui_seen()}, ui_is_target={ui_is_target()}")

    # -----------------------
    # 3) Placement loop
    # -----------------------
    loops = 0
    while not ui_is_target():
        loops += 1
        time_out_place -= 1

        if not g_toggle:
            print("[place_unit] stopped (g_toggle=False)")
            # snap("STOPPED")
            break

        if time_out_place <= 0:
            print("[place_unit][WARN] timed out trying to place unit.")
            print(f"[place_unit][WARN] last UI pixel seen={ui_seen()} expected={UI_TARGET}")
            # snap("PLACE_TIMEOUT")
            break

        if DEBUG:
            print(f"[place_unit] loop={loops} remaining={time_out_place} ui_seen={ui_seen()}")

        if DEBUG and (loops % DEBUG_EVERY_N_LOOPS == 0):
            # snap(f"LOOP_{loops}")
            pass

        # Try clicking the placement point again
        click(pos[0], pos[1], delay=0.67)

        # Optional: your cancel/nudge behaviour
        time.sleep(0.1)
        tap('q')
        time.sleep(0.5)

        # Another quick click
        click(pos[0], pos[1], delay=0.1)
        time.sleep(1)

        # Check UnitExists
        try:
            exists = bt.does_exist("Winter/UnitExists.png", confidence=0.9, grayscale=True)
        except Exception as e:
            print(f"[DEBUG] bt.does_exist(UnitExists) error: {e}")
            exists = False

        if DEBUG:
            print(f"[place_unit] UnitExists={exists}, ui_is_target={ui_is_target()}, ui_seen={ui_seen()}")

        if exists:
            if DEBUG:
                print("[place_unit] UnitExists detected -> stopping loop")
            # snap("UNIT_EXISTS_DETECTED")
            break

        if ui_is_target():
            if DEBUG:
                print("[place_unit] UI pixel became target -> stopping loop")
            # snap("UI_TARGET_REACHED")
            break

        # Re-arm by clicking the hotbar icon again
        if DEBUG:
            print("[place_unit] re-arming by clicking hotbar icon again")

        try:
            clicked = bt.click_image(icon_path, confidence=0.8, grayscale=False, offset=(0, 0), region=region) if region else \
                      bt.click_image(icon_path, confidence=0.8, grayscale=False, offset=(0, 0))
            if DEBUG:
                print(f"[place_unit] re-arm bt.click_image returned: {clicked}")
        except Exception as e:
            print(f"[place_unit][ERROR] re-arm click_image failed: {e}")
            # snap("REARM_CLICK_ERROR")

        time.sleep(0.2)

    # -----------------------
    # 4) Close UI if requested
    # -----------------------
    if close:
        if DEBUG:
            print("[place_unit] close=True -> clicking close/back pixel")
        click(UI_PIXEL[0], UI_PIXEL[1], delay =0.1)

    if DEBUG:
        print(f"[place_unit] finished. final ui_seen={ui_seen()} ui_is_target={ui_is_target()}")
        # snap("END")

    print(f"Placed {unit} at {pos}")

def buy_monarch():  # this just presses e until it buys monarch, use after direction('5')
    monarch_region = (686, 606, 818, 646)
    e_delay = 0.4
    timeout = 3/e_delay
    tap('e')
    while not bt.does_exist('Winter/DetectArea.png',confidence=0.7,grayscale=True):
        if bt.does_exist('Winter/Monarch.png',confidence=0.7,grayscale=False):
            break
        if timeout < 0:
            quick_rts()
            directions('5')
            timeout = 3/e_delay
        timeout-=1
        tap('e')
        time.sleep(e_delay)
    print("Found area")
    while not bt.does_exist('Winter/Monarch.png',confidence=0.7,grayscale=False):
        if not g_toggle:
            break
        tap('e')
        time.sleep(0.8)
    print("Got monarch")

def place_hotbar_units():
    # Scans and places all units in your hotbar, tracking them too
    placing = True
    while placing:
        is_unit = False
        for unit in Settings.Units_Placeable:
            if bt.does_exist(f"Winter/{unit}_hb.png", confidence=0.8, grayscale=False):
                if unit != "Doom":
                    is_unit = True
                    unit_pos = Settings.Unit_Positions.get(unit)
                    index = Settings.Unit_Placements_Left.get(unit)-1
                    if index <0:
                        is_unit = False
                    print(f"Placing unit {unit} {index+1} at {unit_pos}")
                    place_unit(unit, unit_pos[index])
                    if unit == 'Kag':
                        if USE_KAGUYA:
                            kag_ability = [(645, 444), (743, 817), (1091, 244)]
                            for cl in kag_ability:
                                if cl == (743, 817):
                                    bt.click_image("Winter/Kaguya_Auto.png", confidence=0.8, grayscale=False, offset=[0,0]) 
                                else:
                                    click(cl[0],cl[1],delay =0.1)
                                    time.sleep(1)
                else:
                    doom = (572, 560)
                    place_unit(unit,doom)
                    time.sleep(2)
                    set_boss()
                    tap('z')
                    click(607, 381, delay =0.1)
                    directions('5')
                    buy_monarch()
                    quick_rts()
                    click(doom[0],doom[1],delay =0.1)
                if unit != "Doom":
                    Settings.Unit_Placements_Left[unit]-=1
                    print(f"Placed {unit} | {unit} has {Settings.Unit_Placements_Left.get(unit)} placements left.")
                else:
                    print("Placed doom slayer.")
        if is_unit == False:
            click(600,380, delay =0.1)
            placing = False
            
def ainz_setup(unit:str): 
    '''
    Set's up ainz's abilities and places the unit given.
    '''
    pos  = [(646, 513), (526, 622), (779, 439), (779, 511), (503, 400), (524, 541), (781, 491), (506, 398), (681, 458), (778, 506), (959, 645), (750, 559), (649, 587), (690, 677), (503, 377), (495, 456), (618, 521)]
    for v,i in enumerate(pos):
        if AINZ_SPELLS and v<12:
            #491,458
            continue
        if v == 12: # the click to open world items
            print("Selected Spells")
            click(Settings.Unit_Positions['Ainz'][0][0], Settings.Unit_Positions['Ainz'][0][1], delay =0.1)
            print("Waiting for world item logo")
            while not bt.does_exist("Winter/CaloricThing.png",confidence=0.8,grayscale=False):
                time.sleep(0.5)
            print(f"Placing unit {unit}")
        click(i[0],i[1],delay =0.1)
    
        time.sleep(1)
        
        if v == 14:
            write_text(unit)
        time.sleep(0.5)

def repair_barricades(): # Repair barricades 
    #DIR_BARRICADE
    tap('v')
    time.sleep(1)
    press('a')
    time.sleep(0.7)
    release('a')
    tap('e')
    tap('e')
    press('w')
    time.sleep(0.2)
    release('w')
    tap('e')
    tap('e')
    press('s')
    time.sleep(0.4)
    release('s')
    tap('e')
    tap('e')
    time.sleep(1)
    tap('v')
    time.sleep(2)
    
def set_boss(): # Sets unit priority to boss
    tap('r')
    tap('r')
    tap('r')
    tap('r')
    tap('r')
    
def on_failure():
    print("ran")
    time_out = 60/0.4
    click(Settings.REPLAY_BUTTON_POS[0],Settings.REPLAY_BUTTON_POS[1],delay =0.1)
    time.sleep(1)
    while bt.does_exist("Winter/DetectLoss.png",confidence=0.7,grayscale=False):
        if time_out<0:
            #on_disconnect()
            print("should disconnect")
        click(Settings.REPLAY_BUTTON_POS[0],Settings.REPLAY_BUTTON_POS[1],delay =0.1)
        print("Retrying...")
        time_out-=1
        time.sleep(0.4)
    click(Settings.REPLAY_BUTTON_POS[0],Settings.REPLAY_BUTTON_POS[1],delay =0.1)
    

def sell_kaguya(): # Sells kaguya (cant reset while domain is active)
    sold = False
    tick = 0
    click(1119, 450,delay =0.1)
    time.sleep(1)
    while not sold:
        sell = bt.click_image('Winter/Kaguya.png',confidence=0.8,grayscale=False,offset=[0,0])
        if g_toggle == False:
            break
        if sell == True:
            time.sleep(1)
            tap('x')
            sold = True
        scroll(-100)
        tick+=1
        if tick>=40:
            sold = True
        time.sleep(0.4)

def detect_loss():
    time.sleep(10)
    print("Starting loss detection")

    loss_rgb_1 = (235, 73, 67)
    loss_rgb_2 = (222, 55, 45)

    while True:
        # screenshot-based pixel match (Retina-safe)
        is_loss = (
            pixel_matches_seen(532, 287, loss_rgb_1, tol=10, sample_half=2)
            or pixel_matches_seen(693, 283, loss_rgb_2, tol=10, sample_half=2)
        )

        if is_loss:
            print("found loss -> attempting on_failure()")
            try:
                on_failure()
                time.sleep(6)
            except Exception as e:
                print(f"on_failure crashed ({e}) -> restarting script")
                args = list(sys.argv)
                for flag in ("--stopped", "--restart"):
                    if flag in args:
                        args.remove(flag)
                sys.stdout.flush()
                subprocess.Popen([sys.executable, *args])
                os._exit(0)

        time.sleep(1)
        
def main():
    print("Starting Winter Event Macro")
    rabbit_pos = Settings.Unit_Positions.get("mirko")
    speed_pos =  Settings.Unit_Positions.get("speedwagon")
    start_of_run = datetime.now()
    num_runs = 0  
    while True:
        if ROUND_RESTART > 0:
            print("restart")
            if num_runs >= ROUND_RESTART:
                try:
                    print("recconect")
                    args = list(sys.argv)
                    if "--stopped" in args:
                        args.remove("--stopped")
                    sys.stdout.flush()
                    subprocess.Popen([sys.executable, *args, "--restart"])
                    os._exit(0)
                except Exception as e:
                    print(e)
        global g_toggle
        if g_toggle:
            # Reset all placement counts:
            Reset_Placements = {
                "Ainz": 1,
                'Beni': 3,
                'Rukia': 3,
                'Mage': 3,
                'Escanor': 1,
                'Hero': 3,
                'Kuzan':4,
                'Kag':1
            }   
            if not USE_KAGUYA:
                Reset_Placements['Kag'] = 0
                
            Settings.Unit_Placements_Left = Reset_Placements.copy()
            
            print("Starting new match")
            wait_start()
            quick_rts()
            time.sleep(2)
            # Set up first 2 rabbits
            got_mirko = False
            while not got_mirko:
                directions('1', 'rabbit')
                tap('e')
                tap('e')
                quick_rts()
                time.sleep(1.5)
                got_mirko = True
                if bt.does_exist("Winter/Bunny_hb.png",confidence=0.7,grayscale=False, region=SLOT_ONE):
                    print("Got mirko")
                    got_mirko = True
                else:
                    print("Didnt detect mirko, retrying purchase")
            click(835, 226, delay =0.1) # Start Match
            
            
            place_unit('Bunny', rabbit_pos[0], close=True)
            time.sleep(3)
            place_unit('Bunny', rabbit_pos[1], close=True)
            print("Placed first 2 rabbits")
            # get third
            got_mirko_two = False
            while not got_mirko_two:
                print("Attempting to buy third rabbit")
                directions('1', 'rabbit')
                tap('e')
                quick_rts()
                time.sleep(1.5)
                got_mirko_two = True
                # if bt.does_exist("Winter/Bunny_hb.png",confidence=0.7,grayscale=False, region=SLOT_ONE):
                #     print("Got mirko")
                #     got_mirko_two = True
                # else:
                #     print("Didnt detect mirko, retrying purchase")
            place_unit('Bunny', rabbit_pos[2], close=True)
            
            #Start farms - speedwagon
            directions('2', 'speed')
            tap('e')
            tap('e')
            tap('e')
            place_unit('Speed', speed_pos[0], close=True)
            place_unit('Speed', speed_pos[1], close=True)
            place_unit('Speed', speed_pos[2], close=True)
            for pos in speed_pos:
                click(pos[0], pos[1], delay =0.1)
                time.sleep(0.5)
                tap('z')
                time.sleep(0.5)
            click(607, 381, delay =0.1)
            
            # Tak's placement + max
            

            if bt.does_exist("Winter/Tak_Detect.png",confidence=0.8,grayscale=True):
                bt.click_image("Winter/Tak_Detect.png",confidence=0.8,grayscale=True,offset=(0,-20))   
                click(50,50,delay=0.1,right_click=True,dont_move=True)
            else:
                press('w')
                time.sleep(Settings.TAK_W_DELAY)
                release('w')
            if TAK_FINDER:
                path_tak = False
                while not path_tak:
                    press('w')
                    time.sleep(0.1)
                    release('w')
                    tap('e')
                    time.sleep(0.4)
                    if bt.does_exist('Winter/TakDetect.png', confidence=0.7, grayscale=True,region=(581, 676, 958, 752)) or  bt.does_exist('Winter/Tak_hb.png', confidence=0.7, grayscale=False):
                        path_tak = True
                    time.sleep(0.5)
            # Press e until tak is bought
            while not bt.does_exist('Winter/Tak_hb.png', confidence=0.7, grayscale=False):
                tap('e')
                time.sleep(0.2)
            
            place_unit("Tak", Settings.Unit_Positions.get("tak"))
            tap('z')
            time.sleep(0.5)
            click(607, 381, delay =0.1)
            
            #DIR_NAMICARD
            if bt.does_exist("Winter/Nami_detect.png",confidence=0.8,grayscale=True):
                bt.click_image("Winter/Nami_detect.png",confidence=0.8,grayscale=True,offset=(0,0))   
                click(50,50,delay=0.1,right_click=True,dont_move=True)
            else:
                click(Settings.CTM_NAMI_CARD[0], Settings.CTM_NAMI_CARD[1], delay =0.1, right_click=True) # Goes to nami's card
            time.sleep(2)
            #Nami
            while not bt.does_exist('Winter/Nami_hb.png', confidence=0.7, grayscale=False): # Buys nami's card
                tap('e')
                time.sleep(0.2)
            quick_rts()
            place_unit('Nami',(755, 524)) # Nami placement
            tap('z')
            click(607, 381, delay =0.1)

            # Go to upgrader for fortune
            directions('4')
            upgrader('fortune')
            click(1112, 312, delay =1)
            quick_rts()
            
            # Start auto upgrading first rabbit
            secure_select(rabbit_pos[0])
            time.sleep(0.5)
            tap('z')
            click(607, 381, delay =0.1)
            
            # get +100% dmg upgrade
            directions('4')
            upgrader('damage')
            click(1112, 312, delay =0.1)
            quick_rts()
            
            # Start auto upgrading rabbit 1 & 2
            secure_select(rabbit_pos[1])
            time.sleep(0.5)
            tap('z')
            click(607, 381, delay =0.1)
            time.sleep(1)
            secure_select(rabbit_pos[2])
            time.sleep(0.5)
            tap('z')
            click(607, 381, delay =0.1)
            time.sleep(1)
            
            # Get first monarch
            directions('5')
            buy_monarch()
            quick_rts()
            time.sleep(1)
            secure_select(rabbit_pos[0])
            
            # Wave 19 lane unlocks for 20% boost
            wave_19 = False

            while not wave_19 and g_toggle:
                w = avM.get_wave_from_screen()  # re-read each loop

                if w is not None:
                    print("Wave reached:", w)

                    if w >= 19:
                        # DIR_BUYMAINLANES
                        press('d')
                        time.sleep(Settings.BUY_MAIN_LANE_DELAYS[0])
                        release('d')

                        tap('e'); tap('e')

                        press('w')
                        time.sleep(Settings.BUY_MAIN_LANE_DELAYS[1])
                        release('w')

                        tap('e'); tap('e')

                        wave_19 = True
                        break

                time.sleep(0.5)
    
            # Get 2nd and 3rd bunny monarch'd
            quick_rts()
            directions('5')
            buy_monarch()
            quick_rts()
            time.sleep(1)
            secure_select(rabbit_pos[1])
            time.sleep(1)
            directions('5')
            buy_monarch()
            quick_rts()
            time.sleep(1)
            secure_select(rabbit_pos[2])
            
            # Get all upgrades
            directions('4')
            upgrader('range')
            upgrader('speed')
            upgrader('armor')
            click(1112, 312, delay =0.1)
            quick_rts()
            directions('3')
            
            Ben_Upgraded = False
            Erza_Upgraded = False
            
            # Lucky box
            gamble_done = False
            g_toggle= True
            ainzplaced=False
            while not gamble_done:
                for i in range(5):
                    tap('e')
                    time.sleep(0.05)
                
                
                full_bar = bt.does_exist("Winter/Full_Bar.png", confidence=0.7, grayscale=True)
                no_yen = bt.does_exist("Winter/NO_YEN.png", confidence=0.7, grayscale=True)

                print(f"[TEST] full_bar={full_bar} no_yen={no_yen}")
                if full_bar or no_yen:
                    print("Getting Units")
                    quick_rts()
                    time.sleep(3)
                    place_hotbar_units()
                    directions('3')
                if not Erza_Upgraded:
                    print("Buffing Erza")
                    erza_buffer = Settings.Unit_Positions['Mage']
                    if Settings.Unit_Placements_Left['Mage'] == 0:
                        quick_rts()
                        time.sleep(1)
                        # Buffer
                        secure_select(erza_buffer[0])
                        time.sleep(8)
                        click(378,662)
                        time.sleep(0.8)
                        click(647, 449,delay =0.1)
                        while not bt.does_exist('Winter/Erza_Armor.png',confidence=0.8,grayscale=True):
                            click(1015,690,delay =0.1)
                            time.sleep(0.5)
                        click(752, 548,delay =0.1)
                        time.sleep(0.5)
                        click(1140, 290,delay =0.1)
                        time.sleep(0.5)
                        click(607, 381, delay =0.1)
                            
                        #Duelist 1
                        secure_select(erza_buffer[1])
                        time.sleep(0.8)
                        tap('z')
                        click(647, 449,delay =0.1)
                        while not bt.does_exist('Winter/Erza_Armor.png',confidence=0.8,grayscale=True):
                            click(747, 690,delay =0.1)
                            time.sleep(0.5)
                        click(752, 548,delay =0.1)
                        time.sleep(0.5)
                        click(1140, 290,delay =0.1)
                        set_boss()
                        time.sleep(0.5)
                        
                        #Duelist 2
                        secure_select(erza_buffer[2])
                        time.sleep(0.8)
                        click(647, 449,delay =0.1)
                        tap('z')
                        while not bt.does_exist('Winter/Erza_Armor.png',confidence=0.8,grayscale=True):
                            click(747, 690,delay =0.1)
                            time.sleep(0.5)
                        click(752, 548,delay =0.1)
                        time.sleep(0.5)
                        click(1140, 290,delay =0.1)
                        set_boss()
                        time.sleep(0.5)
                        click(607, 381, delay =0.1)
                        
                        directions('5')
                        buy_monarch()
                        quick_rts()
                        click(erza_buffer[1][0],erza_buffer[1][1],delay =0.1)
                        time.sleep(0.5)
                        
                        directions('5')
                        buy_monarch()
                        quick_rts()
                        click(erza_buffer[2][0],erza_buffer[2][1],delay =0.1)
                        time.sleep(0.5)
                        Erza_Upgraded = True
                        # more gamble
                        directions('3')
                if not Ben_Upgraded:
                    print("Upgrading Beni")
                    if Settings.Unit_Placements_Left['Beni'] == 0:
                        quick_rts()
                        time.sleep(1)
                        for ben in Settings.Unit_Positions['Beni']:
                            click(ben[0],ben[1],delay =0.1)
                            secure_select((ben[0],ben[1]))
                            time.sleep(0.5)
                            tap('z')
                            set_boss()
                            time.sleep(0.5)
                            click(607, 381, delay =0.1)
                            directions('5')
                            buy_monarch()
                            quick_rts()
                            time.sleep(0.5)
                            secure_select((ben[0],ben[1]))
                            time.sleep(0.5)
                            click(607, 381, delay =0.1)
                        Ben_Upgraded = True
                        # more gamble
                        directions('3')
                if not ainzplaced:
                    print("Ainz stuff")
                    if Settings.Unit_Placements_Left['Ainz'] == 0: # Ainz thingy
                        ainzplaced = True
                        quick_rts()
                        time.sleep(1)
                        ainz_pos = Settings.Unit_Positions['Ainz']
                        pos = Settings.Unit_Positions.get("Caloric_Unit")
                        secure_select((ainz_pos[0]))
                        time.sleep(0.5)
                        if Settings.USE_WD == True:
                            ainz_setup(unit="world des")
                        elif Settings.USE_DIO == True:
                            ainz_setup(unit="god")
                        elif USE_BUU:
                            ainz_setup(unit="boo")
                        else:
                            ainz_setup(unit=Settings.USE_AINZ_UNIT)
                        global AINZ_SPELLS
                        if not AINZ_SPELLS:
                            AINZ_SPELLS = True
                        click(pos[0], pos[1], delay=0.67) # Place world destroyer + auto upgrade
                        time.sleep(0.5)
                        while not pixel_matches_seen(607, 381, (255, 255, 255), tol=20, sample_half=2):
                            if not g_toggle:
                                break

                            click(pos[0], pos[1], delay=0.67)
                            time.sleep(0.5)

                        time.sleep(1)
                        if Settings.USE_DIO:
                            ability_clicks = [(648, 448), (1010, 563), (1099, 309)]
                            for p in ability_clicks:
                                click(p[0], p[1], delay =0.1)
                                time.sleep(1.2)
                        if Settings.MAX_UPG_AINZ_PLACEMENT:
                            tap('z')
                        if Settings.MONARCH_AINZ_PLACEMENT:
                            directions('5')
                            buy_monarch()
                            quick_rts()
                            time.sleep(1)
                            click(pos[0], pos[1], delay=0.67) 
                        time.sleep(1)
                        print("Placed ainz's unit")
                        click(607, 381, delay =0.1)
                        
                        # Ainz auto upgrade + monarch
                        secure_select((ainz_pos[0]))
                        time.sleep(0.5)
                        tap('z')
                        time.sleep(0.5)
                        click(607, 381, delay =0.1)
                        directions('5')
                        buy_monarch()
                        quick_rts()
                        time.sleep(1)
                        click(ainz_pos[0][0],ainz_pos[0][1],delay =0.1)
                        time.sleep(1)
                        # go gamble more son
                        directions('3')
                print("===============================")
                is_done = True
                for unit in Settings.Units_Placeable:
                    if unit != "Doom":
                        if Settings.Unit_Placements_Left[unit] > 0:
                            is_done = False
                            print(f"{unit} has {Settings.Unit_Placements_Left[unit]} placements left.")
                print("===============================")
                if is_done:
                    gamble_done = True
                time.sleep(0.1)
            print("Gambling done")
             
               

            # Auto upgrade + Monarch everything else
            
            # set up buffer erza
            
            quick_rts()
            time.sleep(1)
    
            # World destroyer
            if Settings.USE_WD:
                secure_select(Settings.Unit_Positions.get("Caloric_Unit"))
                time.sleep(1)
                while True:
                    print("Upgrading")
                    if bt.does_exist("Winter/StopWD.png",confidence=0.8,grayscale=False):
                        print("Stop")
                        break
                    if bt.does_exist("Unit_Maxed.png",confidence=0.8,grayscale=False):
                        print("Stop, maxed on accident")
                        break
                    tap('t') #Upgrade Hotkey
                    time.sleep(0.5)
                time.sleep(0.5)
                click(607, 381, delay =0.1)
            elif Settings.USE_DIO:
                secure_select(Settings.Unit_Positions.get("Caloric_Unit"))
                time.sleep(1)
                while True:
                    if bt.does_exist("Winter/DIO_MOVE.png",confidence=0.8,grayscale=False):
                        print("Stop")
                        break
                    if bt.does_exist("Unit_Maxed.png",confidence=0.8,grayscale=False):
                        print("Stop, maxed on accident")
                        break
                    tap('t')
                    time.sleep(0.5)
                time.sleep(0.5)
                click(607, 381, delay =0.1)
            elif USE_BUU:
                secure_select(Settings.Unit_Positions.get("Caloric_Unit"))
                time.sleep(1)
                while True:
                    if bt.does_exist("Winter/Buu_Ability.png",confidence=0.5,grayscale=False):
                        print("Found Ability")
                        bt.click_image("Winter/Buu_Ability.png",confidence=0.5,grayscale=False,offset=(0,0))
                        time.sleep(1)
                        click(441,151,0.2)
                        time.sleep(1)
                    if bt.does_exist("Winter/BuuSellDetect.png",confidence=0.8,grayscale=False, ):
                        print("SellBuu")
                        tap('x')
                        break
                    if not bt.does_exist("Winter/Unit_Maxed.png",confidence=0.8,grayscale=False):
                        print("Upgrade")
                        tap('t')
                        time.sleep(.1) 
            elif Settings.MAX_UPG_AINZ_PLACEMENT == False:
                secure_select(Settings.Unit_Positions.get("Caloric_Unit"))
                time.sleep(1)
                while True:
                    if bt.does_exist("Winter/YOUR_MOVE.png",confidence=0.8,grayscale=False):
                        print("Stop")
                        break
                    if bt.does_exist("Unit_Maxed.png",confidence=0.8,grayscale=False):
                        print("Stop, maxed on accident")
                        break
                    tap('t')
                    time.sleep(0.5)
                time.sleep(0.5)
                click(607, 381, delay =0.1)
            
            # ice queen
            for ice in Settings.Unit_Positions['Rukia']:
                 
                secure_select((ice[0],ice[1]))
                time.sleep(0.5)
                set_boss()
                time.sleep(0.5)
                click(607, 381, delay =0.1)
                directions('5')
                buy_monarch()
                quick_rts()
                time.sleep(0.5)
                secure_select((ice[0],ice[1]))
                time.sleep(0.5)
                while True:
                    if bt.does_exist("Winter/StopUpgradeRukia.png",confidence=0.8,grayscale=True):
                        print("Stop")
                        break
                    if bt.does_exist("Unit_Maxed.png",confidence=0.8,grayscale=False):
                        print("Stop, maxed on accident")
                        break
                    tap('t')
                    time.sleep(0.5)
                time.sleep(0.5)
                click(607, 381, delay =0.1)
             
               

                
            for gamer in Settings.Unit_Positions['Hero']:
                 

                click(gamer[0],gamer[1],delay =0.1)
                time.sleep(0.5)
                tap('z')
                set_boss()
                time.sleep(0.5)
                click(607, 381, delay =0.1)
                directions('5')
                buy_monarch()
                quick_rts()
                time.sleep(0.5)
                click(gamer[0],gamer[1],delay =0.1)
                time.sleep(0.5)
                click(607, 381, delay =0.1)
             
            
            for kuzan in Settings.Unit_Positions['Kuzan']:
                click(kuzan[0],kuzan[1],delay =0.1)
                time.sleep(0.5)
                tap('z')
                set_boss()
                time.sleep(0.5)
                click(607, 381, delay =0.1)
                directions('5')
                buy_monarch()
                quick_rts()
                time.sleep(0.5)
                click(kuzan[0],kuzan[1],delay =0.1)
                time.sleep(0.5)
                click(607, 381, delay =0.1)

             
               
            for esc in Settings.Unit_Positions['Escanor']:
                click(esc[0],esc[1],delay =0.1)
                time.sleep(0.5)
                tap('z')
                set_boss()
                time.sleep(0.5)
                click(607, 381, delay =0.1)
                directions('5')
                buy_monarch()
                quick_rts()
                time.sleep(0.5)
                click(esc[0],esc[1],delay =0.1)
                time.sleep(0.5)
                click(607, 381, delay =0.1)
            
 

            if Settings.WAVE_RESTART_150:
                wave_150 = False
                done_path = False

                while not wave_150:
                    w = avM.get_wave_from_screen()

                    # If OCR failed, skip this loop tick safely
                    if w is None:
                        time.sleep(0.5)
                        continue

                    # Run once on confirmed wave 149
                    if (not done_path) and w == 149:
                        print("Confirmed wave 149 — running pre-150 logic")

                        quick_rts()

                        tap('f')  # Unit Manager Hotkey
                        time.sleep(0.7)

                        ok = bt.click_image(
                            "Winter/LookDownFinder.png",
                            confidence=0.8,
                            grayscale=False,
                            offset=(0, -50)   # <- make this a tuple, not a list
                        )
                        print("[LookDownFinder click] ok =", ok)

                        tap('f')

                        # ONLY start spamming E after the menu / setup step is done
                        def spam_e():
                            while not done_path:
                                tap('e')
                                time.sleep(0.2)
                            print("Done buying lanes")

                        Thread(target=spam_e, daemon=True).start()

                        clicks_look_down = [(401, 404), (649, 777), (750, 875)]
                        for pt in clicks_look_down:
                            click(pt[0], pt[1], delay=0.1)
                            time.sleep(1 if pt == (649, 777) else 0.2)

                        press('o'); time.sleep(1); release('o')

                        press('s'); time.sleep(Settings.BUY_FINAL_LANE_DELAYS[0]); release('s')

                        tap('v'); time.sleep(1)

                        press('a'); time.sleep(Settings.BUY_FINAL_LANE_DELAYS[1]); release('a')
                        press('d'); time.sleep(Settings.BUY_FINAL_LANE_DELAYS[2]); release('d')

                        tap('v')
                        quick_rts()
                        time.sleep(2)

                        done_path = True

                    # Exit when 150 is reached (or higher)
                    if 150 <= w <= 170:
                        wave_150 = True
                    else:
                        # Your repair logic, but using stable wave reads
                        if (w != -1 and w % 2 == 0) or w == 139:
                            repair_barricades()
                            quick_rts()

                    time.sleep(2)
            else:
                wave_140 = False
                done_path = False

                while not wave_140:
                    w = avM.get_wave_from_screen()

                    # OCR failed -> skip safely
                    if w is None:
                        time.sleep(0.5)
                        continue

                    # Run once on confirmed wave 139
                    if (not done_path) and w == 139:
                        print("Confirmed wave 139 — running pre-140 logic")

                        def spam_e():
                            while not done_path:
                                tap('e')
                                time.sleep(0.2)
                            print("Done buying lanes")

                        Thread(target=spam_e, daemon=True).start()

                        quick_rts()
                        tap('f')
                        time.sleep(0.7)
                        bt.click_image("Winter/LookDownFinder.png", confidence=0.8, grayscale=False, offset=[0, -50])
                        tap('f')

                        clicks_look_down = [(404, 400), (649, 772), (745, 858)]
                        for pt in clicks_look_down:
                            click(pt[0], pt[1], delay=0.1)
                            time.sleep(1 if pt == (649, 772) else 0.3)

                        press('o'); time.sleep(1); release('o')

                        press('s')
                        time.sleep(Settings.BUY_FINAL_LANE_DELAYS[0])
                        release('s')

                        tap('v')
                        time.sleep(1)

                        press('a')
                        time.sleep(Settings.BUY_FINAL_LANE_DELAYS[1])
                        release('a')

                        press('d')
                        time.sleep(Settings.BUY_FINAL_LANE_DELAYS[2])
                        release('d')

                        tap('v')
                        quick_rts()
                        time.sleep(2)

                        # stop spam thread
                        done_path = True

                    # Exit when 140 is reached (or higher)
                    if 140 <= w <= 170:
                        wave_140 = True
                    else:
                        # Only do modulo checks when w is a real number
                        if (w % 2 == 0) or (w == 139 and done_path):
                            repair_barricades()
                            quick_rts()

                    time.sleep(2)
            num_runs+=1
            # print(f"Run over, runs: {num_runs}")
            # try:
            #         victory = wt.screen_shot_memory()
            #         runtime = f"{datetime.now()-start_of_run}"
                
            #         g = Thread(target=webhook.send_webhook,
            #             kwargs={

            #                     "run_time": f"{str(runtime).split('.')[0]}",
            #                     "num_runs": num_runs,
            #                     "task_name": "Winter Event",
            #                     "img": victory,
            #                 },
            #             )            
            #         g.start()
            # except Exception as e:
            #     print(f" error {e}")
                
            if USE_KAGUYA:    
                ainz_pos = Settings.Unit_Positions['Ainz']
                click(ainz_pos[0][0],ainz_pos[0][1],delay =0.1)
                time.sleep(0.5)
                tap('x')
                time.sleep(0.5)
                tap('f')
                time.sleep(1)
                sell_kaguya()
                tap('f')
                
            match_restarted = False
            while not match_restarted:
                avM.restart_match() 
                time.sleep(0.5)
                if avM.get_wave() == 0:
                    match_restarted = True
                time.sleep(5)

# def disconnect_checker():
#     time.sleep(60) # intial detect delay
#     while True:
#        if bt.does_exist("Winter/Disconnected.png",confidence=0.9,grayscale=True,region=(525,353,972,646)) or bt.does_exist("Winter/Disconnect_Two.png",confidence=0.9,grayscale=True,region=(525,353,972,646)):
#         print("found disconnected")
#         try:
#             args = list(sys.argv)
#             if "--stopped" in args:
#                 args.remove("--stopped")
#             if "--restart" in args:
#                 args.remove("--restart")    
#             sys.stdout.flush()
#             subprocess.Popen([sys.executable, *args])
#             os._exit(0)
#         except Exception as e:
#             print("Error")
#         time.sleep(6)
# def _osascript(script: str) -> bool:
#     """
#     Runs AppleScript. Returns True if command succeeded.
#     Note: requires Accessibility permissions for Terminal/Python if controlling UI.
#     """
#     try:
#         subprocess.run(["osascript", "-e", script], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#         return True
#     except Exception:
#         return False

def _osascript(script: str) -> bool:
    try:
        subprocess.run(["osascript", "-e", script], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

def focus_roblox():
    # Brings Roblox to front (best effort)
    _osascript('tell application "Roblox" to activate')
    time.sleep(0.2)



# def try_position_roblox_window(x=200, y=100, w=1100, h=800):
#     """
#     Best-effort window move/resize on macOS.
#     This may fail depending on Roblox + macOS security settings.
#     If it fails, your macro can still work as long as Roblox is already positioned correctly.
#     """
#     # This targets the front window of the Roblox process.
#     # If it errors, ignore.
#     script = f'''
#     tell application "System Events"
#         tell process "Roblox"
#             try
#                 set position of front window to {{{x}, {y}}}
#                 set size of front window to {{{w}, {h}}}
#             end try
#         end tell
#     end tell
#     '''
#     _osascript(script)
#     time.sleep(0.5)

# def open_private_server():
#     """
#     Launches Roblox using a roblox:// deep link.
#     On macOS we use `open "<url>"`.
#     """
#     if not PRIVATE_SERVER_CODE:
#         # If you don't use a private server, just open Roblox normally:
#         _osascript('tell application "Roblox" to activate')
#         return

#     url = f'roblox://placeId={ROBLOX_PLACE_ID}&linkCode={PRIVATE_SERVER_CODE}/'
#     try:
#         subprocess.Popen(["open", url])
#     except Exception as e:
#         print(f"[on_disconnect] Failed to open roblox deep link: {e}")

# def on_disconnect():
#     """
#     macOS replacement for your Windows on_disconnect().
#     What it does:
#       1) Opens/launches Roblox into your private server via roblox:// link
#       2) Focuses Roblox and (optionally) tries to resize/move the window
#       3) Waits until key UI elements exist, then clicks through menus to get back in
#     """
#     print("[on_disconnect] Rejoining Roblox (mac) ...")

#     # 1) Launch / deep link
#     open_private_server()
#     time.sleep(10)

#     # 2) Focus + try window position (best effort)
#     focus_roblox()
#     try_position_roblox_window(200, 100, 1100, 800)

#     # 3) Wait until we are in-game enough for your UI automation to proceed
#     # NOTE: multi-monitor warning: make sure Roblox is on PRIMARY display
#     # otherwise coords can be "off screen".
#     # Wait until AreaIcon exists, closing popup if needed
#     while not bt.does_exist("Winter/AreaIcon.png", confidence=0.8, grayscale=False):
#         # “close popup” indicator (white X/button area)
#         if pixel_matches_seen(1085, 321, (255, 255, 255), tol=8, sample_half=2):
#             click(1083, 321, delay=0.1)
#         time.sleep(1)

# time.sleep(1)

# # One extra close attempt (same as your original)
# if pixel_matches_seen(1085, 321, (255, 255, 255), tol=8, sample_half=2):
#     click(1083, 321, delay=0.1)

# # Click the Area Icon
# bt.click_image("Winter/AreaIcon.png", confidence=0.8, grayscale=False, offset=(0, 0))
# time.sleep(3)

# # Re-open your area menu by moving and spamming E until a pixel changes
# open_menu = False
# spam_running = True

# def spam_e():
#     while spam_running and not open_menu:
#         tap('e')
#         time.sleep(0.2)

# spam_thread = Thread(target=spam_e, daemon=True)
# spam_thread.start()

# try:
#     while not open_menu:
#         click(656, 764, delay=0.1)
#         time.sleep(1)

#         press('a')
#         time.sleep(1)
#         release('a')

#         press('a')
#         time.sleep(1)
#         release('a')

#         # “menu opened” indicator pixel
#         if pixel_matches_seen(888, 269, (165, 232, 235), tol=30, sample_half=2):
#             open_menu = True
#             break

#         # If not open, try closing popup + clicking AreaIcon again
#         if pixel_matches_seen(1085, 321, (255, 255, 255), tol=8, sample_half=2):
#             click(1083, 321, delay=0.1)

#         bt.click_image("Winter/AreaIcon.png", confidence=0.8, grayscale=False, offset=(0, 0))
#         time.sleep(3)

# finally:
#     spam_running = False

#     # 5) Click through your menu sequence
#     click(454, 703, delay=0.1)
#     time.sleep(2)
#     click(659, 509, delay=0.1)
#     time.sleep(2)
#     click(301, 676, delay=0.1)
#     time.sleep(2)

#     # 6) Wait start screen
#     wait_start()

#     # 7) Your camera / scroll setup
#     press('i')
#     time.sleep(1)
#     release('i')

#     pyautogui.scroll(1000)   # mac replacement for scroll()

#     press('o')
#     time.sleep(1)
#     release('o')

#     click(488, 463, delay =0.1)

#     print("[on_disconnect] Finished reconnect routine (mac).")


# # ---- Replace your restart hook ----
# if "--restart" in sys.argv:
#     on_disconnect()

# # --- Startup / watchdog block (mac) ---

# Thread(target=disconnect_checker, daemon=True).start()

# print(f"Launched with args {sys.argv}")
# print(f"Running loxer's winter macro v{VERSION_N}")

# # If already disconnected, rejoin
# if (
#     bt.does_exist("Winter/Disconnected.png", confidence=0.9, grayscale=True, region=(525, 353, 972, 646))
#     or bt.does_exist("Winter/Disconnect_Two.png", confidence=0.9, grayscale=True, region=(525, 353, 972, 646))
# ):
#     on_disconnect()
#     time.sleep(6)

# Loss Detector
Thread(target=detect_loss, daemon=True).start()

# # ✅ On mac: don't use pygetwindow coordinate checks.
# # Instead, do a quick sanity check that Roblox UI is visible.
# # (Example: confirm AreaIcon exists or Roblox is focused)
# try:
#     # If this fails, you likely aren't in the Roblox window or coords are wrong.
#     # Not fatal, but helps you catch issues early.
#     focus_roblox()
#     time.sleep(0.5)
# except Exception as e:
#     print(f"[warn] could not focus roblox: {e}")


#Test Gamble
def test_gamble_loop(max_seconds: int = 60):
        """
        Isolated test for the 'gamble' loop logic.
        Runs for max_seconds then exits.
        """
        print("[TEST] Starting gamble loop test...")
        start = time.time()

        # Optional: force you into the right place first
        # quick_rts()
        # directions('3')
        # time.sleep(2)

        gamble_done = False
        loops = 0

        while not gamble_done:
            loops += 1

            # stop conditions
            if not g_toggle:
                print("[TEST] g_toggle is False -> stopping test")
                break
            if time.time() - start > max_seconds:
                print("[TEST] max_seconds reached -> stopping test")
                break

            # your E spam
            for _ in range(5):
                tap('e')
                time.sleep(0.05)  # tiny delay helps reliability

            # detection (add prints so you can see what's happening)
            full_bar = bt.does_exist("Winter/Full_Bar.png", confidence=0.7, grayscale=False)
            no_yen = bt.does_exist("Winter/NO_YEN.png", confidence=0.7, grayscale=False)

            print(f"[TEST] loop={loops} full_bar={full_bar} no_yen={no_yen}")

            if full_bar or no_yen:
                print("[TEST] Trigger hit -> quick_rts + place_hotbar_units + directions('3')")
                quick_rts()
                time.sleep(3)
                place_hotbar_units()
                directions('3')

            time.sleep(0.2)

        print("[TEST] Gamble loop test finished.")






#Enter into terminal: python3 Winter_Event.py --test-gamble
if "--test-gamble" in sys.argv:
    g_toggle = True  # so it actually runs
    test_gamble_loop(max_seconds=120)
    sys.exit(0)



# Auto-start logic stays the same
if Settings.AUTO_START:
    if "--stopped" not in sys.argv:
        g_toggle = True
    else:
        print("Program was STOPPED, won't auto start")

for z in range(3):
    print(f"Starting in {3 - z}")
    time.sleep(1)

# ✅ Focus Roblox once before any clicks/keys
focus_roblox()

if g_toggle:
    if avM.get_wave() >= 1:
        avM.restart_match()

    tap('w'); tap('a'); tap('s'); tap('d')
    main()
else:
    while not g_toggle:
        time.sleep(1)

    # ✅ Focus again when user manually starts (optional but helpful)
    focus_roblox()

    if avM.get_wave() >= 1:
        avM.restart_match()

    release('w'); release('a'); release('s'); release('d')
    main()