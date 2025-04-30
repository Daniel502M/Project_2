import pygame
import pytmx


class TileMap:
    def __init__(self, filename):
        self.tmx_data = pytmx.load_pygame(filename, pixelalpha=True)
        self.tile_width = self.tmx_data.tilewidth
        self.tile_height = self.tmx_data.tileheight
        self.width = self.tmx_data.width * self.tile_width
        self.height = self.tmx_data.height * self.tile_height

    def draw(self, surface, offset=pygame.Vector2(0, 0)):
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        pos_x = x * self.tile_width - offset.x
                        pos_y = y * self.tile_height - offset.y
                        surface.blit(tile, (pos_x, pos_y))

    def get_collision_rects(self, layer_name="Стены"):
        rects = []
        layer = self.tmx_data.get_layer_by_name(layer_name)
        for x, y, gid in layer:
            if gid != 0:  # не пустой тайл — считается препятствием
                rect = pygame.Rect(
                    x * self.tile_width,
                    y * self.tile_height,
                    self.tile_width,
                    self.tile_height
                )
                rects.append(rect)
        return rects
