#!/usr/bin/env python2

from world import Tile, World
from entity import Entity, Player, Clock
from util import *
import math
from collections import defaultdict
import pygame
from pygame.locals import *
import sys


def blitfont(screen, msg, pos, align="LEFT"):
    x, y = pos
    if align == "CENTER":
        x -= msg.get_width() / 2
        y -= msg.get_height() / 2
    elif align == "RIGHT":
        x -= msg.get_width()
    screen.blit(msg, (x, y))

def show_intro(screen, font):
    y = screen.get_height() / 2
    x = screen.get_width() / 2
    black = pygame.Color(0, 0, 0)
    white = pygame.Color(255, 255, 255)

    msg = font.render("WASD to move", 1, WHITE, BLACK)
    blitfont(screen, msg, (x, y), align="CENTER")
    y += msg.get_height()

    msg = font.render("Arrow keys to attack", 1, WHITE, BLACK)
    blitfont(screen, msg, (x, y), align="CENTER")
    y += msg.get_height()

    msg = font.render("Collect clocks to reset the timer", 1, WHITE, BLACK)
    blitfont(screen, msg, (x, y), align="CENTER")
    y += msg.get_height()

    msg = font.render("Attack enemies for points", 1, WHITE, BLACK)
    blitfont(screen, msg, (x, y), align="CENTER")
    y += msg.get_height()

    msg = font.render("Press E to set off a bomb", 1, WHITE, BLACK)
    blitfont(screen, msg, (x, y), align="CENTER")
    y += msg.get_height()

    msg = font.render("Press space to start", 1, WHITE, BLACK)
    blitfont(screen, msg, (x, y), align="CENTER")
    y += msg.get_height()

