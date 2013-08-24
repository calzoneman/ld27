from collections import namedtuple

AABB = namedtuple('AABB', ['x', 'y', 'width', 'height'])

class Entity(object):
    def __init__(self, pos, img):
        self.x, self.y = pos
        self.w, self.h = img.get_width(), img.get_height()
        self.aabb = AABB(self.x - self.w/2, self.y - self.h/2, self.w, self.h)
        self.image = img

    def render(self, screen, pos):
        sx, sy = pos
        sx -= self.w / 2
        sy -= self.h / 2
        screen.blit(self.image, (sx, sy))
