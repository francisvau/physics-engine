import random
import traceback
from math import inf

import pygame
from pygame.locals import *

from vector2d import Vector2D
from engine import PhysicsWorld, SquareBody

pygame.display.init()
pygame.font.init()
pygame.display.set_caption("Physics Simulation Demo")
font = pygame.font.Font(None, 24)
screen_dims = (1280, 768)
display_surface = pygame.display.set_mode(screen_dims)
frame_timer = pygame.time.Clock()

gravity_strength = 200  # zwaartekracht sterkte
is_gravity_enabled = True
physics_world = PhysicsWorld(gravity=gravity_strength)

spawned_squares = []  # lijst van bestaande squares
green_line_start = Vector2D(screen_dims[0] / 2, 200)  # referentiepunt

for _ in range(30):  # maak 30 willekeurige squares
    while True:
        size = random.randint(30, 100)
        pos_x = random.randint(0, screen_dims[0])
        pos_y = random.randint(0, screen_dims[1])
        rotation = random.randint(0, 360)

        square = SquareBody(size, size, pos_x, pos_y, angle=rotation, mass=inf)

        has_overlap = False
        for existing in spawned_squares:
            collision, _, _ = square.collide(existing)
            if collision:
                has_overlap = True
                break

        distance_from_center = (Vector2D(pos_x, pos_y) - green_line_start).length()
        if distance_from_center < 100:
            has_overlap = True

        if not has_overlap:
            physics_world.add(square)
            spawned_squares.append(square)
            break

green_line_start = Vector2D(screen_dims[0] / 2, 200)
cursor_position = green_line_start


def switch_gravity():
    global is_gravity_enabled, gravity_strength, physics_world
    if is_gravity_enabled:
        physics_world.gravity = 0  # zwaartekracht uitzetten
    else:
        physics_world.gravity = gravity_strength
    is_gravity_enabled = not is_gravity_enabled


def handle_input():
    global cursor_position
    cursor_position = pygame.mouse.get_pos()
    mouse_clicked = pygame.mouse.get_pressed()

    for evt in pygame.event.get():
        if evt.type == QUIT:
            return False
        elif evt.type == KEYDOWN:
            if evt.key == K_ESCAPE:
                return False
            elif evt.key == K_g:
                switch_gravity()
        elif evt.type == MOUSEBUTTONUP and mouse_clicked[0]:
            new_body = SquareBody(20, 20, green_line_start.x, green_line_start.y, angle=random.randint(0, 90))
            physics_world.add(new_body)
            new_body.velocity = Vector2D(cursor_position) - green_line_start
    return True


def render():
    display_surface.fill((50, 50, 50))

    for obj in physics_world.bodies:
        obj.draw(display_surface)

    pygame.draw.line(display_surface, (0, 255, 0), green_line_start, cursor_position, 2)

    actieve_objecten = [obj for obj in physics_world.bodies if obj.mass != inf]
    gravity_status = "ON" if is_gravity_enabled else "OFF"

    display_surface.blit(font.render(f'Gravity: {gravity_status} (Press G)', True, (255, 255, 255)), (10, 10))
    display_surface.blit(font.render(f'Objects: {len(actieve_objecten)}', True, (255, 255, 255)), (10, 40))
    display_surface.blit(font.render(f'FPS: {frame_timer.get_fps():.0f}', True, (255, 255, 255)), (10, 70))
    pygame.display.flip()


def game_loop():
    time_step = 1 / 60
    while True:
        if not handle_input():
            break

        physics_world.update(time_step)

        for obj in physics_world.bodies:
            if obj.position.x < 0 or obj.position.x > screen_dims[0] or obj.position.y < 0 or obj.position.y > screen_dims[1]:
                physics_world.remove(obj)

        render()
        frame_timer.tick(60)
    pygame.quit()


if __name__ == "__main__":
    try:
        game_loop()
    except Exception:
        traceback.print_exc()
        pygame.quit()
        input()
