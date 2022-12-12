import sys
from enum import Enum

import click
import numpy as np
import pygame

grid_color = (30, 30, 60)


class State(Enum):
    alive = (255, 255, 215)
    about_to_die = (200, 200, 225)
    dead = (10, 10, 40)


def init_rand(col, row):
    return np.random.randint(0, 2, size=(col, row))


def init_slider(col, row):
    matrix = np.zeros((col, row))
    pattern = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0,
                         0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0,
                         0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                         0, 0, 1, 1, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                         0, 0, 1, 1, 0, 0, 0],
                        [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                         0, 0, 0, 0, 0, 0, 0],
                        [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0,
                         0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0,
                         0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                         0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                         0, 0, 0, 0, 0, 0, 0]])
    pos = (3, 3)
    matrix[pos[0]:pos[0] + pattern.shape[0], pos[1]:pos[1] + pattern.shape[1]] = pattern
    return matrix


@click.command()
@click.option("--cell-size", default=10)
@click.option("--col", default=100)
@click.option("--row", default=100)
def conway(cell_size, col, row):
    pygame.init()
    pygame.display.set_caption("John Conway's Game of Life")
    button = pygame.Rect(10, 10, 50, 50)

    surface = pygame.display.set_mode((col * cell_size + 1, row * cell_size + 1))
    matrix = init_rand(col, row)

    surface.fill(grid_color)
    for x, y in np.ndindex(matrix.shape):
        pygame.draw.rect(surface, State.alive.value if matrix[x, y] else State.dead.value,
                         pygame.Rect(x * cell_size + 1, y * cell_size + 1, cell_size - 1, cell_size - 1))

    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and button.collidepoint(event.pos):
                surface.fill(grid_color)
                matrix_new = np.zeros((col, row), dtype=int)

                for x, y in np.ndindex(matrix.shape):
                    alive_neighbours = np.sum(matrix[x - 1:x + 2, y - 1:y + 2]) - matrix[x, y]

                    if matrix[x, y] == 1 and alive_neighbours < 2 or alive_neighbours > 3:
                        matrix_new[x, y] = 0
                    elif alive_neighbours == 3 or (
                            matrix[x, y] == 1 and (2 == alive_neighbours or alive_neighbours == 3)):
                        matrix_new[x, y] = 1

                    pygame.draw.rect(surface, State.alive.value if matrix_new[x, y] else State.dead.value,
                                     pygame.Rect(x * cell_size + 1, y * cell_size + 1, cell_size - 1, cell_size - 1))
                pygame.display.update()
                matrix = matrix_new


if __name__ == "__main__":
    conway()
