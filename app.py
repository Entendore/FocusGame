# focus_rogue.py
# ──────────────────────────────────────────────────────────────────────────────
# 1. IMPORTS & CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────
import pygame
import pygame.freetype
import random
import time
import sys
import os
import math
import copy
import threading
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Optional, Dict

try:
    import pygetwindow as gw
    HAS_GW = True
except Exception:
    HAS_GW = False

try:
    import psutil
    HAS_PSUTIL = True
except Exception:
    HAS_PSUTIL = False

WIDTH, HEIGHT = 1024, 720
TILE = 32
GRID_W, GRID_H = 21, 16
GAME_W = GRID_W * TILE      # 672
GAME_H = GRID_H * TILE      # 512
SIDEBAR_X = GAME_W
SIDEBAR_W = WIDTH - GAME_W  # 352
FPS = 60

# Display Colors
COL_BG       = (12, 14, 22)
COL_FLOOR    = (40, 44, 60)
COL_FLOOR2   = (34, 38, 52)
COL_WALL     = (70, 76, 100)
COL_WALL_TOP = (110, 118, 146)
COL_PLAYER   = (90, 200, 255)
COL_MONSTER  = (220, 70, 70)
COL_LOOT     = (255, 210, 90)
COL_STAIRS   = (180, 140, 220)
COL_TEXT     = (220, 225, 240)
COL_DIM      = (130, 138, 160)
COL_GOOD     = (90, 220, 140)
COL_BAD      = (220, 80, 80)
COL_PANEL    = (22, 26, 38)
COL_EDGE     = (60, 66, 90)


# ──────────────────────────────────────────────────────────────────────────────
# 2. DATA SECTION (Items, Monsters, NPCs, Behaviors)
# ──────────────────────────────────────────────────────────────────────────────
PLAYER_BEHAVIORS = ["Balanced", "Aggressive", "Looter", "Speedrunner", "Survivalist", "Pacifist"]

HERO_EMOJIS = [
    "🧝", "🧙", "🧚", "🧛", "🧜", "🧞", "🧟", "🦸", "🦹", "🥷", "🤴", "👸", "👑", "🤠", 
    "🕵️", "👮", "👷", "🦰", "🦱", "🦳", "🦲", "🧔", "🧑", "👨", "👩", "👴", "👵", 
    "👼", "🤵", "👰", "🤰", "🤱"
]

# Format: ("Name", "Emoji", Color(R,G,B), HP, ATK, DEF)
MONSTER_KINDS = [
    ("Goblin","👺",(120,180,80),8,3,0), ("Skeleton","💀",(210,210,210),10,4,1),
    ("Slime","🟢",(120,200,200),6,2,0), ("Bat","🦇",(160,120,200),5,3,0),
    ("Orc","👹",(180,120,80),14,5,1), ("Wraith","👻",(150,110,190),12,6,2),
    ("Giant Spider","🕷️",(80,80,80),9,4,0), ("Viper","🐍",(60,120,60),7,5,0),
    ("Scorpion","🦂",(150,100,40),11,5,1), ("Imp","😈",(200,50,50),8,4,0),
    ("Stone Golem","🗿",(100,100,110),20,3,4), ("Dire Wolf","🐺",(100,110,120),12,6,0),
    ("Kobold","🦎",(50,150,50),6,2,0), ("Giant Rat","🐀",(60,60,60),4,2,0),
    ("Microbe","🦠",(100,200,100),3,1,0), ("T-Rex","🦖",(80,120,40),25,8,2),
    ("Sauropod","🦕",(90,150,60),20,6,3), ("Crocodile","🐊",(60,100,40),14,6,2),
    ("Shark","🦈",(80,120,150),16,7,1), ("Giant Octopus","🐙",(150,80,100),18,5,2),
    ("Crab","🦀",(200,80,80),12,3,3), ("Giant Fly","🪰",(60,60,60),5,3,0),
    ("Centipede","🪱",(100,80,80),8,4,0), ("Dragon","🐉",(200,50,0),30,10,5),
    ("Fel Beast","🐈‍⬛",(20,20,20),15,7,1), ("Hydra","🐲",(50,100,150),22,7,3),
    ("Mammoth","🦣",(150,100,50),24,5,4), ("Bison","🐃",(100,80,60),18,4,3),
    ("Ram","🐏",(180,180,180),14,5,2), ("Boar","🐗",(60,60,40),12,5,1),
    ("Panda","🐼",(240,240,240),16,3,2), ("Skunk","🦨",(20,20,20),8,2,0),
    ("Walrus","🦭",(100,80,60),20,4,3), ("Seal","🦭",(120,100,80),12,3,1),
    ("Tiger","🐅",(200,100,0),18,8,1), ("Leopard","🐆",(200,180,0),16,7,1),
    ("Zebra","🦓",(240,240,240),14,6,1), ("Boar","🐗",(80,60,40),14,5,2),
    ("Hippo","🦛",(120,80,80),22,4,4), ("Kangaroo","🦘",(200,150,100),15,6,1),
    ("Lizard","🦖",(50,150,50),14,5,1), ("Eagle","🦅",(200,150,0),10,7,0),
    ("Owl","🦉",(150,100,50),8,5,0), ("Dodo","🦤",(200,150,100),6,2,1)
]

# Format: ("Name", "Emoji", Color(R,G,B), HP, ATK, DEF)
NPC_KINDS = [
    ("Merchant","🛒",(90,220,140),30,5,2), ("Sage","🔮",(210,190,120),20,2,0),
    ("Wandering Knight","🤺",(190,190,230),45,8,4), ("Bard","🎸",(180,100,220),15,3,1),
    ("Priest","🙏",(230,230,200),25,1,3), ("Town Guard","💂",(100,150,200),40,6,3),
    ("Fairy","🧚",(230,200,255),10,2,0), ("Merman","🧜",(100,200,230),20,4,2),
    ("Troll","🧌",(100,130,100),50,3,5), ("Scientist","🧑‍🔬",(200,200,200),15,2,1),
    ("Doctor","👨‍⚕️",(255,255,255),20,1,3), ("Farmer","👨‍🌾",(200,180,100),25,2,1),
    ("Chef","👨‍🍳",(220,220,220),30,3,1), ("Student","👨‍🎓",(180,180,240),12,2,0),
    ("Singer","👨‍🎤",(255,100,200),18,3,0), ("Teacher","👨‍🏫",(200,200,150),22,2,2),
    ("Mechanic","👨‍🔧",(150,150,150),35,4,2), ("Programmer","👨‍💻",(100,200,100),15,5,0),
    ("Office Worker","👨‍💼",(100,150,200),25,2,2), ("Pilot","👨‍✈️",(180,180,200),30,5,2),
    ("Astronaut","👨‍🚀",(240,240,240),40,6,3)
]

# Format: ("Name", "Emoji", ATK)
WEAPONS  = [
    ("Rusty Dagger","🗡️",3), ("Steel Sword","⚔️",6), ("Iron Axe","🪓",9),
    ("Mythril Blade","🔪",13), ("Voidreaver","🗡️",18), ("Hunter's Bow","🏹",7),
    ("War Hammer","🔨",10), ("Trident","🔱",11), ("Magic Staff","🪄",8),
    ("Pistol","🔫",5), ("Bomb","💣",12), ("Boomerang","🪃",6), ("Saw","🪚",8),
    ("Firecracker","🧨",7), ("Wrench","🔧",4), ("Pickaxe","⛏️",6), ("Nut","🔩",2),
    ("Gear","⚙️",3), ("Brick","🧱",4), ("Anchor","⚓",14), ("Hook","🪝",7),
    ("Tire","🛞",5), ("Ladder","🪜",2), ("Magnet","🧲",1), ("Bat","🏏",5),
    ("Hockey Stick","🏒",4), ("Lacrosse Stick","🥍",4), ("Pool Cue","🎱",3),
    ("Yo-yo","🪀",2), ("Bowling Ball","🎳",8), ("Dart","🎯",4), ("Skewer","🍢",2)
]

# Format: ("Name", "Emoji", DEF)
ARMORS   = [
    ("Leather Vest","🦺",2), ("Chainmail","⛓️",4), ("Iron Plate","🛡️",6),
    ("Dragonscale","🐲",9), ("Aegis Plate","🛡️",12), ("Bone Armor","🦴",5),
    ("Copper Mail","⚙️",3), ("Military Helmet","🪖",2), ("Goggles","🥽",1),
    ("Rescue Helmet","⛑️",3), ("Space Suit","🪐",15), ("Heavy Duty Tire","🛞",8),
    ("Cement Block","🧱",10), ("Steel Beam","🪜",7), ("Metal Door","🚪",12),
    ("Trash Can","🗑️",4), ("Shopping Cart","🛒",3), ("Boulder","🗿",14),
    ("Stop Sign","🛑",6), ("Traffic Light","🚦",5), ("Barrier","🚧",8), ("Pylon","🚧",4)
]

