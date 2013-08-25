import pygame

pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
pygame.font.init()

def loadimage(name, scale=1):
    img = pygame.image.load("assets/"+name)
    if scale == 1:
        return img
    surf = pygame.transform.scale(img, (img.get_width()*scale,
                                        img.get_height()*scale))
    return surf

def loadsound(name):
    return pygame.mixer.Sound("assets/"+name)

def tile_background(img, size):
    w, h = size
    iw, ih = img.get_width(), img.get_height()
    w /= iw
    h /= ih

    s = pygame.Surface(size)
    for i in range(w):
        for j in range(h):
            s.blit(img, (i * iw, j * ih))

    return s

def coloredrect(size, color):
    color = pygame.Color(*color)
    s = pygame.Surface(size)
    s.fill(color)
    return s

def makefont(size):
    return pygame.font.SysFont("Sans", size)
