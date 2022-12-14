import collections
import os
import sys
import timeit
from enum import Enum
from multiprocessing import cpu_count, Pool

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
        self.trash_pos = (window_width - size[0] - 5, self.pos_y)

        def init_button(path, pos, _size):
            return pygame.Rect(pos[0], pos[1], _size[0], _size[1]), pygame.transform.scale(pygame.image.load(path), _size)

        self.play_pause_rect, self.play_icon = init_button(os.path.join("play.png"), self.play_pause_pos, size)
        _, self.pause_icon = init_button(os.path.join("pause.png"), self.play_pause_pos, size)
        self.next_rect, self.next_icon = init_button(os.path.join("angle-right.png"), self.next_pos, size)
        self.previous_rect, self.previous_icon = init_button(os.path.join("angle-left.png"), self.previous_pos, size)
        self.refresh_rect, self.refresh_icon = init_button(os.path.join("refresh.png"), self.refresh_pos, size)
        self.trash_rect, self.trash_icon = init_button(os.path.join("trash.png"), self.trash_pos, size)

    def draw(self, game_running):
        pygame.draw.rect(self.surface, (255, 255, 255), self.play_pause_rect)
        pygame.draw.rect(self.surface, (255, 255, 255), self.next_rect)
        pygame.draw.rect(self.surface, (255, 255, 255), self.previous_rect)
        pygame.draw.rect(self.surface, (255, 255, 255), self.refresh_rect)
        pygame.draw.rect(self.surface, (255, 255, 255), self.trash_rect)

        self.surface.blit(self.pause_icon if game_running else self.play_icon, self.play_pause_pos)
        self.surface.blit(self.next_icon, self.next_pos)
        self.surface.blit(self.previous_icon, self.previous_pos)
        self.surface.blit(self.refresh_icon, self.refresh_pos)
        self.surface.blit(self.trash_icon, self.trash_pos)

    def next_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.next_rect.collidepoint(event.pos)

    def refresh_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.refresh_rect.collidepoint(event.pos)

    def play_pause_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.play_pause_rect.collidepoint(event.pos)

    def previous_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.previous_rect.collidepoint(event.pos)

    def trash_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.trash_rect.collidepoint(event.pos)


@click.command()
@click.option("--cell-size", default=10)
@click.option("--col", default=100)
@click.option("--row", default=100)
@click.option("--all-cores", is_flag=True, default=False, help="Uses all cores for calculation. If this flag is passed, the --col option will be rounded down, "
                                                               "to a multiple of you cpu core count to give each process the same chunk size")
@click.option("--processes-per-core", default=1)
def conway(cell_size, col, row, all_cores, processes_per_core):
    pygame.init()
    pygame.display.set_caption("John Conway's Game of Life")

    pool = None
    if all_cores:
        print(f"Using {cpu_count()} cores, with {processes_per_core} process per core")
        processes = cpu_count() * processes_per_core
        print(f"original dimensions: {row}/{col}")
        col = int(col / processes) * processes
        print(f"adjusted dimensions: {row}/{col}")
        pool = Pool(processes)

    print(f"{row} * {col} = {row * col} pixels")

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
    next_state_hold = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                continue
            elif controls.next_clicked(event):
                run_game = True
                next_state_hold = True
            elif next_state_hold and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                run_game = False
                next_state_hold = False
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
            elif controls.trash_clicked(event):
                matrix = np.zeros((col, row))
                matrix_history = collections.deque()
                draw_matrix(matrix, cell_size, surface)
            elif event.type == pygame.MOUSEBUTTONDOWN and 0 < event.pos[1] < cell_size * row and 0 < event.pos[0] < cell_size * col:
                x, y = event.pos
                x = int((x - 1) / cell_size)
                y = int((y - 1) / cell_size)
                matrix[x, y] = 1 - matrix[x, y]
                draw_matrix(matrix, cell_size, surface)
            elif event.type == pygame.QUIT:
                if pool:
                    pool.close()
                pygame.quit()
                sys.exit()

        if run_game:
            if not matrix_history:
                matrix_history.append(matrix)
            elif not np.array_equal(matrix, matrix_history[-1]):
                matrix_history.append(matrix)

            start = timeit.default_timer()
            if all_cores:
                args = [(matrix, _id, processes) for _id in range(processes)]
                new_matrices = pool.starmap(next_generation, args)
                matrix = np.concatenate(new_matrices)
            else:
                matrix = next_generation(matrix, 0, 1)
            print(timeit.default_timer() - start)

            draw_matrix(matrix, cell_size, surface)

        elif previous_state and matrix_history:
            matrix = matrix_history.pop()
            draw_matrix(matrix, cell_size, surface)
            pygame.time.delay(100)

        controls.draw(run_game and not next_state_hold)
        pygame.display.update()


def next_generation(matrix, process_id, process_count):
    matrix_part_length = int(matrix.shape[0] / process_count)

    matrix_new = np.zeros((matrix_part_length, matrix.shape[1]), dtype=int)
    for x, y in np.ndindex(matrix_part_length, matrix.shape[1]):
        x_of_part = x + process_id * matrix_part_length

        sum_x_lower = x_of_part - 1 if x_of_part > 0 else x_of_part
        sum_y_lower = y - 1 if y > 0 else y

        alive_neighbours = np.sum(matrix[sum_x_lower:x_of_part + 2, sum_y_lower:y + 2]) - matrix[x_of_part, y]

        if matrix[x_of_part, y] == 1 and alive_neighbours < 2 or alive_neighbours > 3:
            matrix_new[x, y] = 0
        elif alive_neighbours == 3 or (matrix[x_of_part, y] == 1 and (2 == alive_neighbours or alive_neighbours == 3)):
            matrix_new[x, y] = 1

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