# Format: ("Name", "Emoji", DEF, INT)
CLOTHES  = [
    ("Wanderer's Cloak","🧥",1,1), ("Silk Robe","👘",0,2), ("Shadow Garb","🥷",2,2),
    ("Mantle of Stars","✨",3,3), ("Royal Crown","👑",0,5), ("Wanderer's Boots","🥾",1,0),
    ("Leather Gloves","🧤",1,1), ("Slick Shades","🕶️",0,3), ("Martial Gi","🥋",2,2),
    ("Top Hat","🎩",0,3), ("Graduation Cap","🎓",0,4), ("Billed Cap","🧢",1,1),
    ("High Heels","👠",0,2), ("Socks","🧦",1,0), ("Scarf","🧣",1,2), ("Dress","👗",0,3),
    ("Tuxedo","🤵",1,4), ("Wedding Veil","👰",0,4), ("Pregnant Belly","🤰",2,0),
    ("Bikini","👙",0,1), ("Swimsuit","🩱",0,1), ("Briefs","🩲",0,0), ("Trunks","🩳",0,0),
    ("Flat Shoes","🥿",0,1), ("Ballet Slippers","🩰",1,2), ("Sneakers","👟",1,1),
    ("Loafers","👞",0,1), ("Boots","👢",2,1), ("Sandals","🩴",0,0), ("Backpack","🎒",1,3)
]

# Format: ("Name", "Emoji", INT)
BOOKS    = [
    ("Tome of Sparks","📖",3), ("Grimoire","📕",5), ("Atlas of Realms","🗺️",2),
    ("Codex of Echoes","📘",7), ("Ancient Scroll","📜",4), ("Old Newspaper","📰",1),
    ("Travel Journal","📓",2), ("Ledger","📒",1), ("Green Book","📗",3),
    ("Orange Book","📙",2), ("Stack of Books","📚",8), ("Bookmark","🔖",1),
    ("Notebook","📔",2), ("Page","📃",1), ("Document","📄",2), ("Calendar","📅",3),
    ("Tear-off Calendar","📆",4), ("Rolodex","📇",2), ("Clipboard","📋",3), ("Folder","📁",2),
    ("Open File","📂",3), ("Note","🗒️",1), ("Reminder","🗓️",2), ("Card Index","🗃️",4),
    ("File Cabinet","🗄️",5), ("Wastebasket","🗑️",1), ("Package","📦",2), ("Mailbox","📫",3),
    ("Postbox","📮",4), ("Label","🏷️",1), ("Pencil","📝",2)
]

# Format: ("Name", "Emoji", ATK, DEF)
ACCESS   = [
    ("Iron Ring","💍",1,0), ("Amulet of Vigor","📿",0,3), ("Lucky Charm","🍀",1,1),
    ("Eye of Insight","👁️",0,4), ("Sapphire Gem","💎",0,5), ("Skeleton Key","🗝️",1,2),
    ("Magic Crystal","🔮",0,6), ("Smartwatch","⌚",1,2), ("Nazar Amulet","🧿",0,5),
    ("Red Lantern","🏮",1,1), ("Floppy Disk","💾",0,3), ("Compass","🧭",1,3),
    ("Key","🔑",1,1), ("Bow","🎀",0,2), ("Ticket","🎫",0,1), ("ID Card","🪪",0,2),
    ("Name Tag","📛",0,1), ("Credit Card","💳",0,2), ("Red Envelope","🧧",0,3),
    ("Love Letter","💌",0,2), ("Envelope","✉️",0,1), ("Email","📧",0,2),
    ("Inbox","📥",0,3), ("Outbox","📤",0,3), ("Stamp","📮",0,1), ("Barcode","🏷️",0,1),
    ("Money Bag","💰",1,4), ("Dollar Bill","💵",0,2), ("Yen","💴",0,2), ("Euro","💶",0,2)
]

# Format: ("Name", "Emoji", HEAL)
POTIONS  = [
    ("Health Potion","🧪",15), ("Greater Potion","🍹",35), ("Elixir","⚗️",60),
    ("Holy Water","🍷",25), ("Milk","🥛",10), ("Herbal Tea","🍵",20),
    ("Coffee","☕",12), ("Bubble Tea","🧋",18), ("Cocktail","🍸",25),
    ("Champagne","🍾",45), ("Energy Drink","🥤",20), ("Ice Water","🧊",5),
    ("Whiskey","🥃",30), ("Beer","🍺",15), ("Cider","🍻",15), ("Wine Glass","🥂",22),
    ("Sake","🍶",18), ("Spoiled Milk","🥛",5), ("Hot Sauce","🌶️",8), ("Chocolate","🍫",10),
    ("Candy","🍬",5), ("Lollipop","🍭",7), ("Custard","🍮",12), ("Honey","🍯",15),
    ("Baby Bottle","🍼",8), ("Green Potion","🧪",18), ("Blue Potion","🧪",22)
]


# ──────────────────────────────────────────────────────────────────────────────
# 3. ITEMS & EQUIPMENT LOGIC
# ──────────────────────────────────────────────────────────────────────────────
class IT(Enum):
    WEAPON="Weapon"; ARMOR="Armor"; CLOTHING="Clothing"
    BOOK="Book"; ACCESSORY="Accessory"; POTION="Potion"

@dataclass
class Item:
    name: str; type: IT; emoji: str
    atk: int = 0; defn: int = 0; intl: int = 0; heal: int = 0
    color: Tuple[int,int,int] = (255,255,255)

