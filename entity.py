from collections import namedtuple
from util import *
import math
import random

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
        oldtx, oldty = self.world.screen_to_world((self.x, self.y))
        if tx < 0 or ty < 0:
            return False
        if tx > self.world.width or ty > self.world.height:
            return False
        if self.world.get_tile(tx, oldty).solid:
            pos = (self.x, pos[1])
        if self.world.get_tile(oldtx, ty).solid:
            pos = (pos[0], self.y)
        self.oldx, self.oldy = self.x, self.y
        self.x, self.y = pos
        if self.world:
            self.world.check_collision(self)
        return True

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
            self.player.score += 10
            self.player.world.add_entity(TextParticle((ent.x, ent.y), "+10"))

ATTACK_UP    = loadimage("attack-up.png")
ATTACK_DOWN  = loadimage("attack-down.png")
ATTACK_LEFT  = loadimage("attack-left.png")
ATTACK_RIGHT = loadimage("attack-right.png")
AOFF = 10
hurt = loadsound("hurt.wav")
class Player(Entity):
    def __init__(self, *args, **kwargs):
        Entity.__init__(self, *args, **kwargs)
        self.score = 0
        self.attack_timer = 0
        self.health = 10
        self.swipe = False
        self.recovery_timer = 0
        self.bombs = 2

    def on_collision(self, ent):
        if isinstance(ent, Clock):
            self.score += 100
            self.world.spawn_clock()
            self.world.reset_timer()
        elif isinstance(ent, Enemy):
            if self.recovery_timer > 0:
                return
            hurt.play()
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

        elif isinstance(ent, ShrapnelParticle):
            self.health = 0
            self.die()

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
            make_deathparticles((self.x, self.y), self.world)
            self.world.spawn_slowenemy()

class FastEnemy(Enemy):
    def __init__(self, *args, **kwargs):
        Enemy.__init__(self, *args, **kwargs)
        self.health = 1
        self.speed = 3

    def die(self):
        Entity.die(self)
        if self.world:
            make_deathparticles((self.x, self.y), self.world)
            self.world.spawn_fastenemy()

clock_get = loadsound("clock_get.wav")
class Clock(Entity):
    def on_collision(self, ent):
        if isinstance(ent, Player):
            clock_get.play()
            self.world.add_entity(TextParticle((self.x, self.y), "+100"))
            self.world.remove_entity(self)
            
def make_deathparticles(pos, world):
    for i in range(10):
        ang = random.random() * 2*math.pi
        speed = random.random() * 3
        e = BaseParticle(pos, (speed*math.cos(ang), speed*math.sin(ang)))
        world.add_entity(e)

def sign(x):
    if x == 0:
        return 0
    return x / abs(x)

PARTICLE_RED = coloredrect((4, 4), (187, 0, 0))
class BaseParticle(Entity):
    def __init__(self, pos, vec, timer=60):
        self.x, self.y = pos
        self.w, self.h = PARTICLE_RED.get_width(), PARTICLE_RED.get_height()
        self.image = PARTICLE_RED
        self.vec = list(vec)
        self.timer = timer
        self.damp = 0.1

    def tick(self):
        self.timer -= 1
        if self.timer == 0:
            self.die()

        self.move((self.vec[0] + self.x, self.vec[1] + self.y))
        self.vec[0] -= self.damp * sign(self.vec[0])
        if abs(self.vec[0]) < 0.2:
            self.vec[0] = 0
        self.vec[1] -= self.damp * sign(self.vec[1])
        if abs(self.vec[1]) < 0.2:
            self.vec[1] = 0

PARTICLE_GREY = coloredrect((4, 4), (60, 60, 60))
class ShrapnelParticle(BaseParticle):
    def __init__(self, *args, **kwargs):
        BaseParticle.__init__(self, *args, **kwargs)
        self.image = PARTICLE_GREY
        self.damp = 0.01

SMALLFONT = makefont(14)
class TextParticle(Entity):
    def __init__(self, pos, text):
        self.x, self.y = pos
        self.text = text
        self.w, self.h = 0, 0
        self.opacity = 255
        self.dy = -2.0

    def tick(self):
        self.y += self.dy
        self.dy += 0.1
        self.opacity -= 1
        if self.opacity <= 0:
            self.die()

    def render(self, screen, pos):
        fg = (0, 0, 0, self.opacity)
        self.image = SMALLFONT.render(self.text, 1, fg)
        Entity.render(self, screen, pos)
