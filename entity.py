from collections import namedtuple
from util import *
import math

AABB = namedtuple('AABB', ['x', 'y', 'width', 'height'])

class Entity(object):
    def __init__(self, pos, img):
        self.x, self.y = pos
        self.w, self.h = img.get_width(), img.get_height()
        self.image = img

    def die(self):
        if self.world:
            self.world.remove_entity(self)

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
        if sx < -self.w or sy < -self.h:
            return
        if sx > screen.get_width() or sy > screen.get_height():
            return
        screen.blit(self.image, (sx, sy))

class MeleeSwipe(Entity):
    def on_collision(self, ent):
        if isinstance(ent, Enemy):
            self.player.score += 1

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
        self.recovery_timer = 0

    def on_collision(self, ent):
        if isinstance(ent, Clock):
            self.world.spawn_clock()
            self.world.reset_timer()
        elif isinstance(ent, Enemy):
            if self.recovery_timer > 0:
                return
            self.health -= 1
            self.recovery_timer = 60

    def tick(self):
        if self.attack_timer:
            self.attack_timer -= 1
        if self.attack_timer == 0:
            self.swipe = False
        if self.recovery_timer:
            self.recovery_timer -= 1

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
        self.swipe.player = self
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

    def __init__(self, *args, **kwargs):
        Entity.__init__(self, *args, **kwargs)
        self.knockbacktimer = 0
        self.knockback = (0, 0)
        self.health = 5
        self.target = None
        self.speed = 2

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
            self.move((x + self.speed * dx, y + self.speed * dy))

    def on_collision(self, ent):
        if isinstance(ent, MeleeSwipe):
            self.health -= 1
            if self.health == 0:
                self.die()
                return
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
            self.health -= 1
            if self.health == 0:
                self.die()
            
            ang = math.atan2(ent.y - self.y, ent.x - self.x)
            self.knockback = (-math.cos(ang)*Enemy.KB_SPEED, 
                              -math.sin(ang)*Enemy.KB_SPEED)
            self.knockbacktimer = 10

class SlowEnemy(Enemy):
    def __init__(self, *args, **kwargs):
        Enemy.__init__(self, *args, **kwargs)
        self.health = 5
        self.speed = 2

    def die(self):
        Entity.die(self)
        if self.world:
            self.world.spawn_slowenemy()

class FastEnemy(Enemy):
    def __init__(self, *args, **kwargs):
        Enemy.__init__(self, *args, **kwargs)
        self.health = 1
        self.speed = 3

    def die(self):
        Entity.die(self)
        if self.world:
            self.world.spawn_fastenemy()

class Clock(Entity):
    def on_collision(self, ent):
        if isinstance(ent, Player):
            self.world.remove_entity(self)
