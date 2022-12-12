import collections
import os
import sys
from enum import Enum

import click
import numpy as np
import pygame

grid_color = (30, 30, 60)


class State(Enum):
    alive = (255, 255, 215)
    dead = (10, 10, 40)


class Controls:

    def __init__(self, surface, window_width, window_height, size) -> None:
        self.surface = surface
        self.offset = size[0] + 5

        self.pos_x = window_width / 2 - self.offset * 2
        self.pos_y = window_height

        self.play_pause_pos = (self.pos_x, self.pos_y)
        self.previous_pos = (self.pos_x + 1 * self.offset, self.pos_y)
        self.next_pos = (self.pos_x + 2 * self.offset, self.pos_y)
        self.refresh_pos = (self.pos_x + 3 * self.offset, self.pos_y)

        def init_button(path, pos, _size):
            return pygame.Rect(pos[0], pos[1], _size[0], _size[1]), pygame.transform.scale(pygame.image.load(path), _size)

        self.play_pause_rect, self.play_icon = init_button(os.path.join("play.png"), self.play_pause_pos, size)
        _, self.pause_icon = init_button(os.path.join("pause.png"), self.play_pause_pos, size)
        self.next_rect, self.next_icon = init_button(os.path.join("angle-right.png"), self.next_pos, size)
        self.previous_rect, self.previous_icon = init_button(os.path.join("angle-left.png"), self.previous_pos, size)
        self.refresh_rect, self.refresh_icon = init_button(os.path.join("refresh.png"), self.refresh_pos, size)

    def draw(self, game_running):
        pygame.draw.rect(self.surface, (255, 255, 255), self.play_pause_rect)
        pygame.draw.rect(self.surface, (255, 255, 255), self.next_rect)
        pygame.draw.rect(self.surface, (255, 255, 255), self.previous_rect)
        pygame.draw.rect(self.surface, (255, 255, 255), self.refresh_rect)

        self.surface.blit(self.play_icon if game_running else self.pause_icon, self.play_pause_pos)
        self.surface.blit(self.next_icon, self.next_pos)
        self.surface.blit(self.previous_icon, self.previous_pos)
        self.surface.blit(self.refresh_icon, self.refresh_pos)

    def next_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.next_rect.collidepoint(event.pos)

    def refresh_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.refresh_rect.collidepoint(event.pos)

    def play_pause_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.play_pause_rect.collidepoint(event.pos)

    def previous_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.previous_rect.collidepoint(event.pos)


@click.command()
@click.option("--cell-size", default=10)
@click.option("--col", default=100)
@click.option("--row", default=100)
def conway(cell_size, col, row):
    pygame.init()
    pygame.display.set_caption("John Conway's Game of Life")
    width = col * cell_size + 1
    height = row * cell_size + 1

    surface = pygame.display.set_mode((width, height + 50))
    controls = Controls(surface, width, height, (50, 50))

    matrix = generate_start(cell_size, col, row, surface)
    matrix_history = collections.deque(maxlen=100)

    controls.draw(False)
    pygame.display.update()

    run_game = False
    previous_state = False
    next_state = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                continue
            elif controls.next_clicked(event):
                run_game = True
                next_state = True
            elif next_state and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                run_game = False
                next_state = False
            elif controls.refresh_clicked(event):
                matrix = generate_start(cell_size, col, row, surface)
                run_game = False
            elif controls.play_pause_clicked(event):
                run_game = not run_game
            elif controls.previous_clicked(event):
                run_game = False
                previous_state = True
            elif previous_state and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                previous_state = False
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if run_game:
            matrix_history.append(matrix)
            matrix = next_generation(cell_size, col, matrix, row, surface)
        elif previous_state and matrix_history:
            matrix = matrix_history.pop()
            draw_matrix(matrix, cell_size, surface)
            pygame.time.delay(100)

        controls.draw(run_game and not next_state)
        pygame.display.update()


def next_generation(cell_size, col, matrix, row, surface):
    surface.fill(grid_color)
    matrix_new = np.zeros((col, row), dtype=int)
    for x, y in np.ndindex(matrix.shape):

        sum_x_lower = x - 1 if x > 0 else x
        sum_y_lower = y - 1 if y > 0 else y

        alive_neighbours = np.sum(matrix[sum_x_lower:x + 2, sum_y_lower:y + 2]) - matrix[x, y]

        if matrix[x, y] == 1 and alive_neighbours < 2 or alive_neighbours > 3:
            matrix_new[x, y] = 0
        elif alive_neighbours == 3 or (
                matrix[x, y] == 1 and (2 == alive_neighbours or alive_neighbours == 3)):
            matrix_new[x, y] = 1

        pygame.draw.rect(surface, State.alive.value if matrix_new[x, y] else State.dead.value, pygame.Rect(x * cell_size + 1, y * cell_size + 1, cell_size - 1, cell_size - 1))
    return matrix_new


def generate_start(cell_size, col, row, surface):
    matrix = np.random.randint(0, 2, size=(col, row))
    draw_matrix(matrix, cell_size, surface)
    return matrix


def draw_matrix(matrix, cell_size, surface):
    surface.fill(grid_color)
    for x, y in np.ndindex(matrix.shape):
        pygame.draw.rect(surface, State.alive.value if matrix[x, y] else State.dead.value, pygame.Rect(x * cell_size + 1, y * cell_size + 1, cell_size - 1, cell_size - 1))


if __name__ == "__main__":
    conway()
