import pygame

def loadimage(name, scale=1):
    img = pygame.image.load(name)
    if scale == 1:
        return img
    surf = pygame.transform.scale(img, (img.get_width()*scale,
                                        img.get_height()*scale))
    return surf
