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
            if gid == 0:
                continue

            tile_x = x * self.tile_width
            tile_y = y * self.tile_height

            w = self.tile_width
            h = self.tile_height
            half_w = w // 2
            half_h = h // 2

            # Пример сопоставления по gid — замените на реальные GID из вашей карты
            if gid == 7:  # Только правая сторона
                rect = pygame.Rect(tile_x + w - 13, tile_y, 13, h)

            elif gid == 6:  # Только левая сторона
                rect = pygame.Rect(tile_x, tile_y, 13, h)

            elif gid == 4:  # Только верхняя сторона
                rect = pygame.Rect(tile_x, tile_y, w, 13)

            elif gid == 12:  # Только нижняя сторона
                rect = pygame.Rect(tile_x, tile_y + h - 13, w, 13)

            elif gid == 5:  # Верхняя и правая
                rects.append(pygame.Rect(tile_x + w - 13, tile_y, 13, h))
                rects.append(pygame.Rect(tile_x, tile_y, w, 13))
                continue

            elif gid == 13:  # Нижняя и правая
                rects.append(pygame.Rect(tile_x + w - 13, tile_y, 13, h))
                rects.append(pygame.Rect(tile_x, tile_y + h - 13, w, 13))
                continue

            elif gid == 3:  # Верхняя и левая
                rects.append(pygame.Rect(tile_x, tile_y, 13, h))
                rects.append(pygame.Rect(tile_x, tile_y, w, 13))
                continue

            elif gid == 11:  # Нижняя и левая
                rects.append(pygame.Rect(tile_x, tile_y, 13, h))
                rects.append(pygame.Rect(tile_x, tile_y + h - 13, w, 13))
                continue

            elif gid == 8:  # Верхняя и левая с продолжением вверх
                rects.append(pygame.Rect(tile_x, tile_y, 13, h))
                rects.append(pygame.Rect(tile_x, tile_y, w, 13))
                continue

            elif gid == 9:  # Верхняя дверь
                rect = pygame.Rect(tile_x, tile_y, w, 13)

            elif gid == 10:  # Верхняя дверь
                rect = pygame.Rect(tile_x, tile_y + h - 13, w, 13)

            else:  # Полный тайл по умолчанию
                rect = pygame.Rect(tile_x, tile_y, w, h)

            rects.append(rect)

        return rects



