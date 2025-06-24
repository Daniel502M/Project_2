import pygame
import pytmx


class TileMap:
    def __init__(self, filename):
        self.tmx_data = pytmx.load_pygame(filename, pixelalpha=True)
        self.tile_width = self.tmx_data.tilewidth
        self.tile_height = self.tmx_data.tileheight
        self.width = self.tmx_data.width * self.tile_width
        self.height = self.tmx_data.height * self.tile_height

    def draw(self, surface, offset=pygame.Vector2(0, 0), skip_door_ids=None):
        """
        Отрисовывает карту. Если указан skip_door_ids — не рисует двери с этими id.
        """
        if skip_door_ids is None:
            skip_door_ids = set()

        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    if gid == 0:
                        continue

                    pos_x = x * self.tile_width - offset.x
                    pos_y = y * self.tile_height - offset.y

                    # Пропускаем закрытую дверь, если она была заменена открытой
                    door_id = f"{x}_{y}"
                    if door_id in skip_door_ids:
                        continue

                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        surface.blit(tile, (pos_x, pos_y))

    def get_collision_rects(self, layer_name="Стены"):
        walls = []
        doors = []
        layer = self.tmx_data.get_layer_by_name(layer_name)

        open_gids = {
            15: 68,  # Верхняя
            20: 68,  # Нижняя
            12: 70,  # Правая
            13: 70,  # Левая
        }

        for x, y, gid in layer:
            if gid == 0:
                continue

            tile_x = x * self.tile_width
            tile_y = y * self.tile_height
            w = self.tile_width
            h = self.tile_height
            rect = None

            if gid in open_gids:
                if gid == 15:  # Верхняя дверь
                    rect = pygame.Rect(tile_x, tile_y, w, 13)
                    door_id = f"{x}_{y}"
                elif gid == 20:  # Нижняя дверь
                    rect = pygame.Rect(tile_x, tile_y + h - 13, w, 13)
                    door_id = f"{x}_{y}"
                elif gid == 12:  # Правая дверь
                    rect = pygame.Rect(tile_x + w - 13, tile_y, 13, h)
                    door_id = f"{x}_{y}"
                elif gid == 13:  # Левая дверь
                    rect = pygame.Rect(tile_x, tile_y, 13, h)
                    door_id = f"{x}_{y}"

                doors.append({
                    "id": door_id,
                    "rect": rect,
                    "pos": (x, y),
                    "gid": gid,
                    "open_gid": open_gids[gid],
                    "is_open": False
                })
                continue

            if gid in {11, 14, 18}:
                rect = pygame.Rect(tile_x + w - 13, tile_y, 13, h)
            elif gid in {10, 16, 24, 31}:
                rect = pygame.Rect(tile_x, tile_y, 13, h)
            elif gid == 4:
                rect = pygame.Rect(tile_x, tile_y, w, 13)
            elif gid in {19, 23}:
                rect = pygame.Rect(tile_x, tile_y + h - 13, w, 13)
            elif gid in {6, 7, 9, 17}:
                walls.append(pygame.Rect(tile_x + w - 13, tile_y, 13, h))
                walls.append(pygame.Rect(tile_x, tile_y, w, 13))
                continue
            elif gid in {21, 27, 29, 32}:
                walls.append(pygame.Rect(tile_x + w - 13, tile_y, 13, h))
                walls.append(pygame.Rect(tile_x, tile_y + h - 13, w, 13))
                continue
            elif gid in {3, 5, 8, 25}:
                walls.append(pygame.Rect(tile_x, tile_y, 13, h))
                walls.append(pygame.Rect(tile_x, tile_y, w, 13))
                continue
            elif gid in {22, 26, 28, 30}:
                walls.append(pygame.Rect(tile_x, tile_y, 13, h))
                walls.append(pygame.Rect(tile_x, tile_y + h - 13, w, 13))
                continue
            else:
                rect = pygame.Rect(tile_x, tile_y, w, h)

            if rect:
                walls.append(rect)

        return walls, doors

    def get_closed_door_image(self, door):
        """Возвращает изображение закрытой двери по GID."""
        return self.tmx_data.get_tile_image_by_gid(door["gid"])

    def get_object_collision_rects(self, layer_name="Объекты"):
        object_rects = []
        bullet_blocking_rects = []

        bullet_passable_gids = {49, 38, 43, 41, 50, 33, 34, 35, 59, 42, 54, 51, 52, 65,
                                46, 48, 56, 47, 61, 55, 66, 67, 53, 60, 44, 39, 40}

        try:
            layer = self.tmx_data.get_layer_by_name(layer_name)
        except Exception as e:
            print(f"[❌] Ошибка: слой '{layer_name}' не найден — {e}")
            return [], []

        if not isinstance(layer, pytmx.TiledTileLayer):
            print(f"[❌] Слой '{layer_name}' не является тайловым слоем!")
            return [], []

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

        for x, y, gid in layer:
            if gid == 0:
                continue

            tile_x = x * self.tile_width
            tile_y = y * self.tile_height

            if gid in gid_hitboxes:
                w, h, ox, oy = gid_hitboxes[gid]
                rect = pygame.Rect(tile_x + ox, tile_y + self.tile_height - h + oy, w, h)
            else:
                rect = pygame.Rect(tile_x, tile_y, self.tile_width, self.tile_height)

            object_rects.append(rect)
            if gid not in bullet_passable_gids:
                bullet_blocking_rects.append(rect)

        return object_rects, bullet_blocking_rects
