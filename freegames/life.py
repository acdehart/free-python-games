"""Game of Life simulation.

Conway's game of life is a classic cellular automation created in 1970 by John
Conway. https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life

Exercises

1. Can you identify any Still Lifes, Oscillators, or Spaceships?
2. How can you make the simulation faster? Or bigger?
3. How would you modify the initial state?
4. Try changing the rules of life :)
"""
import tkinter.messagebox
from random import choice
from turtle import *

from freegames import square

step_count = 0
last_state = {}
cells = {}
player = {1: [-180, -180], 2: [10, 0]}
player_cells = {}

x_window = 420
y_window = 420

x_field = 200
y_field = x_field

x_garden = 50
y_garden = x_garden

cell_size = 10


def initialize():
    """Start with all cells Off"""
    for x in range(-x_field, x_field, cell_size):
        for y in range(-y_field, y_field, cell_size):
            cells[x, y] = False
            player_cells[x, y] = False

    """Randomly initialize the cells."""
    for x in range(-x_garden, x_garden, cell_size):
        for y in range(-y_garden, y_garden, cell_size):
            cells[x, y] = choice([True, False])

    player_cells[player[1][0], player[1][1]] = True


class game:
    def __init__(self):
        self.step_count = 0
        setup(x_window, y_window, 4 * 370, 0)
        # speed(1)
        hideturtle()
        tracer(False)
        initialize()

    def move(self, player_number, dx, dy):
        player_cells[player[player_number][0], player[player_number][1]] = False
        player[player_number][0] = min(max(-x_field, player[player_number][0] + dx*cell_size), x_field-1*cell_size)
        player[player_number][1] = min(max(-y_field, player[player_number][1] - dy*cell_size), y_field-1*cell_size)
        player_cells[player[player_number][0], player[player_number][1]] = True

    def step(self):
        """Compute one step in the Game of Life."""
        neighbors = {}
        game_over = False

        for x in range(-190, 190, cell_size):
            for y in range(-190, 190, cell_size):
                count = -cells[x, y]
                for h in [-10, 0, cell_size]:
                    for v in [-10, 0, cell_size]:
                        count += cells[x + h, y + v]
                neighbors[x, y] = count

        for cell, count in neighbors.items():
            if cells[cell]:
                if count < 2 or count > 3:
                    cells[cell] = False
                    if player_cells[cell]:
                        print("GAME OVER")
                        print(f"SORE {self.step_count}")
                        game_over = True


            elif count == 3:
                cells[cell] = True

        if game_over:
            return False
        return True

    def draw(self):

        """Draw all the squares."""
        self.step_count += 1
        if self.step_count % 10 == 0:
            print(f"Step {self.step_count}")
        live_game = self.step()
        clear()

        for (x, y), alive in cells.items():
            if player_cells[(x, y)]:
                square(x, y, cell_size, 'blue')
            elif alive:
                square(x, y, cell_size, 'green')
            else:
                square(x, y, cell_size, 'black')

        # for (x, y), alive in player.items():
        #     if alive:
        #         square(x, y, cell_size, 'blue')

        # cells[(0, 0)] = True
        # square(0, 0, 10, 'blue')

        """Set Characters"""

        update()

        if not live_game:
            tkinter.messagebox.showerror("Game Over!", f"Score {self.step_count}")
            return None

        ontimer(self.draw(), 100)


if __name__ == "__main__":
    living_game = True

    game = game()
    listen()
    onkey(lambda: game.move(1, 0, -1), 'w')
    onkey(lambda: game.move(1, 0, 1), 's')
    onkey(lambda: game.move(1, -1, 0), 'a')
    onkey(lambda: game.move(1, 1, 0), 'd')
    while living_game:

        if not game.draw():
            break
    done()