if __name__ == "__main__":
    pygame.init()
    pygame.display.init()
    pygame.font.init()
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

    slash = loadsound("slash.wav")
    gameover = loadsound("gameover.wav")
    timewarn = loadsound("time.wav")

    SWIDTH, SHEIGHT = 640, 480
    TWIDTH, THEIGHT = SWIDTH / Tile.SIZE, SHEIGHT / Tile.SIZE
    FLAGS = HWSURFACE | DOUBLEBUF
    screen = pygame.display.set_mode((SWIDTH, SHEIGHT), FLAGS)
    pygame.display.set_caption("TimeRunner")

    regfont = makefont(20)
    WHITE = pygame.Color(255, 255, 255)
    BLACK = pygame.Color(0, 0, 0)
    GREEN = pygame.Color(0, 255, 0)
    YELLOW = pygame.Color(255, 255, 0)
    RED = pygame.Color(255, 0, 0)
    arrow = loadimage("arrow.png")
    water = loadimage("water.png")
    bg = tile_background(water, (SWIDTH, SHEIGHT))

    def play():
        keys = defaultdict(lambda: False)
        clock = pygame.time.Clock()
        paused = False

        world = World((50, 50), default=Tile.GRASS)
        px, py = world.random_position()
        player = Player((px, py), loadimage("player.png"))
        world.add_entity(player)
        MOVE_SPEED = 3
        for i in range(1):
            world.spawn_clock()
        for i in range(3):
            world.spawn_fastenemy()
        for i in range(5):
            world.spawn_slowenemy()

        ticks = 0
        started = False

        while True:
            for ev in pygame.event.get():
                if ev.type == QUIT:
                    pygame.quit()
                    sys.exit(0)
                elif ev.type == KEYDOWN:
                    keys[ev.key] = True
                    if ev.key == K_SPACE:
                        if not started:
                            started = True
                        else:
                            paused = not paused
                    if ev.key in [K_UP, K_LEFT, K_DOWN, K_RIGHT]:
                        slash.play()
                    if ev.key == K_e and player.bombs > 0:
                        world.bomb((player.x, player.y))
                        player.bombs -= 1
                elif ev.type == KEYUP:
                    keys[ev.key] = False

            if keys[K_ESCAPE]:
                pygame.quit()
                sys.exit(0)

            if started and not paused:
                if keys[K_w]:
                    player.move((player.x           , player.y-MOVE_SPEED))
                if keys[K_s]:
                    player.move((player.x           , player.y+MOVE_SPEED))
                if keys[K_a]:
                    player.move((player.x-MOVE_SPEED, player.y           ))
                if keys[K_d]:
                    player.move((player.x+MOVE_SPEED, player.y           ))

                if keys[K_UP]:
                    player.attack("UP")
                elif keys[K_LEFT]:
                    player.attack("LEFT")
                elif keys[K_DOWN]:
                    player.attack("DOWN")
                elif keys[K_RIGHT]:
                    player.attack("RIGHT")

                world.tick()

            if player.health <= 0 or world.timer <= 0:
                return player.score, ticks

            px, py = player.x, player.y
            xo = SWIDTH/2 - player.x
            yo = SHEIGHT/2 - player.y

            #screen.fill(BLACK)
            screen.blit(bg, (0, 0))

            # Draw world
            world.render(screen, (xo, yo), (TWIDTH, THEIGHT))

            # Draw HUD
            for e in world.entities:
                if isinstance(e, Clock):
                    ex = e.x + xo
                    ey = e.y + yo
                    if (ex < 0 or ex > SWIDTH or
                        ey < 0 or ey > SHEIGHT):
                        ang = math.atan2(ey - SHEIGHT/2, ex - SWIDTH/2)
                        icon = pygame.transform.rotate(arrow, -ang*180/math.pi)
                        w = icon.get_width()/2
                        h = icon.get_height()/2
                        dx = math.cos(ang) * 50 - h
                        dy = math.sin(ang) * 50 - w
                        screen.blit(icon, (SWIDTH/2 + dx, SHEIGHT/2 + dy))

            msg = regfont.render("{} fps".format(int(clock.get_fps())), 1,
                                 WHITE, BLACK)
            blitfont(screen, msg, (0, 0))
            msg = regfont.render("{:.1f} seconds".format(world.timer / 60.0), 1,
                                 WHITE, BLACK)
            blitfont(screen, msg, (SWIDTH-1, 0), align="RIGHT")
            msg = regfont.render("Bombs: {}".format(player.bombs), 1,
                                 WHITE, BLACK)
            blitfont(screen, msg, (0, 1*msg.get_height()))
            healthcol = GREEN
            if player.health < 3:
                healthcol = RED
            elif player.health < 6:
                healthcol = YELLOW
            msg = regfont.render("Health: {}".format(player.health), 1,
                                 healthcol, BLACK)
            blitfont(screen, msg, (0, 2*msg.get_height()))
            msg = regfont.render("Score: {}".format(player.score), 1,
                                 WHITE, BLACK)
            blitfont(screen, msg, (0, 3*msg.get_height()))

            if world.timer < 180 and ticks % 40 == 0:
                timewarn.play()

            if world.timer < 180 and (ticks / 20) % 2 == 0:
                msg = regfont.render("Time's running out!", 1, WHITE, BLACK)
                blitfont(screen, msg, (SWIDTH/2, msg.get_height()/2),
                                       align="CENTER")


            if not started:
                show_intro(screen, regfont)
            elif paused:
                msg = regfont.render("Paused", 1, WHITE, BLACK)
                blitfont(screen, msg, (SWIDTH/2, SHEIGHT/2), align="CENTER")
            pygame.display.flip()

            ticks += 1
            clock.tick(60)

    score, time = play()
    gameover.play()
    while True:
        for ev in pygame.event.get():
            if ev.type == QUIT or ev.type == KEYDOWN and ev.key == K_ESCAPE:
                pygame.quit()
                sys.exit(0)
        screen.fill(BLACK)
        msg = regfont.render("Score: {}".format(score), 1, WHITE, BLACK)
        blitfont(screen, msg, (SWIDTH/2, SHEIGHT/2+0*msg.get_height()),
                 align="CENTER")
        msg = regfont.render("Time: {} seconds".format(int(time/60)), 1,
                             WHITE, BLACK)
        blitfont(screen, msg, (SWIDTH/2, SHEIGHT/2+1*msg.get_height()),
                 align="CENTER")

        pygame.display.flip()
