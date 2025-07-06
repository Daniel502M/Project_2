tile_map = TileMap("Maps/Lawn_Cart/Lawn_Cart.tmx")
static_obstacles, door_obstacles = tile_map.get_collision_rects()
object_obstacles, _ = tile_map.get_object_collision_rects()

door_spritesheet = pygame.image.load("Maps/Lawn_Cart/Sprite_for_Lawn_Cart.png").convert_alpha()
SPRITE_SIZE = 64
door_gids = {
    15: ("top", 0, 0),
    20: ("bottom", 64, 0),
    12: ("right", 128, 0),
    13: ("left", 192, 0),
}