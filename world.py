import pygame
import random
from entity import Entity, Clock

clock_img = pygame.image.load("clock.png")

class Tile(object):
    SIZE = 16
    def __init__(self, image, solid=False):
        self.image = image
        self.solid = solid

    def render(self, screen, x, y):
        if self.image:
            screen.blit(self.image, (x, y))

Tile.GRASS = Tile(pygame.image.load("grass.png"))

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

    def spawn_clock(self):
        x = random.randint(0, self.width * Tile.SIZE)
        y = random.randint(0, self.height * Tile.SIZE)
        e = Clock((x, y), clock_img)
        print "Spawned clock",x/Tile.SIZE,y/Tile.SIZE
        self.add_entity(e)

    def render(self, screen, offset, size):
        xo, yo = offset
        tx = int(-xo / Tile.SIZE)
        ty = int(-yo / Tile.SIZE)
        w, h = size
        for y in range(ty, h + 1):
            if y < 0:
                continue
            if y > self.height:
                break
            for x in range(tx, w + 1):
                if x < 0 or x > self.width:
                    continue
                t = self.get_tile(x, y)
                t.render(screen, xo + x*Tile.SIZE, yo + y*Tile.SIZE)
        for e in self.entities:
            pos = (xo + e.x, yo + e.y)
            e.render(screen, pos)
