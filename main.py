from world import Tile, World
from entity import Entity
from collections import defaultdict
import pygame
from pygame.locals import *
import sys

if __name__ == "__main__":
    pygame.init()
    pygame.display.init()
    SWIDTH, SHEIGHT = 640, 480
    TWIDTH, THEIGHT = SWIDTH / Tile.SIZE, SHEIGHT / Tile.SIZE
    screen = pygame.display.set_mode((SWIDTH, SHEIGHT), HWSURFACE | DOUBLEBUF)
    running = True
    keys = defaultdict(lambda: False)
    clock = pygame.time.Clock()

    grass = pygame.image.load("grass.png")
    water = pygame.image.load("water.png")
    ply = pygame.image.load("player.png")
    world = World((10, 10), default=Tile(grass))
    world.set_tile(0, 0, Tile(water))
    player = Entity((0, 0), ply)
    world.entities.append(player)

    ticks = 0

    while running:
        for ev in pygame.event.get():
            if ev.type == QUIT:
                pygame.quit()
                sys.exit(0)
            elif ev.type == KEYDOWN:
                keys[ev.key] = True
            elif ev.type == KEYUP:
                keys[ev.key] = False

        if keys[K_ESCAPE]:
            pygame.quit()
            sys.exit(0)
        if keys[K_w]:
            player.y -= 1
        if keys[K_s]:
            player.y += 1
        if keys[K_a]:
            player.x -= 1
        if keys[K_d]:
            player.x += 1

        px, py = player.x, player.y
        xo = SWIDTH/2 - player.x
        yo = SHEIGHT/2 - player.y
        screen.fill(pygame.Color(0, 0, 0))
        world.render(screen, (xo, yo), (TWIDTH, THEIGHT))
        pygame.display.flip()

        ticks += 1
        clock.tick(60)
        if ticks % 60 == 0:
            print(clock.get_fps())
