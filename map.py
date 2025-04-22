import pygame
import pytmx

from menu import display


pygame.draw.rect(display, (255, 255, 255), (300, 300, 16, 16))


class Map:
    def __init__(self, tmx_file):
        self.tmx_data = pytmx.load_pygame(tmx_file, pixelalpha=True)
        self.tile_size = self.tmx_data.tilewidth
        self.stone_positions = []
        self.coal_positions = []

        # Извлечение позиций камней и угля из тайловой карты
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    if gid in [89, 90]:
                        self.stone_positions.append((x * self.tile_size, y * self.tile_size))
                    elif gid in [94, 95]:
                        self.coal_positions.append((x * self.tile_size, y * self.tile_size))

    def draw(self, surface, camera):
        """Отрисовка карты с учетом смещения камеры."""
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        screen_x = x * self.tile_size - camera.offset_x
                        screen_y = y * self.tile_size - camera.offset_y
                        surface.blit(tile, (screen_x, screen_y))

    def get_stone_positions(self):
        return self.stone_positions

    def get_coal_positions(self):
        return self.coal_positions
