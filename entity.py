from collections import namedtuple
from util import *
import math

AABB = namedtuple('AABB', ['x', 'y', 'width', 'height'])

class Entity(object):
    def __init__(self, pos, img):
        self.x, self.y = pos
        self.w, self.h = img.get_width(), img.get_height()
        self.image = img

    def get_AABB(self):
        return AABB(self.x - self.w/2, self.y - self.h/2, self.w, self.h)

    def collides(self, other):
        a = self.get_AABB()
        b = other.get_AABB()
        if a.x + a.width < b.x:
            return False
        if a.y + a.height < b.y:
            return False
        if a.x > b.x + b.width:
            return False
        if a.y > b.y + b.height:
            return False

        return True

    def on_collision(self, ent):
        pass

    def tick(self):
        pass

    def move(self, pos):
        tx, ty = self.world.screen_to_world(pos)
        if tx < 0 or ty < 0:
            return False
        if tx > self.world.width or ty > self.world.height:
            return False
        self.oldx, self.oldy = self.x, self.y
        self.x, self.y = pos
        if self.world:
            self.world.check_collision(self)

    def render(self, screen, pos):
        sx, sy = pos
        sx -= self.w / 2
        sy -= self.h / 2
        screen.blit(self.image, (sx, sy))

class MeleeSwipe(Entity):
    def on_collision(self, ent):
        print "Hit!"

ATTACK_UP    = loadimage("attack-up.png")
ATTACK_DOWN  = loadimage("attack-down.png")
ATTACK_LEFT  = loadimage("attack-left.png")
ATTACK_RIGHT = loadimage("attack-right.png")
AOFF = 10
class Player(Entity):
    def __init__(self, *args, **kwargs):
        Entity.__init__(self, *args, **kwargs)
        self.score = 0
        self.attack_timer = 0
        self.health = 10
        self.swipe = False

    def on_collision(self, ent):
        if isinstance(ent, Clock):
            self.score += 1
            print "Score: ",self.score
            self.world.spawn_clock()
            self.world.reset_timer()
        elif isinstance(ent, Enemy):
            self.health -= 1
            print "Health: ", self.health

    def tick(self):
        if self.attack_timer:
            self.attack_timer -= 1
        if self.attack_timer == 0:
            self.swipe = False

    def attack(self, direction):
        if self.attack_timer:
            return
        if direction == "UP":
            self.swipe = MeleeSwipe((self.x, self.y-self.h-AOFF), ATTACK_UP)
        elif direction == "DOWN":
            self.swipe = MeleeSwipe((self.x, self.y+self.h+AOFF), ATTACK_DOWN)
        elif direction == "LEFT":
            self.swipe = MeleeSwipe((self.x-self.w-AOFF, self.y), ATTACK_LEFT)
        elif direction == "RIGHT":
            self.swipe = MeleeSwipe((self.x+self.w+AOFF, self.y), ATTACK_RIGHT)

        self.swipe.direction = direction
        self.world.check_collision(self.swipe)
        
        self.attack_timer = 10

    def render(self, screen, pos):
        x, y = pos
        Entity.render(self, screen, pos)
        if self.swipe:
            if self.swipe.direction == "UP":
                self.swipe.render(screen, (x, y - self.h - AOFF))
            elif self.swipe.direction == "DOWN":
                self.swipe.render(screen, (x, y + self.h + AOFF))
            elif self.swipe.direction == "LEFT":
                self.swipe.render(screen, (x - self.w - AOFF, y))
            elif self.swipe.direction == "RIGHT":
                self.swipe.render(screen, (x + self.w + AOFF, y))

class Enemy(Entity):
    KB_SPEED = 2
    MOVE_SPEED = 2

    def __init__(self, *args, **kwargs):
        Entity.__init__(self, *args, **kwargs)
        self.knockbacktimer = 0
        self.knockback = (0, 0)
        self.health = 5
        self.target = None

    def tick(self):
        if self.knockbacktimer:
            self.knockbacktimer -= 1
            kx, ky = self.knockback
            self.move((self.x + kx, self.y + ky))
            return

        if self.target:
            x, y = self.x, self.y
            ox, oy = self.target.x, self.target.y
            d = (x - ox)**2 + (y - oy)**2
            #if d > 100000:
            #    return

            ang = math.atan2(oy - y, ox - x)
            dx, dy = math.cos(ang), math.sin(ang)
            self.move((x + Enemy.MOVE_SPEED * dx, y + Enemy.MOVE_SPEED * dy))

    def on_collision(self, ent):
        if isinstance(ent, MeleeSwipe):
            self.health -= 1
            if self.health == 0:
                self.world.remove_entity(self)
            if ent.direction == "UP":
                self.knockback = (0, -Enemy.KB_SPEED)
            elif ent.direction == "DOWN":
                self.knockback = (0, Enemy.KB_SPEED)
            elif ent.direction == "LEFT":
                self.knockback = (-Enemy.KB_SPEED, 0)
            elif ent.direction == "RIGHT":
                self.knockback = (Enemy.KB_SPEED, 0)

            self.knockbacktimer = 10
        elif isinstance(ent, Player):
            self.world.remove_entity(self)

class Clock(Entity):
    def on_collision(self, ent):
        if isinstance(ent, Player):
            self.world.remove_entity(self)
