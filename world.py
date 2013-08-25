import pygame
import random
from entity import *
from util import *

clock_img = loadimage("clock.png")#pygame.image.load("clock.png")
enemy_img = loadimage("enemy.png")

class Tile(object):
    SIZE = 16
    def __init__(self, image, solid=False):
        self.image = image
        self.solid = solid

    def render(self, screen, x, y):
        if self.image:
            screen.blit(self.image, (x, y))

Tile.GRASS = Tile(loadimage("grass.png"))
Tile.WALL  = Tile(loadimage("wall.png"), solid=True)

class World(object):
    def __init__(self, size, default=Tile(None)):
        self.width, self.height = size
        self.tiles = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append(default)
            self.tiles.append(row)
        self.entities = []
        self.player_entity = None
        self.timer = 600
        perlin(self)

    def get_tile(self, x, y):
        x = x % self.width
        y = y % self.height
        return self.tiles[y][x]

    def set_tile(self, x, y, t):
        x = x % self.width
        y = y % self.height
        self.tiles[y][x] = t

    def add_entity(self, e):
        e.world = self
        if isinstance(e, Player):
            self.player_entity = e
        elif isinstance(e, Enemy):
            e.target = self.player_entity
        if e not in self.entities:
            self.entities.append(e)

    def remove_entity(self, e):
        if e in self.entities:
            self.entities.remove(e)

    def check_collision(self, e):
        for f in self.entities:
            if f != e and e.collides(f):
                e.on_collision(f)
                f.on_collision(e)

    def screen_to_world(self, pos):
        x, y = pos
        x = int(x / Tile.SIZE)
        y = int(y / Tile.SIZE)
        return (x, y)

    def random_position(self):
        x = random.randint(0, self.width)
        y = random.randint(0, self.height)
        while self.get_tile(x, y).solid:
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
        return x * Tile.SIZE, y * Tile.SIZE

    def spawn_clock(self):
        x, y = self.random_position()
        e = Clock((x, y), clock_img)
        self.add_entity(e)

    def spawn_fastenemy(self):
        x, y = self.random_position()
        if self.player_entity:
            px, py = self.player_entity.x, self.player_entity.y
            # Don't be evil in our spawning pattern
            while (y-py)**2 + (x-px)**2 < 100000:
                x, y = self.random_position()
        e = FastEnemy((x, y), enemy_img)
        self.add_entity(e)

    def spawn_slowenemy(self):
        x, y = self.random_position()
        if self.player_entity:
            px, py = self.player_entity.x, self.player_entity.y
            # Don't be evil in our spawning pattern
            while (y-py)**2 + (x-px)**2 < 100000:
                x, y = self.random_position()
        e = SlowEnemy((x, y), enemy_img)
        self.add_entity(e)

    def bomb(self, pos):
        for i in range(20):
            ang = random.random() * 2*math.pi
            speed = random.random() * 5
            e = ShrapnelParticle(pos, 
                                 (speed*math.cos(ang), speed*math.sin(ang)))
            self.add_entity(e)

    def reset_timer(self):
        self.timer = 600

    def tick(self):
        self.timer -= 1
        for e in self.entities:
            e.tick()

    def render(self, screen, offset, size):
        xo, yo = offset
        tx = int(-xo / Tile.SIZE)
        ty = int(-yo / Tile.SIZE)
        w, h = size
        for y in range(ty, ty + h + 1):
            if y < 0:
                continue
            if y > self.height:
                break
            for x in range(tx, tx + w + 1):
                if x < 0 or x > self.width:
                    continue
                t = self.get_tile(x, y)
                t.render(screen, xo + x*Tile.SIZE, yo + y*Tile.SIZE)
        for e in self.entities:
            pos = (xo + e.x, yo + e.y)
            e.render(screen, pos)

def interpolate(a, b, x):
    ft = x * math.pi
    f = (1 - math.cos(ft)) * 0.5

    return a*(1 - f) + b*f

seed = random.randint(-3489423895, 23452345)
def noise(x, y):
    n = x + y*57 + seed
    n = (n << 13) ^ n
    return 1.0 - ((n * (n*n*15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824.0

def smoothnoise(x, y):
    corners = (noise(x-1, y-1)+noise(x+1,y-1)+noise(x-1,y+1)+noise(x+1,y+1))/16
    sides = (noise(x-1,y)+noise(x+1,y)+noise(x,y-1)+noise(x,y+1))/8
    center = noise(x, y) / 4
    return corners + sides + center

def intnoise(x, y):
    ix = int(x)
    fx = x - ix
    iy = int(y)
    fy = y - iy

    v1 = smoothnoise(ix, iy)
    v2 = smoothnoise(ix+1, iy)
    v3 = smoothnoise(ix, iy+1)
    v4 = smoothnoise(ix+1, iy+1)

    i1 = interpolate(v1, v2, fx)
    i2 = interpolate(v3, v4, fx)

    return interpolate(i1, i2, fy)

def perlin_noise(x, y):
    total = 0
    p = 0.20
    n = 3
    for i in range(n):
        f = 2**i
        a = p**i
        total += intnoise(x * f, y * f) * a

    return total

def perlin(world):
    for i in range(world.width):
        for j in range(world.height):
            h = perlin_noise(i, j)
            if h > 0.25:
                world.set_tile(i, j, Tile.WALL)
