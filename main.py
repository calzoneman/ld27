from world import Tile, World
from entity import Entity, Player
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

    player = Player((0, 0), pygame.image.load("player.png"))
    world = World((100, 100), default=Tile.GRASS)
    world.add_entity(player)
    world.spawn_clock()

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
            player.move((player.x  , player.y-1))
        if keys[K_s]:
            player.move((player.x  , player.y+1))
        if keys[K_a]:
            player.move((player.x-1, player.y  ))
        if keys[K_d]:
            player.move((player.x+1, player.y  ))

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