def make_item(level):
    r = random.random()
    tier = min(level // 3, 4)
    if r < 0.25:
        n,e,a = random.choice(WEAPONS)
        return Item(n,IT.WEAPON,e,atk=a,color=(210,210,230))
    if r < 0.45:
        n,e,d = random.choice(ARMORS)
        return Item(n,IT.ARMOR,e,defn=d,color=(180,180,210))
    if r < 0.60:
        n,e,d,i = random.choice(CLOTHES)
        return Item(n,IT.CLOTHING,e,defn=d,intl=i,color=(190,150,210))
    if r < 0.75:
        n,e,i = random.choice(BOOKS)
        return Item(n,IT.BOOK,e,intl=i,color=(230,210,130))
    if r < 0.90:
        n,e,a,d = random.choice(ACCESS)
        return Item(n,IT.ACCESSORY,e,atk=a,defn=d,color=(255,215,100))
    n,e,h = random.choice(POTIONS)
    return Item(n,IT.POTION,e,heal=h,color=(230,90,90))


# ──────────────────────────────────────────────────────────────────────────────
# 4. ENTITIES & UNIVERSAL LOGIC
# ──────────────────────────────────────────────────────────────────────────────
class Entity:
    def __init__(self,x,y,name,glyph,color,hp,atk,defn,kind="monster"):
        self.x=x; self.y=y; self.name=name; self.glyph=glyph; self.color=color
        self.hp=hp; self.max_hp=hp; self.atk=atk; self.defn=defn; self.kind=kind
        self.alive=True; self.xp=0; self.level=1; self.gold=0
        self.inventory: List[Item] = []
        self.equipped: Dict[IT, Item] = {}
        self.dialogue = ""
        self.behavior = "Aggressive"
        self.spawn_x, self.spawn_y = x, y
        self.enraged_logged = False
    def total_atk(self): return self.atk + sum(i.atk for i in self.equipped.values())
    def total_def(self): return self.defn + sum(i.defn for i in self.equipped.values())
    def total_int(self): return sum(i.intl for i in self.equipped.values())

def try_pickup(entity: Entity, items_list: List[Tuple[Tuple[int,int], Item]]):
    for i, (pos, it) in enumerate(items_list):
        if pos[0] == entity.x and pos[1] == entity.y:
            items_list.pop(i)
            entity.inventory.append(it)
            if it.type != IT.POTION:
                cur = entity.equipped.get(it.type)
                cur_s = (cur.atk*2+cur.defn*2+cur.intl) if cur else -1
                new_s = it.atk*2+it.defn*2+it.intl
                if new_s > cur_s:
                    if cur: entity.inventory.append(cur)
                    entity.equipped[it.type] = it
                    entity.inventory.remove(it)
                    return f"equipped {it.name}"
                return f"picked up {it.name}"
            return f"picked up {it.name}"
    return None

def try_heal(entity: Entity):
    if entity.hp < entity.max_hp * 0.5:
        for i, it in enumerate(entity.inventory):
            if it.type == IT.POTION:
                entity.hp = min(entity.max_hp, entity.hp + it.heal)
                entity.inventory.pop(i)
                return it.name
    return None

def drop_loot(entity: Entity, items_list: List[Tuple[Tuple[int,int], Item]]):
    dropped = entity.inventory + list(entity.equipped.values())
    for it in dropped:
        items_list.append(((entity.x, entity.y), it))
    entity.inventory.clear()
    entity.equipped.clear()
    return len(dropped)

def bfs_step(grid, start, goal):
    if start == goal: return None
    q = deque([start]); prev = {start: None}
    while q:
        c = q.popleft()
        if c == goal: break
        for dx,dy in ((0,1),(0,-1),(1,0),(-1,0)):
            nx,ny = c[0]+dx, c[1]+dy
            if 0<=nx<GRID_W and 0<=ny<GRID_H and grid[ny][nx]!=T.WALL and (nx,ny) not in prev:
                prev[(nx,ny)] = c; q.append((nx,ny))
    if goal not in prev: return None
    path = []; c = goal
    while c != start: path.append(c); c = prev[c]
    return path[-1] if path else None

def get_flee_step(grid, start, threat):
    best_dist = abs(start[0]-threat[0]) + abs(start[1]-threat[1])
    best_step = None
    for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
        nx, ny = start[0]+dx, start[1]+dy
        if 0<=nx<GRID_W and 0<=ny<GRID_H and grid[ny][nx]!=T.WALL:
            d = abs(nx-threat[0]) + abs(ny-threat[1])
            if d > best_dist:
                best_dist = d
                best_step = (nx, ny)
    return best_step

def find_nearest_item(grid, start, items_list):
    if not items_list: return None
    nearest_pos = None; min_d = 999
    for (ix, iy), it in items_list:
        d = abs(ix-start[0]) + abs(iy-start[1])
        if d < min_d:
            min_d = d
            nearest_pos = (ix, iy)
    return nearest_pos


# ──────────────────────────────────────────────────────────────────────────────
# 5. DUNGEON GENERATION
# ──────────────────────────────────────────────────────────────────────────────
class T:
    WALL, FLOOR, STAIRS = 0, 1, 2

@dataclass
class Room:
    x: int; y: int; w: int; h: int
    def center(self): return self.x + self.w//2, self.y + self.h//2
    def intersects(self, o):
        return (self.x <= o.x+o.w and self.x+self.w >= o.x and
                self.y <= o.y+o.h and self.y+self.h >= o.y)

def generate_dungeon(level):
    grid = [[T.WALL]*GRID_W for _ in range(GRID_H)]
    rooms = []
    for _ in range(120):
        if len(rooms) >= random.randint(6, 10): break
        w = random.randint(4, 8); h = random.randint(4, 6)
        x = random.randint(1, GRID_W-w-1); y = random.randint(1, GRID_H-h-1)
        nr = Room(x, y, w, h)
        if any(nr.intersects(r) for r in rooms): continue
        for ry in range(y, y+h):
            for rx in range(x, x+w): grid[ry][rx] = T.FLOOR
        if rooms:
            px, py = rooms[-1].center(); cx, cy = nr.center()
            if random.random() < 0.5:
                for gx in range(min(cx,px), max(cx,px)+1): grid[py][gx] = T.FLOOR
                for gy in range(min(cy,py), max(cy,py)+1): grid[gy][cx] = T.FLOOR
            else:
                for gy in range(min(cy,py), max(cy,py)+1): grid[gy][px] = T.FLOOR
                for gx in range(min(cx,px), max(cx,px)+1): grid[cy][gx] = T.FLOOR
        rooms.append(nr)
    sx, sy = rooms[-1].center(); grid[sy][sx] = T.STAIRS
    px, py = rooms[0].center()

    monsters = []
    for r in rooms[1:-1]:
        for _ in range(random.randint(1, 3)):
            mx = random.randint(r.x+1, r.x+r.w-1)
            my = random.randint(r.y+1, r.y+r.h-1)
            k = random.choice(MONSTER_KINDS)
            s = 1 + level * 0.35
            m = Entity(mx,my,k[0],k[1],k[2],int(k[3]*s),int(k[4]*s),k[5],"monster")
            m.xp = int(k[3]*s)//2 + int(k[4]*s)
            m.gold = random.randint(2, 10)
            m.spawn_x, m.spawn_y = mx, my
            m.behavior = random.choice(["Aggressive", "Wanderer", "Territorial", "Cowardly", "Berserker", "Hoarder"])
            monsters.append(m)

    items = []
    for r in rooms[1:]:
        for _ in range(random.randint(0, 2)):
            ix = random.randint(r.x+1, r.x+r.w-1)
            iy = random.randint(r.y+1, r.y+r.h-1)
            items.append(((ix,iy), make_item(level)))

    npcs = []
    if random.random() < 0.65:
        r = random.choice(rooms[1:-1])
        nx = random.randint(r.x+1, r.x+r.w-1)
        ny = random.randint(r.y+1, r.y+r.h-1)
        k = random.choice(NPC_KINDS)
        n = Entity(nx,ny,k[0],k[1],k[2],k[3],k[4],k[5],"npc")
        n.dialogue = random.choice([
            "Greetings, traveler.",
            "The depths hold many treasures...",
            "Beware the lower levels.",
            "I have wares, if you have coin.",
            "Strange forces stir below.",
            "May your blade stay sharp.",
        ])
        n.spawn_x, n.spawn_y = nx, ny
        n.behavior = random.choice(["Patrol", "Wander", "Flee", "Looter", "Guard"])
        npcs.append(n)
    return grid, rooms, (px,py), monsters, items, npcs, (sx,sy)


# ──────────────────────────────────────────────────────────────────────────────
# 6. FOCUS MONITORING
# ──────────────────────────────────────────────────────────────────────────────
class FocusMonitor:
    def __init__(self):
        self.sites = ["youtube", "reddit", "twitter", "x.com", "tiktok",
                      "instagram", "facebook", "netflix", "twitch",
                      "9gag", "pinterest", "linkedin"]
        self.apps  = ["discord.exe", "steam.exe", "epicgames", "spotify.exe",
                      "netflix", "hulu", "disney"]
        self.locked = False
        self.reason = ""
        self._lock = threading.Lock()
        if HAS_GW or HAS_PSUTIL:
            threading.Thread(target=self._loop, daemon=True).start()

    def add_site(self, name):
        with self._lock:
            if name.lower() not in self.sites:
                self.sites.append(name.lower())

    def add_app(self, name):
        with self._lock:
            if name.lower() not in self.apps:
                self.apps.append(name.lower())

    def _loop(self):
        while True:
            self._check()
            time.sleep(1.0)

    def _check(self):
        with self._lock:
            sites = list(self.sites); apps = list(self.apps)
        title = ""
        if HAS_GW:
            try:
                w = gw.getActiveWindow()
                if w: title = w.title
            except Exception:
                pass
        t = title.lower()
        found = next((s for s in sites if s in t), None)
        if not found and HAS_PSUTIL:
            try:
                for p in psutil.process_iter(['name']):
                    pn = (p.info.get('name') or '').lower()
                    hit = next((a for a in apps if a in pn), None)
                    if hit: found = hit; break
            except Exception:
                pass
        with self._lock:
            self.locked = bool(found)
            self.reason = found or ""

    def status(self):
        with self._lock:
            return self.locked, self.reason


# ──────────────────────────────────────────────────────────────────────────────
# 7. MCTS & AI SIMULATION
# ──────────────────────────────────────────────────────────────────────────────
@dataclass
class GameState:
    player: Entity
    monsters: List[Entity]
    items: List[Tuple[Tuple[int,int], Item]]
    npcs: List[Entity]
    stairs: Optional[Tuple[int,int]]
    grid: List[List[int]]
    level: int
    descended: bool = False

class MCTSNode:
    def __init__(self, parent=None, action=None):
        self.parent = parent
        self.action = action
        self.children = []
        self.untried_actions = []
        self.visits = 0
        self.value = 0.0

    def is_fully_expanded(self):
        return len(self.untried_actions) == 0

    def best_child(self, c_param=1.414):
        choices = []
        for child in self.children:
            ucb = (child.value / child.visits) + c_param * math.sqrt((2 * math.log(self.visits)) / child.visits)
            choices.append((ucb, child))
        return max(choices, key=lambda x: x[0])[1]

def get_valid_actions(state: GameState):
    actions = []
    p = state.player
    if not p.alive: return actions

    for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
        nx, ny = p.x+dx, p.y+dy
        if 0<=nx<GRID_W and 0<=ny<GRID_H and state.grid[ny][nx]!=T.WALL:
            if not any(m.alive and m.x==nx and m.y==ny for m in state.monsters) and \
               not any(n.x==nx and n.y==ny for n in state.npcs):
                actions.append(("move", dx, dy))

    for m in state.monsters:
        if m.alive and abs(m.x-p.x)+abs(m.y-p.y)==1:
            actions.append(("attack", m.x, m.y))

    for pos, it in state.items:
        if pos[0]==p.x and pos[1]==p.y:
            actions.append(("pickup",))
            break

    for it in p.inventory:
        if it.type == IT.POTION and p.hp < p.max_hp:
            actions.append(("use",))
            break

    for n in state.npcs:
        if abs(n.x-p.x)+abs(n.y-p.y)==1 and "Merchant" in n.name:
            if p.gold >= 10:
                actions.append(("talk", n.x, n.y))

    if state.stairs and (p.x, p.y) == state.stairs:
        actions.append(("descend",))

    if not actions:
        actions.append(("wait",))
    return actions

def apply_action_sim(state: GameState, action):
    p = state.player
    k = action[0]
    
    if k == "move":
        p.x += action[1]; p.y += action[2]
    elif k == "attack":
        mx, my = action[1], action[2]
        for m in state.monsters:
            if m.alive and m.x == mx and m.y == my:
                dmg = max(1, p.total_atk() - m.total_def())
                m.hp -= dmg
                if m.hp <= 0:
                    m.alive = False
                    drop_loot(m, state.items)
                    p.xp += m.xp
                    p.gold += m.gold
                    need = p.level * 20
                    if p.xp >= need:
                        p.xp -= need
                        p.level += 1
                        p.max_hp += 8
                        p.hp = p.max_hp
                        p.atk += 1
                break
    elif k == "pickup":
        try_pickup(p, state.items)
    elif k == "use":
        if p.hp < p.max_hp:
            for i, it in enumerate(p.inventory):
                if it.type == IT.POTION:
                    p.hp = min(p.max_hp, p.hp + it.heal)
                    p.inventory.pop(i)
                    break
    elif k == "talk":
        for n in state.npcs:
            if n.x == action[1] and n.y == action[2] and "Merchant" in n.name:
                if p.gold >= 10:
                    p.gold -= 10
                    ni = make_item(state.level)
                    p.inventory.append(ni)
                    if ni.type != IT.POTION:
                        cur = p.equipped.get(ni.type)
                        cur_s = (cur.atk*2+cur.defn*2+cur.intl) if cur else -1
                        new_s = ni.atk*2+ni.defn*2+ni.intl
                        if new_s > cur_s:
                            if cur: p.inventory.append(cur)
                            p.equipped[ni.type] = ni
                            p.inventory.remove(ni)
                break
    elif k == "descend":
        state.descended = True

def simulate_npcs_sim(state: GameState):
    for n in state.npcs:
        try_heal(n)
        try_pickup(n, state.items)
        if n.behavior == "Guard":
            for m in state.monsters:
                if m.alive and abs(n.x-m.x)+abs(n.y-m.y)==1:
                    dmg = max(1, n.total_atk() - m.total_def())
                    m.hp -= dmg
                    if m.hp <= 0:
                        m.alive = False
                        drop_loot(m, state.items)
        elif n.behavior in ["Flee", "Looter"]:
            nearest_m = None; nd = 999
            for m in state.monsters:
                if not m.alive: continue
                d = abs(m.x-n.x) + abs(m.y-n.y)
                if d < nd: nd = d; nearest_m = m
            if nearest_m and nd <= 4:
                step = get_flee_step(state.grid, (n.x,n.y), (nearest_m.x, nearest_m.y))
                if step: n.x, n.y = step
            elif n.behavior == "Looter":
                target = find_nearest_item(state.grid, (n.x,n.y), state.items)
                if target and target != (n.x,n.y):
                    for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                        nx, ny = n.x+dx, n.y+dy
                        if 0<=nx<GRID_W and 0<=ny<GRID_H and state.grid[ny][nx]!=T.WALL:
                            if abs(nx-target[0])+abs(ny-target[1]) < abs(n.x-target[0])+abs(n.y-target[1]):
                                n.x, n.y = nx, ny; break

def simulate_monsters_sim(state: GameState):
    p = state.player
    if not p.alive: return
    for m in state.monsters:
        if not m.alive: continue
        try_heal(m)
        try_pickup(m, state.items)
        d = abs(m.x - p.x) + abs(m.y - p.y)
        
        atk_buff = 5 if (m.behavior == "Berserker" and m.hp < m.max_hp * 0.4) else 0
        
        if m.behavior == "Cowardly" and m.hp < m.max_hp * 0.5:
            if d <= 5:
                step = get_flee_step(state.grid, (m.x, m.y), (p.x, p.y))
                if step: m.x, m.y = step
            continue
        elif m.behavior == "Wanderer" and d > 3:
            if random.random() < 0.5: continue
        elif m.behavior == "Territorial" and d > 4: continue
        elif m.behavior == "Hoarder":
            if d <= 3:
                step = get_flee_step(state.grid, (m.x, m.y), (p.x, p.y))
                if step: m.x, m.y = step
            else:
                target = find_nearest_item(state.grid, (m.x,m.y), state.items)
                if target and target != (m.x,m.y):
                    for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                        nx, ny = m.x+dx, m.y+dy
                        if 0<=nx<GRID_W and 0<=ny<GRID_H and state.grid[ny][nx]!=T.WALL:
                            if abs(nx-target[0])+abs(ny-target[1]) < abs(m.x-target[0])+abs(m.y-target[1]):
                                m.x, m.y = nx, ny; break
            continue
            
        if d == 1:
            dmg = max(1, (m.total_atk() + atk_buff) - p.total_def())
            p.hp -= dmg
            if p.hp <= 0:
                p.alive = False; p.hp = 0; return
        elif d <= 6:
            best_move = None; best_dist = d
            for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                nx, ny = m.x+dx, m.y+dy
                if 0<=nx<GRID_W and 0<=ny<GRID_H and state.grid[ny][nx]!=T.WALL:
                    if any(o is not m and o.alive and o.x==nx and o.y==ny for o in state.monsters): continue
                    if any(o.x==nx and o.y==ny for o in state.npcs): continue
                    if nx == p.x and ny == p.y: continue
                    nd = abs(nx-p.x) + abs(ny-p.y)
                    if nd < best_dist:
                        best_dist = nd; best_move = (nx, ny)
            if best_move: m.x, m.y = best_move

def evaluate_state(state: GameState):
    if not state.player.alive: return -10000.0
    if state.descended: return 10000.0
    p = state.player
    score = p.hp + (p.gold * 0.5) + (p.xp * 2.0) + (len(p.equipped) * 5.0)
    
    if p.behavior == "Aggressive": score += (p.xp * 4.0)
    elif p.behavior == "Looter": score += (len(p.inventory) * 3.0) + (p.gold * 1.0)
    elif p.behavior == "Speedrunner" and state.stairs:
        dist = abs(p.x - state.stairs[0]) + abs(p.y - state.stairs[1])
        score -= (dist * 5.0)
    elif p.behavior == "Survivalist":
        score += (p.hp * 2.0)
        min_dist = min([abs(m.x-p.x)+abs(m.y-p.y) for m in state.monsters if m.alive] + [99])
        if min_dist <= 2: score -= 50.0
    elif p.behavior == "Pacifist":
        score += (p.hp * 1.0)
        if state.stairs:
            dist = abs(p.x - state.stairs[0]) + abs(p.y - state.stairs[1])
            score -= (dist * 8.0)
        min_dist = min([abs(m.x-p.x)+abs(m.y-p.y) for m in state.monsters if m.alive] + [99])
        if min_dist <= 4: score -= 100.0
    return score

def rollout(state: GameState, max_depth=6):
    temp_state = copy.deepcopy(state)
    for _ in range(max_depth):
        if not temp_state.player.alive or temp_state.descended: break
        actions = get_valid_actions(temp_state)
        if not actions: break
        action = random.choice(actions)
        apply_action_sim(temp_state, action)
        simulate_npcs_sim(temp_state)
        simulate_monsters_sim(temp_state)
    return evaluate_state(temp_state)

def mcts_search(root_state: GameState, iterations=30):
    root = MCTSNode()
    root.untried_actions = get_valid_actions(root_state)
    if not root.untried_actions: return ("wait",)

    for _ in range(iterations):
        node = root
        sim_state = copy.deepcopy(root_state)

        while node.is_fully_expanded() and node.children:
            node = node.best_child()
            apply_action_sim(sim_state, node.action)
            simulate_npcs_sim(sim_state)
            simulate_monsters_sim(sim_state)

        if node.untried_actions:
            action = node.untried_actions.pop()
            apply_action_sim(sim_state, action)
            simulate_npcs_sim(sim_state)
            simulate_monsters_sim(sim_state)
            child = MCTSNode(parent=node, action=action)
            child.untried_actions = get_valid_actions(sim_state)
            node.children.append(child)
            node = child

        reward = rollout(sim_state)

        while node is not None:
            node.visits += 1
            node.value += reward
            node = node.parent

    if not root.children: return ("wait",)
    best = max(root.children, key=lambda c: c.visits)
    return best.action


# ──────────────────────────────────────────────────────────────────────────────
# 8. GAME ENGINE (INIT, LOOP, UPDATE, RENDER)
# ──────────────────────────────────────────────────────────────────────────────
class Game:
    def __init__(self):
        pygame.init()
        pygame.freetype.init()
        self.screen = pygame.display.set_mode((WIDTH,HEIGHT))
        pygame.display.set_caption("Focus Rogue — Emergent Ecosystem Edition")
        self.clock = pygame.time.Clock()

        self.font      = pygame.font.SysFont("consolas,couriernew,monospace", 16, bold=True)
        self.font_sm   = pygame.font.SysFont("consolas,couriernew,monospace", 14)
        self.font_tiny = pygame.font.SysFont("consolas,couriernew,monospace", 12)
        self.font_big  = pygame.font.SysFont("consolas,couriernew,monospace", 26, bold=True)

        self.emoji_font = self._load_emoji_font(TILE - 4)
        self.emoji_cache = {}

        self.focus = FocusMonitor()
        if not (HAS_GW or HAS_PSUTIL):
            print("Warning: pygetwindow/psutil not found — install them for auto-pause.")
            
        self._generate_tile_surfaces()
        self.reset_game()
        self.event_log: List[str] = []
        self.ui_mode = "game"      
        self.input_text = ""
        self.show_list = False
        self.show_inv = False
        self.paused_alpha = 0
        self.focus_time = 0.0
        self.dist_time = 0.0
        self.fast = False
        self.tick_accum = 0.0
        self.running = True
        self.use_mcts = True

    # ── Engine Setup Helpers ──
    def _load_emoji_font(self, size):
        paths_to_check = [
            "emoji.ttf", 
            "C:/Windows/Fonts/seguiemj.ttf", 
            "/System/Library/Fonts/Apple Color Emoji.ttc", 
            "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 
            "/usr/share/fonts/noto-color-emoji/NotoColorEmoji.ttf"
        ]
        for p in paths_to_check:
            if os.path.exists(p):
                try:
                    return pygame.freetype.Font(p, size)
                except Exception: pass
        return pygame.freetype.SysFont("Arial", size)

    def _generate_tile_surfaces(self):
        self.tile_surfaces = {}
        floor_surf = pygame.Surface((TILE, TILE))
        floor_surf.fill(COL_FLOOR)
        for _ in range(8):
            rx = random.randint(0, TILE-3); ry = random.randint(0, TILE-3)
            col = COL_FLOOR2 if random.random() > 0.5 else (50, 54, 70)
            pygame.draw.rect(floor_surf, col, (rx, ry, 3, 3))
        self.tile_surfaces[T.FLOOR] = floor_surf.convert()

        wall_surf = pygame.Surface((TILE, TILE))
        wall_surf.fill(COL_WALL)
        pygame.draw.rect(wall_surf, COL_WALL_TOP, (0, 0, TILE, 6))
        pygame.draw.line(wall_surf, (50, 56, 80), (0, TILE//2), (TILE, TILE//2), 1)
        pygame.draw.line(wall_surf, (50, 56, 80), (TILE//2, 6), (TILE//2, TILE//2), 1)
        self.tile_surfaces[T.WALL] = wall_surf.convert()

    def get_emoji_surface(self, emoji_char):
        if emoji_char not in self.emoji_cache:
            try:
                surf, rect = self.emoji_font.render(emoji_char, fgcolor=(255,255,255))
                self.emoji_cache[emoji_char] = (surf.convert_alpha(), rect)
            except Exception:
                surf = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
                pygame.draw.rect(surf, (255,0,0), (0,0,TILE,TILE), 2)
                self.emoji_cache[emoji_char] = (surf, surf.get_rect())
        return self.emoji_cache[emoji_char]

    def draw_emoji(self, x, y, emoji_char):
        surf, rect = self.get_emoji_surface(emoji_char)
        pos_x = x*TILE + (TILE - rect.width)//2 - rect.x
        pos_y = y*TILE + (TILE - rect.height)//2 - rect.y
        self.screen.blit(surf, (pos_x, pos_y))

    def reset_game(self):
        self.level = 1
        hero_emoji = random.choice(HERO_EMOJIS)
        self.player = Entity(0,0,"Hero",hero_emoji,COL_PLAYER,30,4,1,"player")
        self.player.max_hp = 30
        self.player.behavior = "Balanced"
        self.event_log = []
        self.new_level()
        self.add_log("🚪 A new hero descends into the dungeon.")

    def new_level(self):
        g,rooms,ppos,mons,items,npcs,stairs = generate_dungeon(self.level)
        self.grid=g; self.rooms=rooms; self.monsters=mons
        self.items=items; self.npcs=npcs; self.stairs=stairs
        self.player.x,self.player.y = ppos
        self.add_log(f"🪜 --- Depth {self.level} ---")

    def add_log(self,m):
        self.event_log.append(m)
        self.event_log = self.event_log[-40:]

    # ── AI & Turn Execution ──
    def player_think(self):
        if self.use_mcts:
            state = GameState(
                player=copy.deepcopy(self.player),
                monsters=copy.deepcopy(self.monsters),
                items=copy.deepcopy(self.items),
                npcs=copy.deepcopy(self.npcs),
                stairs=self.stairs, grid=self.grid, level=self.level
            )
            return mcts_search(state, iterations=30)
        else:
            return self.heuristic_think()

    def heuristic_think(self):
        p = self.player
        if p.behavior == "Survivalist" and p.hp < p.max_hp * 0.8:
            for it in p.inventory:
                if it.type==IT.POTION: return ("use",)
        if p.behavior not in ["Speedrunner", "Pacifist"]:
            for m in self.monsters:
                if m.alive and abs(m.x-p.x)+abs(m.y-p.y)==1: return ("attack", m.x, m.y)
            for (ix,iy),it in self.items:
                if ix==p.x and iy==p.y: return ("pickup",)
        
        nm,nd = None,999
        for m in self.monsters:
            if not m.alive: continue
            d = abs(m.x-p.x)+abs(m.y-p.y)
            if d<nd: nd=d; nm=m
        if p.behavior in ["Survivalist", "Pacifist"] and nm and nd <= 5:
            step = get_flee_step(self.grid, (p.x,p.y), (nm.x,nm.y))
            if step: return ("move", step[0]-p.x, step[1]-p.y)
        if p.behavior == "Aggressive" and nm and nd<=10: return ("goto",(nm.x,nm.y))
        if p.behavior not in ["Aggressive", "Pacifist"]:
            ni,nid = None,999
            for (ix,iy),it in self.items:
                d=abs(ix-p.x)+abs(iy-p.y)
                if d<nid: nid=d; ni=(ix,iy)
            if ni and nid<=15: return ("goto",ni)
        if self.stairs:
            if (p.x,p.y)==self.stairs: return ("descend",)
            return ("goto",self.stairs)
        return ("wait",)

    def execute(self, act):
        p=self.player
        k=act[0]
        if k=="move":
            p.x += act[1]; p.y += act[2]
        elif k=="attack":
            mx, my = act[1], act[2]
            for m in self.monsters:
                if m.alive and m.x == mx and m.y == my:
                    dmg = max(1, p.total_atk() - m.total_def())
                    m.hp -= dmg
                    self.add_log(f"💥 You strike {m.name} ({dmg}).")
                    if m.hp <= 0:
                        m.alive = False
                        cnt = drop_loot(m, self.items)
                        if cnt > 0: self.add_log(f"💀 {m.name} dropped {cnt} items!")
                        p.xp += m.xp; p.gold += m.gold
                        self.add_log(f"☠️ The {m.name} falls! (+{m.xp}xp, +{m.gold}g)")
                        need = p.level * 20
                        if p.xp >= need:
                            p.xp -= need; p.level += 1; p.max_hp += 8; p.hp = p.max_hp; p.atk += 1
                            self.add_log(f"⭐ *** Level {p.level}! ***")
                    break
        elif k=="pickup":
            res = try_pickup(p, self.items)
            if res: self.add_log(f"📦 You {res}.")
        elif k=="use":
            for i, it in enumerate(p.inventory):
                if it.type == IT.POTION:
                    p.hp = min(p.max_hp, p.hp + it.heal); p.inventory.pop(i)
                    self.add_log(f"🥤 Drank {it.name}. (+{it.heal} HP)"); break
        elif k=="talk":
            mx, my = act[1], act[2]
            for n in self.npcs:
                if n.x == mx and n.y == my:
                    self.add_log(f'💬 {n.name}: "{n.dialogue}"')
                    if "Merchant" in n.name and p.gold >= 10:
                        p.gold -= 10; ni = make_item(self.level); p.inventory.append(ni)
                        self.add_log(f"🤝 Traded 10g for {ni.name}.")
                        if ni.type != IT.POTION:
                            cur = p.equipped.get(ni.type)
                            cur_s = (cur.atk*2+cur.defn*2+cur.intl) if cur else -1
                            new_s = ni.atk*2+ni.defn*2+ni.intl
                            if new_s > cur_s:
                                if cur: p.inventory.append(cur)
                                p.equipped[ni.type] = ni; p.inventory.remove(ni)
                                self.add_log(f"🛡️ Equipped {ni.name}.")
                    break
        elif k=="goto":
            tx,ty=act[1]
            step=bfs_step(self.grid,(p.x,p.y),(tx,ty))
            if step and step!=(p.x,p.y):
                if not any(m.alive and (m.x,m.y)==step for m in self.monsters) and \
                   not any((n.x,n.y)==step for n in self.npcs):
                    p.x,p.y=step
        elif k=="descend":
            self.level += 1; self.add_log("⬇️ You descend deeper..."); self.new_level()

    def step_game(self):
        if not self.player.alive: return
        act = self.player_think()
        self.execute(act)
        self.npc_turn()
        self.monster_turn()
        self.monsters = [m for m in self.monsters if m.alive]

    def npc_turn(self):
        for n in self.npcs:
            res = try_heal(n)
            if res: self.add_log(f"🧪 {n.name} drank {res}!")
            
            if n.behavior == "Guard":
                attacked = False
                for mon in self.monsters:
                    if mon.alive and abs(n.x-mon.x)+abs(n.y-mon.y)==1:
                        dmg = max(1, n.total_atk() - mon.total_def())
                        mon.hp -= dmg
                        self.add_log(f"⚔️ {n.name} strikes {mon.name} ({dmg}).")
                        attacked = True
                        if mon.hp <= 0:
                            mon.alive = False
                            cnt = drop_loot(mon, self.items)
                            self.add_log(f"☠️ {mon.name} is struck down by {n.name}!")
                if not attacked:
                    nearest_m = None; nd = 999
                    for m in self.monsters:
                        if not m.alive: continue
                        d = abs(m.x-n.x) + abs(m.y-n.y)
                        if d < nd: nd = d; nearest_m = m
                    if nearest_m and nd <= 3:
                        step = bfs_step(self.grid, (n.x,n.y), (nearest_m.x, nearest_m.y))
                        if step and not any(m.alive and m.x==step[0] and m.y==step[1] for m in self.monsters):
                            n.x, n.y = step
                            
            elif n.behavior == "Looter":
                nearest_m = None; nd = 999
                for m in self.monsters:
                    if not m.alive: continue
                    d = abs(m.x-n.x) + abs(m.y-n.y)
                    if d < nd: nd = d; nearest_m = m
                if nearest_m and nd <= 4:
                    step = get_flee_step(self.grid, (n.x,n.y), (nearest_m.x, nearest_m.y))
                    if step: n.x, n.y = step
                else:
                    target = find_nearest_item(self.grid, (n.x,n.y), self.items)
                    if target:
                        if (n.x, n.y) == target: pass
                        else:
                            step = bfs_step(self.grid, (n.x,n.y), target)
                            if step and not any(m.alive and m.x==step[0] and m.y==step[1] for m in self.monsters) and \
                                      not any(o is not n and o.x==step[0] and o.y==step[1] for o in self.npcs) and \
                                      not (self.player.x==step[0] and self.player.y==step[1]):
                                n.x, n.y = step
                                
            elif n.behavior == "Flee":
                nearest_m = None; nd = 999
                for m in self.monsters:
                    if not m.alive: continue
                    d = abs(m.x-n.x) + abs(m.y-n.y)
                    if d < nd: nd = d; nearest_m = m
                if nearest_m and nd <= 4:
                    step = get_flee_step(self.grid, (n.x,n.y), (nearest_m.x, nearest_m.y))
                    if step: n.x, n.y = step
                    
            elif n.behavior in ["Patrol", "Wander"]:
                if random.random() < (0.3 if n.behavior == "Patrol" else 0.5):
                    dx, dy = random.choice([(0,1),(0,-1),(1,0),(-1,0)])
                    nx, ny = n.x+dx, n.y+dy
                    if 0<=nx<GRID_W and 0<=ny<GRID_H and self.grid[ny][nx]!=T.WALL:
                        if not any(m.x==nx and m.y==ny for m in self.monsters) and \
                           not any(o is not n and o.x==nx and o.y==ny for o in self.npcs) and \
                           not (self.player.x==nx and self.player.y==ny):
                            n.x, n.y = nx, ny
                            
        for n in self.npcs:
            res = try_pickup(n, self.items)
            if res: self.add_log(f"📦 {n.name} {res}.")

    def monster_turn(self):
        for m in self.monsters:
            if not m.alive: continue
            res = try_heal(m)
            if res: self.add_log(f"🧪 {m.name} drank {res}!")
            
            d = abs(m.x-self.player.x)+abs(m.y-self.player.y)
            atk_buff = 5 if (m.behavior == "Berserker" and m.hp < m.max_hp * 0.4) else 0
            
            if atk_buff > 0 and not m.enraged_logged:
                self.add_log(f"🔥 {m.name} enters a berserker rage!")
                m.enraged_logged = True
                
            if m.behavior == "Cowardly" and m.hp < m.max_hp * 0.5:
                if d <= 6:
                    step = get_flee_step(self.grid, (m.x,m.y), (self.player.x, self.player.y))
                    if step: m.x, m.y = step
                try_pickup(m, self.items)
                continue
            elif m.behavior == "Wanderer" and d > 3:
                if random.random() < 0.5:
                    dx, dy = random.choice([(0,1),(0,-1),(1,0),(-1,0)])
                    nx, ny = m.x+dx, m.y+dy
                    if 0<=nx<GRID_W and 0<=ny<GRID_H and self.grid[ny][nx]!=T.WALL:
                        if not any(o is not m and o.alive and o.x==nx and o.y==ny for o in self.monsters) and \
                           not any(n.x==nx and n.y==ny for n in self.npcs) and \
                           not (self.player.x==nx and self.player.y==ny):
                            m.x, m.y = nx, ny
                try_pickup(m, self.items)
                continue
            elif m.behavior == "Territorial" and d > 4:
                if abs(m.x-m.spawn_x) + abs(m.y-m.spawn_y) > 1:
                    step = bfs_step(self.grid, (m.x,m.y), (m.spawn_x, m.spawn_y))
                    if step and step != (m.spawn_x, m.spawn_y):
                        if not any(o is not m and o.alive and (o.x,o.y)==step for o in self.monsters):
                            m.x, m.y = step
                try_pickup(m, self.items)
                continue
            elif m.behavior == "Hoarder":
                if d <= 3:
                    step = get_flee_step(self.grid, (m.x,m.y), (self.player.x, self.player.y))
                    if step: m.x, m.y = step
                else:
                    target = find_nearest_item(self.grid, (m.x,m.y), self.items)
                    if target:
                        if (m.x, m.y) == target: pass
                        else:
                            step = bfs_step(self.grid, (m.x,m.y), target)
                            if step and not any(o is not m and o.alive and o.x==step[0] and o.y==step[1] for o in self.monsters):
                                m.x, m.y = step
                try_pickup(m, self.items)
                continue

            if d==1:
                dmg = max(1, (m.total_atk() + atk_buff) - self.player.total_def())
                self.player.hp -= dmg
                self.add_log(f"💥 {m.name} strikes you ({dmg}).")
                if self.player.hp<=0:
                    self.player.hp=0; self.player.alive=False
                    self.add_log(f"☠️ Slain by {m.name}!"); return
            elif d<=6:
                step=bfs_step(self.grid,(m.x,m.y),(self.player.x,self.player.y))
                if step and step!=(self.player.x,self.player.y):
                    if not any(o is not m and o.alive and (o.x,o.y)==step for o in self.monsters) and \
                       not any(n.x==step[0] and n.y==step[1] for n in self.npcs):
                        m.x,m.y=step
            
            res = try_pickup(m, self.items)
            if res: self.add_log(f"📦 {m.name} {res}.")

    # ── Update Loop ──
    def update(self, dt):
        locked,_ = self.focus.status()
        if locked:
            self.dist_time += dt
            self.paused_alpha = min(190, self.paused_alpha + dt*250)
            return
        self.focus_time += dt
        self.paused_alpha = max(0, self.paused_alpha - dt*300)
        if not self.player.alive: return
        self.tick_accum += dt
        delay = 0.14 if self.fast else 0.42
        while self.tick_accum >= delay:
            self.tick_accum -= delay
            self.step_game()

    # ── Rendering ──
    def draw(self):
        self.screen.fill(COL_BG)
        self._draw_dungeon()
        self._draw_entities()
        self._draw_sidebar()
        self._draw_log()
        if self.paused_alpha>0: self._draw_pause()
        if self.show_list: self._draw_list()
        if self.show_inv: self._draw_inventory()
        if self.ui_mode.startswith("add_"): self._draw_input()
        if not self.player.alive: self._draw_over()
        pygame.display.flip()

    def _draw_dungeon(self):
        for y in range(GRID_H):
            for x in range(GRID_W):
                t=self.grid[y][x]
                if t==T.WALL:
                    self.screen.blit(self.tile_surfaces[T.WALL], (x*TILE, y*TILE))
                elif t==T.FLOOR:
                    self.screen.blit(self.tile_surfaces[T.FLOOR], (x*TILE, y*TILE))
                elif t==T.STAIRS:
                    self.screen.blit(self.tile_surfaces[T.FLOOR], (x*TILE, y*TILE))
                    self.draw_emoji(x, y, "🕳️")

    def _draw_entities(self):
        for (ix,iy),it in self.items:
            self.draw_emoji(ix, iy, it.emoji)
        for n in self.npcs:
            self.draw_emoji(n.x, n.y, n.glyph)
        for m in self.monsters:
            if not m.alive: continue
            self.draw_emoji(m.x, m.y, m.glyph)
            if m.hp<m.max_hp:
                bw=TILE-4; bx=m.x*TILE+2; by=m.y*TILE+TILE-4
                pygame.draw.rect(self.screen,(60,20,20),(bx,by,bw,3))
                pygame.draw.rect(self.screen,COL_BAD,(bx,by,int(bw*m.hp/m.max_hp),3))
        if self.player.alive:
            self.draw_emoji(self.player.x, self.player.y, self.player.glyph)

    def _draw_sidebar(self):
        x=SIDEBAR_X
        pygame.draw.rect(self.screen,COL_PANEL,(x,0,SIDEBAR_W,HEIGHT))
        pygame.draw.line(self.screen,COL_EDGE,(x,0),(x,HEIGHT),2)
        p=self.player; y=12
        self.screen.blit(self.font_big.render("FOCUS ROGUE",True,COL_TEXT),(x+12,y)); y+=34
        
        locked,reason=self.focus.status()
        st="⏸ PAUSED" if locked else "▶ ACTIVE"
        self.screen.blit(self.font_sm.render(f"Sim: {st}",True,COL_BAD if locked else COL_GOOD),(x+12,y)); y+=20
        if locked and reason:
            self.screen.blit(self.font_tiny.render(f"🚫 trigger: {reason}",True,COL_DIM),(x+12,y))
        y+=22
        
        self.screen.blit(self.font_sm.render(f"⏱️ Focused:    {int(self.focus_time//60):02d}:{int(self.focus_time%60):02d}",True,COL_GOOD),(x+12,y)); y+=18
        self.screen.blit(self.font_sm.render(f"⌛ Distracted: {int(self.dist_time//60):02d}:{int(self.dist_time%60):02d}",True,COL_BAD),(x+12,y)); y+=22
        pygame.draw.line(self.screen,COL_EDGE,(x+12,y),(x+SIDEBAR_W-12,y)); y+=8
        
        ai_type = "🧠 MCTS AI" if self.use_mcts else "⚙️ Heuristic AI"
        self.screen.blit(self.font_sm.render(f"AI Mode: {ai_type}",True,COL_LOOT),(x+12,y)); y+=18
        self.screen.blit(self.font_sm.render(f"🎯 Player: {p.behavior}",True,COL_LOOT),(x+12,y)); y+=22
        
        self.screen.blit(self.font_sm.render(f"🦸 HERO  Lv.{p.level}",True,COL_PLAYER),(x+12,y)); y+=20
        
        hr=p.hp/p.max_hp if p.max_hp else 0
        hc=COL_GOOD if hr>0.5 else (COL_LOOT if hr>0.25 else COL_BAD)
        pygame.draw.rect(self.screen,(40,20,20),(x+12,y,SIDEBAR_W-24,14))
        pygame.draw.rect(self.screen,hc,(x+12,y,int((SIDEBAR_W-24)*hr),14))
        pygame.draw.rect(self.screen,COL_EDGE,(x+12,y,SIDEBAR_W-24,14),1)
        self.screen.blit(self.font_tiny.render(f"❤️ {p.hp}/{p.max_hp}",True,COL_TEXT),(x+16,y-1)); y+=22
        
        need=p.level*20; xr=p.xp/need if need else 0
        pygame.draw.rect(self.screen,(20,20,40),(x+12,y,SIDEBAR_W-24,8))
        pygame.draw.rect(self.screen,(120,140,255),(x+12,y,int((SIDEBAR_W-24)*xr),8)); y+=14
        
        self.screen.blit(self.font_tiny.render(f"⚔️ {p.total_atk()}  🛡️ {p.total_def()}  🧠 {p.total_int()}",True,COL_DIM),(x+12,y)); y+=16
        self.screen.blit(self.font_tiny.render(f"🪙 {p.gold}   🪜 Depth L{self.level}",True,COL_DIM),(x+12,y)); y+=16
        self.screen.blit(self.font_tiny.render(f"🎒 {len(p.inventory)} items",True,COL_DIM),(x+12,y)); y+=14
        
        y+=6; pygame.draw.line(self.screen,COL_EDGE,(x+12,y),(x+SIDEBAR_W-12,y)); y+=8
        self.screen.blit(self.font_sm.render("EQUIPPED",True,COL_TEXT),(x+12,y)); y+=18
        for t in [IT.WEAPON,IT.ARMOR,IT.CLOTHING,IT.BOOK,IT.ACCESSORY]:
            it=p.equipped.get(t)
            if it:
                txt=self.font_tiny.render(f"{it.emoji} {it.name}",True,it.color)
            else:
                txt=self.font_tiny.render(f"{t.value}: ---",True,COL_DIM)
            self.screen.blit(txt,(x+12,y)); y+=14
            
        y+=8; pygame.draw.line(self.screen,COL_EDGE,(x+12,y),(x+SIDEBAR_W-12,y)); y+=8
        for c in ["[A] add website","[S] add application",
                  "[L] view block-list","[I] view inventory",
                  "[F] toggle fast sim","[M] toggle MCTS/Heur.",
                  "[B] cycle Player Behavior","[R] restart hero","[ESC] quit"]:
            self.screen.blit(self.font_tiny.render(c,True,COL_DIM),(x+12,y)); y+=14

    def _draw_log(self):
        ly=GAME_H+4
        pygame.draw.rect(self.screen,COL_PANEL,(0,GAME_H,GAME_W,HEIGHT-GAME_H))
        pygame.draw.line(self.screen,COL_EDGE,(0,GAME_H),(GAME_W,GAME_H),2)
        entries=self.event_log[-6:]
        for i,e in enumerate(entries):
            col=COL_TEXT if i==len(entries)-1 else COL_DIM
            self.screen.blit(self.font_sm.render(e,True,col),(8,ly+i*16))

    def _draw_pause(self):
        ov=pygame.Surface((GAME_W,GAME_H),pygame.SRCALPHA)
        ov.fill((0,0,0,int(self.paused_alpha))); self.screen.blit(ov,(0,0))
        if self.paused_alpha>40:
            _,reason=self.focus.status()
            t=self.font_big.render("🛑 FOCUS LOST 🛑",True,COL_BAD)
            self.screen.blit(t,(GAME_W//2-t.get_width()//2,GAME_H//2-50))
            if reason:
                t2=self.font_sm.render(f"⚠️ Detected: {reason}",True,COL_TEXT)
                self.screen.blit(t2,(GAME_W//2-t2.get_width()//2,GAME_H//2-8))
            t3=self.font_sm.render("🚪 Close the distraction to resume the sim",True,COL_DIM)
            self.screen.blit(t3,(GAME_W//2-t3.get_width()//2,GAME_H//2+18))
            t4=self.font_sm.render("🕯️ Your hero waits in the darkness...",True,COL_DIM)
            self.screen.blit(t4,(GAME_W//2-t4.get_width()//2,GAME_H//2+40))

    def _draw_list(self):
        ov=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA); ov.fill((0,0,0,190))
        self.screen.blit(ov,(0,0))
        pw,ph=520,500; px=(WIDTH-pw)//2; py=(HEIGHT-ph)//2
        pygame.draw.rect(self.screen,COL_PANEL,(px,py,pw,ph),border_radius=8)
        pygame.draw.rect(self.screen,COL_EDGE,(px,py,pw,ph),2,border_radius=8)
        self.screen.blit(self.font_big.render("🚫 Block-list",True,COL_TEXT),(px+16,py+12))
        y=py+56
        self.screen.blit(self.font_sm.render("🌐 WEBSITES (window-title match):",True,COL_DIM),(px+16,y)); y+=22
        for s in self.focus.sites:
            self.screen.blit(self.font_sm.render(f"  • {s}",True,COL_TEXT),(px+16,y)); y+=18
        y+=10
        self.screen.blit(self.font_sm.render("🖥️ APPLICATIONS (process-name match):",True,COL_DIM),(px+16,y)); y+=22
        for s in self.focus.apps:
            self.screen.blit(self.font_sm.render(f"  • {s}",True,COL_TEXT),(px+16,y)); y+=18
        self.screen.blit(self.font_sm.render("[L] / [ESC] close",True,COL_DIM),(px+16,py+ph-26))

    def _draw_inventory(self):
        ov=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA); ov.fill((0,0,0,190))
        self.screen.blit(ov,(0,0))
        pw,ph=600,500; px=(WIDTH-pw)//2; py=(HEIGHT-ph)//2
        pygame.draw.rect(self.screen,COL_PANEL,(px,py,pw,ph),border_radius=8)
        pygame.draw.rect(self.screen,COL_EDGE,(px,py,pw,ph),2,border_radius=8)
        self.screen.blit(self.font_big.render("🎒 INVENTORY",True,COL_TEXT),(px+16,py+12))
        y=py+56
        self.screen.blit(self.font_sm.render("EQUIPPED:",True,COL_LOOT),(px+16,y)); y+=22
        for t in [IT.WEAPON,IT.ARMOR,IT.CLOTHING,IT.BOOK,IT.ACCESSORY]:
            it=self.player.equipped.get(t)
            if it:
                txt=self.font_sm.render(f"{it.emoji} {it.name} (ATK:{it.atk} DEF:{it.defn} INT:{it.intl})",True,it.color)
            else:
                txt=self.font_sm.render(f"{t.value}: ---",True,COL_DIM)
            self.screen.blit(txt,(px+16,y)); y+=20
        y+=10
        self.screen.blit(self.font_sm.render("BACKPACK:",True,COL_LOOT),(px+16,y)); y+=22
        if not self.player.inventory:
            self.screen.blit(self.font_sm.render("Empty",True,COL_DIM),(px+16,y))
        else:
            for it in self.player.inventory:
                stats = []
                if it.atk > 0: stats.append(f"ATK:{it.atk}")
                if it.defn > 0: stats.append(f"DEF:{it.defn}")
                if it.intl > 0: stats.append(f"INT:{it.intl}")
                if it.heal > 0: stats.append(f"HEAL:{it.heal}")
                txt=self.font_sm.render(f"{it.emoji} {it.name} ({', '.join(stats)})",True,it.color)
                self.screen.blit(txt,(px+16,y)); y+=18
        self.screen.blit(self.font_sm.render("[I] / [ESC] close",True,COL_DIM),(px+16,py+ph-26))

    def _draw_input(self):
        ov=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA); ov.fill((0,0,0,190))
        self.screen.blit(ov,(0,0))
        pw,ph=520,150; px=(WIDTH-pw)//2; py=(HEIGHT-ph)//2
        pygame.draw.rect(self.screen,COL_PANEL,(px,py,pw,ph),border_radius=8)
        pygame.draw.rect(self.screen,COL_EDGE,(px,py,pw,ph),2,border_radius=8)
        lab="🌐 Website keyword (e.g. youtube):" if self.ui_mode=="add_site" else "🖥️ App process (e.g. discord.exe):"
        self.screen.blit(self.font_sm.render(lab,True,COL_TEXT),(px+16,py+16))
        ib=pygame.Rect(px+16,py+46,pw-32,34)
        pygame.draw.rect(self.screen,(0,0,0),ib)
        pygame.draw.rect(self.screen,COL_EDGE,ib,2)
        self.screen.blit(self.font_sm.render(self.input_text+"|",True,COL_TEXT),(ib.x+8,ib.y+9))
        self.screen.blit(self.font_tiny.render("[ENTER] add   [ESC] cancel",True,COL_DIM),(px+16,py+96))

    def _draw_over(self):
        ov=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA); ov.fill((0,0,0,210))
        self.screen.blit(ov,(0,0))
        t=self.font_big.render("☠️ HERO FALLEN ☠️",True,COL_BAD)
        self.screen.blit(t,(WIDTH//2-t.get_width()//2,HEIGHT//2-70))
        for i,s in enumerate([f"🪜 Depth reached: L{self.level}",
                              f"⭐ Hero level: {self.player.level}",
                              f"🪙 Gold: {self.player.gold}",
                              f"⏱️ Time focused: {int(self.focus_time)}s"]):
            st=self.font_sm.render(s,True,COL_TEXT)
            self.screen.blit(st,(WIDTH//2-st.get_width()//2,HEIGHT//2-15+i*22))
        r=self.font_sm.render("[R] restart    [ESC] quit",True,COL_DIM)
        self.screen.blit(r,(WIDTH//2-r.get_width()//2,HEIGHT//2+90))

    # ── Input Handling ──
    def handle(self, ev):
        if ev.type==pygame.QUIT: self.running=False; return
        if ev.type!=pygame.KEYDOWN: return
        if self.ui_mode.startswith("add_"):
            if ev.key==pygame.K_RETURN:
                t=self.input_text.strip()
                if t:
                    if self.ui_mode=="add_site": self.focus.add_site(t)
                    else: self.focus.add_app(t)
                self.ui_mode="game"; self.input_text=""
            elif ev.key==pygame.K_ESCAPE:
                self.ui_mode="game"; self.input_text=""
            elif ev.key==pygame.K_BACKSPACE:
                self.input_text=self.input_text[:-1]
            elif ev.unicode and ev.unicode.isprintable():
                self.input_text+=ev.unicode
            return
        if self.show_list:
            if ev.key in (pygame.K_l,pygame.K_ESCAPE): self.show_list=False
            return
        if self.show_inv:
            if ev.key in (pygame.K_i,pygame.K_ESCAPE): self.show_inv=False
            return
        if ev.key==pygame.K_ESCAPE: self.running=False
        elif ev.key==pygame.K_a: self.ui_mode="add_site"; self.input_text=""
        elif ev.key==pygame.K_s: self.ui_mode="add_app"; self.input_text=""
        elif ev.key==pygame.K_l: self.show_list=True
        elif ev.key==pygame.K_i: self.show_inv=True
        elif ev.key==pygame.K_f: self.fast=not self.fast
        elif ev.key==pygame.K_m: self.use_mcts = not self.use_mcts
        elif ev.key==pygame.K_b:
            idx = PLAYER_BEHAVIORS.index(self.player.behavior)
            self.player.behavior = PLAYER_BEHAVIORS[(idx + 1) % len(PLAYER_BEHAVIORS)]
            self.add_log(f"🎯 Player Behavior changed to: {self.player.behavior}")
        elif ev.key==pygame.K_r: self.reset_game(); self.focus_time=0; self.dist_time=0

    def run(self):
        last=time.time()
        while self.running:
            now=time.time(); dt=now-last; last=now
            for ev in pygame.event.get(): self.handle(ev)
            self.update(dt); self.draw()
            self.clock.tick(FPS)
        pygame.quit()


# ──────────────────────────────────────────────────────────────────────────────
# 9. ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────────
if __name__=="__main__":
    Game().run()