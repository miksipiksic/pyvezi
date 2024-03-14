import os

import pygame
import config


class BaseSprite(pygame.sprite.Sprite):
    images_dict = {}

    def __init__(self, image_name, position, size, offset=(0, 0)):
        super().__init__()
        if image_name in BaseSprite.images_dict:
            image = BaseSprite.images_dict[image_name]
        else:
            image = pygame.image.load(os.path.join(config.IMG_FOLDER, image_name)).convert()
            image = pygame.transform.scale(image, size)
            image.set_colorkey(config.WHITE)
            BaseSprite.images_dict[image_name] = image
        self.image = image.copy()
        self.rect = self.image.get_rect()
        self.rect.topleft = (position[1] * config.TILE_SIZE + offset[1], position[0] * config.TILE_SIZE + offset[0])

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Tile(BaseSprite):
    def __init__(self, position):
        super().__init__('tile.png', position, (config.TILE_SIZE, config.TILE_SIZE))

    def draw_transparent(self, screen, active):
        self.image.set_alpha(200 if active else 255)
        self.draw(screen)


class Checker(BaseSprite):
    def __init__(self, image_name, position, goal_position):
        super().__init__(image_name, position, (config.TILE_SIZE, config.TILE_SIZE))
        self.goal_position = goal_position

    def gravity(self):
        if self.rect.y < self.goal_position[0] * config.TILE_SIZE:
            self.rect.y += config.GRAVITY
            return True
        return False


class WinChecker(BaseSprite):
    def __init__(self, position):
        super().__init__('green.png', position, (config.TILE_SIZE // 4, config.TILE_SIZE // 4),
                         (int(config.TILE_SIZE * 3 / 8), int(config.TILE_SIZE * 3 / 8)))
