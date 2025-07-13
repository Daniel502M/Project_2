import pygame
import pytmx
from map_config import map_configs


class TileMap:
    def __init__(self, filename):
        self.filename = filename
        self.tmx_data = pytmx.load_pygame(filename, pixelalpha=True)
        self.tile_width = self.tmx_data.tilewidth
        self.tile_height = self.tmx_data.tileheight
        self.width = self.tmx_data.width * self.tile_width
        self.height = self.tmx_data.height * self.tile_height

        self.config = map_configs.get(filename)
        if self.config is None:
            raise ValueError(f"[❌] Нет конфигурации карты для {filename}")

    def draw(self, surface, offset=pygame.Vector2(0, 0), skip_door_ids=None):
        """Отрисовывает карту. Если указан skip_door_ids — не рисует двери с этими id."""
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
        """Возвращает список прямоугольников коллизий: стены и двери."""
        walls = []
        doors = []
        layer = self.tmx_data.get_layer_by_name(layer_name)

        open_gids = self.config.get("open_gids", {})
        wall_gids = self.config.get("wall_gids", set())
        wall_hitboxes = self.config.get("wall_hitboxes", {})

        for x, y, gid in layer:
            if gid == 0:
                continue

            tile_x = x * self.tile_width
            tile_y = y * self.tile_height
            w, h = self.tile_width, self.tile_height

            if gid in open_gids:
                # Добавление двери с хитбоксом по направлению
                if gid in [15, 25]:  # Верхняя
                    rect = pygame.Rect(tile_x, tile_y, w, 13)
                elif gid in [20, 26]:  # Нижняя
                    rect = pygame.Rect(tile_x, tile_y + h - 13, w, 13)
                elif gid in [12, 27]:  # Правая
                    rect = pygame.Rect(tile_x + w - 13, tile_y, 13, h)
                elif gid in [13, 28]:  # Левая
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

            # Стены с кастомными хитбоксами
            if gid in wall_hitboxes:
                for ox, oy, ww, hh in wall_hitboxes[gid]:
                    rect = pygame.Rect(tile_x + ox, tile_y + oy, ww, hh)
                    walls.append(rect)
                continue

            # Простые стены без хитбоксов
            if gid in wall_gids:
                rect = pygame.Rect(tile_x, tile_y, w, h)
                walls.append(rect)

        return walls, doors

    def get_closed_door_image(self, door):
        """Возвращает изображение закрытой двери по GID."""
        return self.tmx_data.get_tile_image_by_gid(door["gid"])

    def get_object_collision_rects(self, layer_name="Объекты"):
        """Возвращает коллизии объектов и прямоугольники, блокирующие пули."""
        object_rects = []
        bullet_blocking_rects = []

        bullet_passable_gids = self.config.get("bullet_passable_gids", set())
        gid_hitboxes = self.config.get("gid_hitboxes", {})

        try:
            layer = self.tmx_data.get_layer_by_name(layer_name)
        except Exception as e:
            print(f"[❌] Ошибка: слой '{layer_name}' не найден — {e}")
            return [], []

        if not isinstance(layer, pytmx.TiledTileLayer):
            print(f"[❌] Слой '{layer_name}' не является тайловым слоем!")
            return [], []

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
