"""
Set of functions to help pygame
"""


def load_image(image_path):
    from PIL import Image
    from PIL import ImageDraw
    import pygame
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    mode = image.mode
    size = image.size
    data = image.tobytes()
    return pygame.image.fromstring(data, size, mode)


