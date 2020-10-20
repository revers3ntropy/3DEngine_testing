import pygame as py
import time

import global_data
import renderer

import vector


def tick():
    start_time = time.time()

    # user input
    keys = py.key.get_pressed()

    try:
        fps_mod = 1 / global_data.fps
    except ZeroDivisionError:
        fps_mod = 10

    # movement
    forwards_movement = vector.multiply(global_data.camera_look_direction, global_data.camera_movement_speed * fps_mod)

    if keys[py.K_SPACE]:
        global_data.camera_position.y -= global_data.camera_movement_speed * fps_mod
    if keys[py.K_LSHIFT]:
        global_data.camera_position.y += global_data.camera_movement_speed * fps_mod

    if keys[py.K_d]:
        global_data.camera_position.x += global_data.camera_movement_speed * fps_mod
    if keys[py.K_a]:
        global_data.camera_position.x -= global_data.camera_movement_speed * fps_mod

    if keys[py.K_w]:
        global_data.camera_position = vector.add(global_data.camera_position, forwards_movement)
    if keys[py.K_s]:
        print(global_data.camera_position.z)
        global_data.camera_position = vector.subtract(global_data.camera_position, forwards_movement)

    # looking
    if keys[py.K_LEFT]:
        global_data.yaw += global_data.camera_movement_speed * fps_mod / 4
    if keys[py.K_RIGHT]:
        global_data.yaw -= global_data.camera_movement_speed * fps_mod / 4

    renderer.pygame_tick()

    renderer.draw_mesh(global_data.cube.triangles)

    global_data.tick += 1
    global_data.fps = round(1 / (time.time() - start_time), 1)
    if global_data.tick % 10 == 0:
        py.display.set_caption(f'FPS: {global_data.fps}')


while True:
    tick()
