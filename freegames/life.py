"""Game of Life simulation.

Conway's game of life is a classic cellular automation created in 1970 by John
Conway. https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life

Exercises

1. Can you identify any Still Lifes, Oscillators, or Spaceships?
2. How can you make the simulation faster? Or bigger?
3. How would you modify the initial state?
4. Try changing the rules of life :)
"""
import random
import tkinter.messagebox
from random import choice
from turtle import *

from freegames import square

step_count = 0
last_state = {}
cells = {}
player = {1: [-100, -100], 2: [100, 100]}

player_cells = {}
burst_cells = {}

x_window = 620
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
            burst_cells[x, y] = False

    """Randomly initialize the cells."""
    randomize_patch()

    player_cells[player[1][0], player[1][1]] = True
    player_cells[player[2][0], player[2][1]] = True


def randomize_patch(x_patch=0, y_patch=0):
    for x in range(-x_garden, x_garden, cell_size):
        for y in range(-y_garden, y_garden, cell_size):
            cells[x + x_patch, y - y_patch] = choice([True, False])


def inject_glider_down_right(x, y):
    cells[(x, y+cell_size)] = True
    cells[(x+cell_size, y)] = True
    cells[(x-cell_size, y-cell_size)] = True
    cells[(x, y-cell_size)] = True
    cells[(x+cell_size, y-cell_size)] = True

def inject_glider_down_left(x, y):
    cells[(x, y-cell_size)] = True
    cells[(x+cell_size, y)] = True
    cells[(x-cell_size, y-cell_size)] = True
    cells[(x-cell_size, y)] = True
    cells[(x-cell_size, y+cell_size)] = True

def inject_glider_up_left(x, y):
    cells[(x, y-cell_size)] = True
    cells[(x-cell_size, y)] = True
    cells[(x-cell_size, y+cell_size)] = True
    cells[(x, y+cell_size)] = True
    cells[(x+cell_size, y+cell_size)] = True

def inject_glider_up_right(x, y):
    cells[(x, y+cell_size)] = True
    cells[(x-cell_size, y)] = True
    cells[(x+cell_size, y-cell_size)] = True
    cells[(x+cell_size, y)] = True
    cells[(x+cell_size, y+cell_size)] = True

class game:
    def __init__(self):
        self.step_count = 0
        setup(x_window, y_window, 1*370, 200)
        # speed(1)
        hideturtle()
        tracer(False)
        initialize()
        self.player_1_score = 0
        self.player_2_score = 0

    def move(self, player_number, dx, dy):
        player_cells[player[player_number][0], player[player_number][1]] = False
        player[player_number][0] = min(max(-x_field, player[player_number][0] + dx*cell_size), x_field-1*cell_size)
        player[player_number][1] = min(max(-y_field, player[player_number][1] - dy*cell_size), y_field-1*cell_size)
        player_cells[player[player_number][0], player[player_number][1]] = True

    def step(self):
        """Compute one step in the Game of Life."""
        neighbors = {}
        game_over = False
        if not player[1] and not player[2]:
            game_over = True


        for x in range(-190, 190, cell_size):
            for y in range(-190, 190, cell_size):
                count = -cells[x, y]
                burst_cells[x, y] = False
                for h in [-10, 0, cell_size]:
                    for v in [-10, 0, cell_size]:
                        count += cells[x + h, y + v]
                neighbors[x, y] = count


        for cell, count in neighbors.items():
            if cells[cell]:
                if count < 2 or count > 3:
                    cells[cell] = False
                    burst_cells[cell] = True
                    if player_cells[cell]:
                        if list(cell) == player[1]:
                            player[1] = None
                        if list(cell) == player[2]:
                            player[2] = None
                    #     print("GAME OVER")
                    #     print(f"SORE {self.step_count}")
                    #     game_over = True


            elif count == 3:
                cells[cell] = True

        if self.step_count%50 == 10:
            inject_glider_up_right(-x_field+40, -y_field+40)
            inject_glider_up_left(x_field-40, -y_field+40)
            inject_glider_down_right(-x_field+40, y_field-40)
            inject_glider_down_left(x_field-40, y_field-40)

        if self.step_count%10 == 5:
            randomize_patch(random.choice([-x_garden-60, 0, x_garden+60]),
                            random.choice([-y_garden-60, 0, y_garden+60]))

        if game_over:
            return False
        return True

    def report_scores(self, player_number):
        """Display `text` at coordinates `x` and `y`."""
        if player_number == 1:
            square(-x_window / 2 + 30, y_window/2-30, 10, 'white')
            color('Blue')
            write(f"Score {self.player_1_score}", font=('Arial', 10, 'normal'))

        if player_number == 2:
            square(x_window / 2 - 80, y_window/2-30, 10, 'white')
            color('Orange')
            write(f"Score {self.player_2_score}", font=('Arial', 10, 'normal'))

    def draw(self):

        """Draw all the squares."""
        self.step_count += 1
        if player[1]:
            self.player_1_score += 1
        if player[2]:
            self.player_2_score += 1

        if self.step_count % 10 == 0:
            print(f"Step {self.step_count}")

        live_game = self.step()
        clear()

        for (x, y), alive in cells.items():

            if player_cells[(x, y)] and [x, y] == player[1]:
                square(x, y, cell_size, 'blue')
                if alive:
                    self.player_1_score += 1
            elif player_cells[(x, y)] and [x, y] == player[2]:
                square(x, y, cell_size, 'orange')
                if alive:
                    self.player_2_score += 1
            elif burst_cells[(x, y)]:
                square(x, y, cell_size, 'red')
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

        self.report_scores(1)
        self.report_scores(2)

        update()


        if not live_game:
            if self.player_1_score>self.player_2_score:
                tkinter.messagebox.showinfo("Game Over!", f"Blue Wins!\nScore {self.player_1_score}")
            if self.player_1_score<self.player_2_score:
                tkinter.messagebox.showwarning("Game Over!", f"Orange Wins!\nScore {self.player_2_score}")
            if self.player_1_score == self.player_2_score:
                tkinter.messagebox.showerror("Game Over!", f"Tie Game!\nScore {self.player_1_score}")
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

    onkey(lambda: game.move(2, 0, -1), 'Up')
    onkey(lambda: game.move(2, 0, 1), 'Down')
    onkey(lambda: game.move(2, -1, 0), 'Left')
    onkey(lambda: game.move(2, 1, 0), 'Right')



    while living_game:

        if not game.draw():
            break
    done()
