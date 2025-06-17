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
        walls = []
        doors = []
        layer = self.tmx_data.get_layer_by_name(layer_name)

        for x, y, gid in layer:
            if gid == 0:
                continue

            tile_x = x * self.tile_width
            tile_y = y * self.tile_height
            w = self.tile_width
            h = self.tile_height

            rect = None

            if gid == 15:  # Верхняя дверь
                rect = pygame.Rect(tile_x, tile_y, w, 13)
                doors.append({"id": f"top_door_{x}_{y}", "rect": rect})
                continue

            elif gid == 20:  # Нижняя дверь
                rect = pygame.Rect(tile_x, tile_y + h - 13, w, 13)
                doors.append({"id": f"bottom_door_{x}_{y}", "rect": rect})
                continue
            elif gid == 12:  # Правая дверь
                rect = pygame.Rect(tile_x + w - 13, tile_y, 13, h)
                doors.append({"id": f"bottom_door_{x}_{y}", "rect": rect})
                continue
            elif gid == 13:  # Левая дверь
                rect = pygame.Rect(tile_x, tile_y, 13, h)
                doors.append({"id": f"bottom_door_{x}_{y}", "rect": rect})
                continue

            elif gid == 11 or gid == 14 or gid == 18:  # Только правая сторона
                rect = pygame.Rect(tile_x + w - 13, tile_y, 13, h)

            elif gid == 10 or gid == 16 or gid == 24 or gid == 31:  # Только левая сторона
                rect = pygame.Rect(tile_x, tile_y, 13, h)

            elif gid == 4:  # Только верхняя сторона
                rect = pygame.Rect(tile_x, tile_y, w, 13)

            elif gid == 19 or gid == 23:  # Только нижняя сторона
                rect = pygame.Rect(tile_x, tile_y + h - 13, w, 13)

            elif gid == 6 or gid == 7 or gid == 9 or gid == 17:  # Верхняя и правая
                walls.append(pygame.Rect(tile_x + w - 13, tile_y, 13, h))
                walls.append(pygame.Rect(tile_x, tile_y, w, 13))
                continue

            elif gid == 21 or gid == 27 or gid == 29 or gid == 32:  # Нижняя и правая
                walls.append(pygame.Rect(tile_x + w - 13, tile_y, 13, h))
                walls.append(pygame.Rect(tile_x, tile_y + h - 13, w, 13))
                continue
            elif gid == 3 or gid == 5 or gid == 8 or gid == 25:  # Верхняя и левая
                walls.append(pygame.Rect(tile_x, tile_y, 13, h))
                walls.append(pygame.Rect(tile_x, tile_y, w, 13))
                continue

            elif gid == 22 or gid == 26 or gid == 28 or gid == 30:  # Нижняя и левая
                walls.append(pygame.Rect(tile_x, tile_y, 13, h))
                walls.append(pygame.Rect(tile_x, tile_y + h - 13, w, 13))
                continue
            else:
                rect = pygame.Rect(tile_x, tile_y, w, h)
                # pass
            if rect:
                walls.append(rect)

            # print(f"Tile at ({x}, {y}) has GID: {gid}")

        return walls, doors

    def get_object_collision_rects(self, layer_name="Объекты"):
        """
        Возвращает список прямоугольников коллизий для объектов с учётом их GID.
        Размеры коллизий подбираются индивидуально для каждого GID.
        """
        object_rects = []

        # Индивидуальные размеры объектов по GID
        gid_hitboxes = {
            49: (64, 64, 0, 0),  # Пример: стул (направленный вверх)
            38: (64, 64, 0, 0),  # Пример: стул (направленный вниз)
            43: (64, 64, 0, 0),  # Пример: стул (направленный влево)
            41: (64, 64, 0, 0),  # Пример: стул (направленный вправо)
            36: (64, 64, 0, 0),  # Пример: резервуар вертикальный
            37: (64, 64, 0, 0),  # Пример: резервуар горизонтальный
            50: (50, 115, 7, 64),  # Пример: кровать вертикальная (направленная вниз)
            33: (50, 113, 7, 64),  # Пример: кровать вертикальная (направленная вверх)
            34: (113, 50, 15, -7),  # Пример: кровать горизонтальная (направленная влево)
            35: (113, 50, 15, -7),  # Пример: кровать горизонтальная (направленная вправо)
            59: (38, 38, 13, -13),  # Пример: бочка
            45: (192, 192, 0, 128),  # Пример: котёл (монитор сверху, жёлтый резервуар слева)
            64: (192, 192, 0, 128),  # Пример: котёл (монитор сверху, жёлтый резервуар справа)
            58: (192, 192, 0, 128),  # Пример: котёл (монитор снизу, жёлтый резервуар слева)
            57: (192, 192, 0, 128),  # Пример: котёл (монитор снизу, жёлтый резервуар справа)
            62: (192, 192, 0, 128),  # Пример: котёл (монитор справа, жёлтый резервуар сверху)
            63: (192, 192, 0, 128),  # Пример: котёл (монитор слева, жёлтый резервуар сверху)
            42: (128, 192, 0, 128),  # Пример: стол (вертикальный)
            54: (192, 128, 0, 64),  # Пример: стол (горизонтальный)
            51: (46, 145, 9, 80),  # Пример: каталка с зомби вертикальная (коричневый, головой вверх)
            46: (46, 145, 9, 80),  # Пример: каталка с зомби вертикальная (коричневый, головой вниз)
            52: (145, 46, 0, -9),  # Пример: каталка с зомби горизонтальная (коричневый, головой влево)
            65: (145, 46, 0, -9),  # Пример: каталка с зомби горизонтальная (коричневый, головой влево)
            40: (145, 46, 0, -9),  # Пример: каталка с зомби горизонтальная (коричневый, головой вправо)
            56: (46, 145, 9, 80),  # Пример: каталка с зомби вертикальная (белый, головой вверх)
            39: (46, 145, 9, 80),  # Пример: каталка с зомби вертикальная (белый, головой вниз)
            47: (145, 46, 0, -9),  # Пример: каталка с зомби горизонтальная (белый, головой влево)
            61: (145, 46, 0, -9),  # Пример: каталка с зомби горизонтальная (белый, головой вправо)
            48: (145, 46, 0, -9),  # Пример: каталка с зомби горизонтальная (белый, головой вправо)
            55: (46, 145, 9, 80),  # Пример: каталка с зомби вертикальная (синий, головой вверх)
            67: (46, 145, 9, 80),  # Пример: каталка с зомби вертикальная (синий, головой вниз)
            53: (145, 46, 0, -9),  # Пример: каталка с зомби горизонтальная (синий, головой влево)
            60: (145, 46, 0, -9),  # Пример: каталка с зомби горизонтальная (синий, головой влево)
            66: (145, 46, 0, -9),  # Пример: каталка с зомби горизонтальная (синий, головой вправо)
            44: (145, 46, 0, -9)  # Пример: каталка с зомби горизонтальная (синий, головой вправо)
            # Добавляй нужные GID и размеры (ширина, высота)
        }

        try:
            layer = self.tmx_data.get_layer_by_name(layer_name)
        except Exception as e:
            print(f"[❌] Ошибка: слой '{layer_name}' не найден — {e}")
            return []

        if not isinstance(layer, pytmx.TiledTileLayer):
            print(f"[❌] Слой '{layer_name}' не является тайловым слоем!")
            return []

        for x, y, gid in layer:
            if gid == 0:
                continue
            # print(f"Tile at ({x},{y}) has GID: {gid}")

            tile_x = x * self.tile_width
            tile_y = y * self.tile_height

            if gid in gid_hitboxes:
                w, h, offset_x, offset_y = gid_hitboxes[gid]
                rect = pygame.Rect(
                    tile_x + offset_x,
                    tile_y + self.tile_height - h + offset_y,
                    w,
                    h
                )
            else:
                w = self.tile_width
                h = self.tile_height
                rect = pygame.Rect(tile_x, tile_y, w, h)

            object_rects.append(rect)

            # print(f"GID: {gid} → Rect({rect})")

        print(f"[✅] Объектов в слое '{layer_name}': {len(object_rects)}")
        return object_rects
