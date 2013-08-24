class Tile(object):
    SIZE = 16
    def __init__(self, image, solid=False):
        self.image = image
        self.solid = solid

    def render(self, screen, x, y):
        if self.image:
            screen.blit(self.image, (x, y))

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
