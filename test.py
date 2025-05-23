from PIL import Image, ImageDraw

# Открытие изображения
image_path = "C:/Users/Victus/Desktop/Project_2/Maps/Sprite_for_Cart_Game.png"
image = Image.open(image_path)
draw = ImageDraw.Draw(image)

# Размеры тайла
tile_width = 64
tile_height = 64

# Проведение вертикальных линий
for x in range(0, image.width, tile_width):
    draw.line(((x, 0), (x, image.height)), fill="red", width=1)

# Проведение горизонтальных линий
for y in range(0, image.height, tile_height):
    draw.line(((0, y), (image.width, y)), fill="red", width=1)

# Сохранение изображения
grid_image_path = "C:/Users/Victus/Desktop/Project_2/Maps/Sprite_with_grid.png"
image.save(grid_image_path)

grid_image_path
