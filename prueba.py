import pyglet
from PIL import Image
import pygame

impil = Image.open("Tarea3\cat.png").tobytes()
impygame = pygame.image.load("Tarea3\cat.png")
impygame = pygame.image.tostring(impygame,"RGBA")
impyglet = pyglet.image.load("Tarea3\cat.png").get_image_data()
impyglet = impyglet.get_data("RGBA", impyglet.width * len(impyglet.format))

print(type(impyglet))
print(type((impil)))
print(type(impygame))
print(impil == impygame and impygame == impyglet)