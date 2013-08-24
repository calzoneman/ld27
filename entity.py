from collections import namedtuple

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

    def move(self, pos):
        self.oldx, self.oldy = self.x, self.y
        self.x, self.y = pos
        if self.world:
            self.world.check_collision(self)

    def render(self, screen, pos):
        sx, sy = pos
        sx -= self.w / 2
        sy -= self.h / 2
        screen.blit(self.image, (sx, sy))

class Player(Entity):
    def __init__(self, *args, **kwargs):
        Entity.__init__(self, *args, **kwargs)
        self.score = 0

    def on_collision(self, ent):
        if isinstance(ent, Clock):
            self.score += 1
            print "Score: ",self.score
            self.world.spawn_clock()

class Clock(Entity):
    def on_collision(self, ent):
        if isinstance(ent, Player):
            self.world.remove_entity(self)
