"""Game of Life simulation.

Conway's game of life is a classic cellular automation created in 1970 by John
Conway. https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life

Exercises

1. Can you identify any Still Lifes, Oscillators, or Spaceships?
2. How can you make the simulation faster? Or bigger?
3. How would you modify the initial state?
4. Try changing the rules of life :)
"""
import beepy as beep
import os
import winsound
import random
import sys
import tkinter.messagebox
from random import choice
from turtle import *

from freegames import square

x_window = 660
y_window = 420

x_field = 200
y_field = x_field

x_garden = 50
y_garden = x_garden

cell_size = 10


class player:
    def __init__(self, id):
        self.alive = True
        self.score = 0
        self.lives = 'III'

        if id == 1:
            self.color = 'blue'
            self.pos = [-100, -100]
            self.text = [-320, 140]

        if id == 2:
            self.color = 'orange'
            self.pos = [100, 100]
            self.text = [208, 140]


class game:
    def __init__(self, number_of_players):
        self.verbose = True
        self.damage = False
        self.ding = False
        self.num_of_players = number_of_players
        self.step_count = 0
        setup(x_window, y_window, 1*370, 200)
        # speed(1)
        hideturtle()
        tracer(False)
        square(-150, -10, cell_size, 'white')
        color('Black')
        write(f"Game of Life", font=('Arial', 40, 'bold'))
        self.players = {}
        self.cells = {}
        self.player_cells = {}
        self.burst_cells = {}
        self.initialize()

        if self.verbose:
            beep.beep(1)
        # frequency = 2500  # Set Frequency To 2500 Hertz
        # duration = 1000  # Set Duration To 1000 ms == 1 second
        # winsound.Beep(frequency, duration)

    def initialize(self):
        """Start with all cells Off"""
        for x in range(-x_field, x_field, cell_size):
            for y in range(-y_field, y_field, cell_size):
                self.cells[x, y] = False
                self.player_cells[x, y] = False
                self.burst_cells[x, y] = False

        for id in range(1, self.num_of_players + 1):
            self.players[id] = player(id)
            self.player_cells[self.players[id].pos[0], self.players[id].pos[1]] = True

        """Randomly initialize the cells."""
        self.randomize_patch()

    def close(self):
        """Need method to close app"""
        print("I am nothing")
        # self = None

    def inject_glider_down_right(self, x, y):
        self.cells[(x, y + cell_size)] = True
        self.cells[(x + cell_size, y)] = True
        self.cells[(x - cell_size, y - cell_size)] = True
        self.cells[(x, y - cell_size)] = True
        self.cells[(x + cell_size, y - cell_size)] = True

    def inject_glider_down_left(self, x, y):
        self.cells[(x, y - cell_size)] = True
        self.cells[(x + cell_size, y)] = True
        self.cells[(x - cell_size, y - cell_size)] = True
        self.cells[(x - cell_size, y)] = True
        self.cells[(x - cell_size, y + cell_size)] = True

    def inject_glider_up_left(self, x, y):
        self.cells[(x, y - cell_size)] = True
        self.cells[(x - cell_size, y)] = True
        self.cells[(x - cell_size, y + cell_size)] = True
        self.cells[(x, y + cell_size)] = True
        self.cells[(x + cell_size, y + cell_size)] = True

    def inject_glider_up_right(self, x, y):
        self.cells[(x, y + cell_size)] = True
        self.cells[(x - cell_size, y)] = True
        self.cells[(x + cell_size, y - cell_size)] = True
        self.cells[(x + cell_size, y)] = True
        self.cells[(x + cell_size, y + cell_size)] = True

    def move(self, id, dx, dy):
        self.player_cells[self.players[id].pos[0], self.players[id].pos[1]] = False
        self.players[id].pos[0] = min(max(-x_field+1*cell_size, self.players[id].pos[0] + dx * cell_size), x_field - 2 * cell_size)
        self.players[id].pos[1] = min(max(-y_field+1*cell_size, self.players[id].pos[1] - dy * cell_size), y_field - 2 * cell_size)
        self.player_cells[self.players[id].pos[0], self.players[id].pos[1]] = True

    def step(self):
        """Compute one step in the Game of Life."""
        neighbors = {}
        game_over = False

        if len(self.players) == 1:
            if not self.players[1].alive:
                game_over = True
        else:
            if not self.players[1].alive and self.players[2].score > self.players[1].score:
                game_over = True
            if not self.players[2].alive and self.players[2].score < self.players[1].score:
                game_over = True
            if not self.players[1].alive and not self.players[2].alive:
                game_over = True

        for x in range(-x_field+10, x_field-10, cell_size):
            for y in range(-y_field+10, y_field-10, cell_size):
                count = -self.cells[x, y]
                self.burst_cells[x, y] = False
                for h in [-cell_size, 0, cell_size]:
                    for v in [-cell_size, 0, cell_size]:
                        count += self.cells[x + h, y + v]
                neighbors[x, y] = count

        for cell, count in neighbors.items():
            if self.cells[cell]:
                if count < 2 or count > 3:
                    self.cells[cell] = False
                    self.burst_cells[cell] = True
                    for id in self.players:
                        if self.player_cells[cell]:
                            if list(cell) == self.players[id].pos and self.players[id].alive:
                                self.damage = True
                                if self.players[id].lives:
                                    self.players[id].lives = self.players[id].lives[:-1]
                                else:
                                    self.players[id].alive = False
                                print(f"Player {id} | {self.players[id].lives} with score {self.players[id].score}")

                    #     print("GAME OVER")
                    #     print(f"SORE {self.step_count}")
                    #     game_over = True

            elif count == 3:
                self.cells[cell] = True

        if self.step_count % 50 == 10:
            self.inject_glider_up_right(-x_field+40, -y_field+40)
            self.inject_glider_up_left(x_field-40, -y_field+40)
            self.inject_glider_down_right(-x_field+40, y_field-40)
            self.inject_glider_down_left(x_field-40, y_field-40)

        if self.step_count % 10 == 5:
            self.randomize_patch(random.choice([-x_garden-60, 0, x_garden+60]),
                                 random.choice([-y_garden-60, 0, y_garden+60]))

        if game_over:
            self.close()
            return False
        return True

    def report_scores(self):
        """Display `text` at coordinates `x` and `y`."""

        for id in self.players:
            square(self.players[id].text[0], self.players[id].text[1], cell_size, 'white')
            color(self.players[id].color)
            write(f"Score {self.players[id].score}\nLives {self.players[id].lives}", font=('Arial', 20, 'normal'))
        #
        # if player_number == 2:
        #     square(x_window / 2 - 80, y_window/2-60, 10, 'white')
        #     color('Orange')
        #     write(f"Score {self.player_2_score}\nLives {self.player_2_lives}", font=('Arial', 20, 'normal'))

    def randomize_patch(self, x_patch=0, y_patch=0):
        for x in range(-x_garden, x_garden, cell_size):
            for y in range(-y_garden, y_garden, cell_size):
                self.cells[x + x_patch, y - y_patch] = choice([True, False])

    def draw(self):

        """Draw all the squares."""
        self.step_count += 1

        if self.step_count % 10 == 0:
            for id in self.players:
                if self.players[id].alive:
                    self.players[id].score += 1
            beep.beep(1)
            print(f"Step {self.step_count}")

        live_game = self.step()
        clear()

        for (x, y), alive in self.cells.items():
            if self.burst_cells[(x, y)]:
                square(x, y, cell_size, 'red')
            elif alive:
                square(x, y, cell_size, 'green')
            else:
                square(x, y, cell_size, 'black')

            for id in self.players:
                if self.player_cells[(x, y)] and [x, y] == self.players[id].pos and self.players[id].alive:
                    square(x, y, cell_size, self.players[id].color)
                    if alive:
                        self.players[id].score += 1
                        self.ding = True

        if self.ding:
            self.ding = False
            beep.beep(1)

        """Set Characters"""

        self.report_scores()
        if self.verbose and self.damage:
            self.damage = False
            beep.beep(3)

        update()

        if not live_game:
            beep.beep(5)
            if len(self.players) == 1:
                tkinter.messagebox.showinfo("Game Over!", f"Good Job!\nScore {self.players[1].score}")
            else:
                if self.players[1].score > self.players[2].score:
                    tkinter.messagebox.showinfo("Game Over!", f"Blue Wins!\nScore {self.players[1].score}")
                if self.players[1].score < self.players[2].score:
                    tkinter.messagebox.showwarning("Game Over!", f"Orange Wins!\nScore {self.players[2].score}")
                if self.players[1].score == self.players[2].score:
                    tkinter.messagebox.showerror("Game Over!", f"Tie Game!\nScore {self.players[1].score}")
            return None

        ontimer(self.draw(), 100)


def setup_keys():
    listen()
    onkey(lambda: game.move(1, 0, -1), 'w')
    onkey(lambda: game.move(1, 0, 1), 's')
    onkey(lambda: game.move(1, -1, 0), 'a')
    onkey(lambda: game.move(1, 1, 0), 'd')
    onkey(lambda: game.move(2, 0, -1), 'Up')
    onkey(lambda: game.move(2, 0, 1), 'Down')
    onkey(lambda: game.move(2, -1, 0), 'Left')
    onkey(lambda: game.move(2, 1, 0), 'Right')
    onkey(lambda: game.close(), 'Escape')


if __name__ == "__main__":
    living_game = True

    game = game(2)

    setup_keys()

    while living_game:

        if not game.draw():
            break
    done()
