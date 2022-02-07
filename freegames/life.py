"""Game of Life simulation.

Conway's game of life is a classic cellular automation created in 1970 by John
Conway. https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life

Exercises

1. Can you identify any Still Lifes, Oscillators, or Spaceships?
2. How can you make the simulation faster? Or bigger?
3. How would you modify the initial state?
4. Try changing the rules of life :)
"""
import pickle

RADIUS = 2
PLAYERS = 2
VERBOSE = False
PLAYER_WINNERS = []
PKL_PATH = f'gladiators_r{RADIUS}.pkl'

from threading import Thread
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

x_corner = 1350
y_corner = 0

x_field = 200
y_field = x_field

x_garden = 50
y_garden = x_garden

cell_size = 10


def count_wins(color):
    color_wins = 0
    for player in PLAYER_WINNERS:
        if player.color == color:
            color_wins += 1
    return color_wins


class player:
    def __init__(self, id):
        self.alive = True
        self.score = 0
        self.lives = 'III'
        self.decission = None
        self.prev_decission = None
        self.memory = {} # Key env state # Val prev decision: point change

        if id == 1:
            self.color = 'blue'
            self.pos = [-100, -100]
            self.text = [-320, 110]
            self.weights = [.92, .02, .02, .02, .02]

        if id == 2:
            self.color = 'orange'
            self.pos = [100, 100]
            self.text = [208, 110]
            self.weights = [.2, .2, .2, .2, .2]

    def remember_valhala(self, points, env, env_1):
        """Reinforce (+) moments before scoring points"""
        """Penalize (-) moments before losing points"""
        feature_list = self.get_memory_list(env_1, points)
        self.weights = self.get_action_weights(feature_list)
        self.memory[tuple(feature_list)] = self.prev_decission

    def get_memory_list(self, env_1, points):
        feature_list = []  # i component when up/down, no i when l/r
        for x in range(self.pos[0] - RADIUS * cell_size, self.pos[0] + (1 + RADIUS) * cell_size, 10):
            for y in range(self.pos[1] - RADIUS * cell_size, self.pos[1] + (1 + RADIUS) * cell_size, 10):
                if abs(x) < x_field-1*cell_size and abs(y) < y_field-1*cell_size:
                    feature_list.append(int(env_1[(x, y)]) * points)
                else:
                    feature_list.append(0)
        return feature_list

    def get_action_weights(self, feature_list):
        """TODO: Forward Pass in Network and update weights"""

        return self.weights


class game:
    def __init__(self, number_of_players, verbose):
        self.verbose = verbose
        self.living = True
        self.damage = False
        self.ding = False
        self.num_of_players = number_of_players
        self.step_count = 0
        setup(x_window, y_window, x_corner, y_corner)
        hideturtle()
        tracer(False)
        self.players = {}
        self.cells = {}
        self.prev_cells = {}
        self.player_cells = {}
        self.border_cells = {}
        self.burst_cells = {}
        self.initialize()

        if self.verbose:
            b = Thread(beep.beep(2))
            b.start()

    def get_best_player(self):
        if self.num_of_players == 1:
            return self.players[1].score
        else:
            if self.players[1].score >= self.players[2].score:
                return self.players[1]
            else:
                return self.players[2]

    def initialize(self):
        """Start with all cells Off"""
        for x in range(-x_field, x_field, cell_size):
            for y in range(-y_field, y_field, cell_size):
                self.cells[x, y] = False
                self.prev_cells[x, y] = False
                self.player_cells[x, y] = False
                self.burst_cells[x, y] = False
                self.border_cells[x, y] = False
                if x == abs(x_field-10) or y == abs(y_field-10) or \
                        x == -x_field or y == -y_field:
                    self.border_cells[x, y] = True

        for id in range(1, self.num_of_players + 1):
            self.players[id] = player(id)
            self.player_cells[self.players[id].pos[0], self.players[id].pos[1]] = True

        """Randomly initialize the cells."""
        self.randomize_patch()

    def close(self):
        """Need method to close app"""
        print(f"GAME END | {self.get_best_player().color} with {self.get_best_player().score}")

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
        if self.players[id % 2+1].pos != self.players[id].pos:
            self.player_cells[self.players[id].pos[0], self.players[id].pos[1]] = False
        self.players[id].pos[0] = min(max(-x_field+1*cell_size, self.players[id].pos[0] + dx * cell_size), x_field - 2 * cell_size)
        self.players[id].pos[1] = min(max(-y_field+1*cell_size, self.players[id].pos[1] - dy * cell_size), y_field - 2 * cell_size)
        self.player_cells[self.players[id].pos[0], self.players[id].pos[1]] = True

    def step(self):
        """Compute one step in the Game of Life."""
        neighbors = {}
        game_over = self.check_if_game_over()

        for x in range(-x_field+10, x_field-10, cell_size):
            for y in range(-y_field+10, y_field-10, cell_size):
                count = -self.cells[x, y]
                self.burst_cells[x, y] = False
                for h in [-cell_size, 0, cell_size]:
                    for v in [-cell_size, 0, cell_size]:
                        count += self.cells[x + h, y + v]
                neighbors[x, y] = count

        self.prev_cells = self.cells
        for cell, count in neighbors.items():
            if self.cells[cell]:
                if count < 2 or count > 3:
                    self.cells[cell] = False
                    self.burst_cells[cell] = True
                    for id in self.players:
                        self.players[id].prev_decission = self.players[id].decission
                        if self.player_cells[cell]:
                            if list(cell) == self.players[id].pos and self.players[id].alive:
                                """Player Loses Life"""
                                self.damage = True
                                # self.burst_cells[(self.players[id].pos[0], self.players[id].pos[1]+1)] = True
                                # self.burst_cells[(self.players[id].pos[0]+1, self.players[id].pos[1])] = True
                                # self.burst_cells[(self.players[id].pos[0], self.players[id].pos[1])] = True
                                # self.burst_cells[(self.players[id].pos[0], self.players[id].pos[1]-1)] = True
                                # self.burst_cells[(self.players[id].pos[0]-1, self.players[id].pos[1])] = True
                                if self.players[id].lives:
                                    self.players[id].lives = self.players[id].lives[:-1]
                                    self.players[id].score -= 1
                                    self.players[id].remember_valhala(points=-1, env=self.burst_cells, env_1=self.prev_cells)
                                else:
                                    self.players[id].alive = False
                                self.player_cells[cell] = False
                                print(f"Player {id} | {self.players[id].lives} with score {self.players[id].score}")
            elif count == 3:
                self.cells[cell] = True

        self.spawn_random_environment()

        """Agent makes new decision"""
        for id in self.players:
            # self.move_player_random_direction(id)
            self.move_player_informed_direction(id)

        if game_over:
            self.living = False
            self.close()
            return False
        return True

    def spawn_random_environment(self):
        if self.step_count % 50 == 10:
            self.inject_glider_up_right(-x_field + 40, -y_field + 40)
            self.inject_glider_up_left(x_field - 40, -y_field + 40)
            self.inject_glider_down_right(-x_field + 40, y_field - 40)
            self.inject_glider_down_left(x_field - 40, y_field - 40)
        if self.step_count % 10 == 5:
            self.randomize_patch(random.choice([-x_garden - 60, 0, x_garden + 60]),
                                 random.choice([-y_garden - 60, 0, y_garden + 60]))

    def move_player_informed_direction(self, id):
        """With PLAYER_WINNERS"""
        """Train system of nodes & weights"""
        """Feed new env to agent and get decision"""

        feature_list = self.players[id].get_memory_list(self.cells, 1)
        self.players[id].weights = self.players[id].get_action_weights(feature_list)
        self.players[id].decission = random.choices([None, 'w', 's', 'a', 'd'], weights=self.players[id].weights)[0]

        self.move_player_direction(id)
        pass

    def move_player_random_direction(self, id):
        self.players[id].decission = random.choices([None, 'w', 's', 'a', 'd'], weights=self.players[id].weights)[0]
        self.move_player_direction(id)

    def move_player_direction(self, id):
        if self.players[id].decission == 'w':
            self.move(id, 0, 1)
        if self.players[id].decission == 's':
            self.move(id, 0, -1)
        if self.players[id].decission == 'a':
            self.move(id, -1, 0)
        if self.players[id].decission == 'd':
            self.move(id, 1, 0)

    def check_if_game_over(self):
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
            if not self.player_cells[tuple(self.players[1].pos)] and not self.player_cells[tuple(self.players[2].pos)]:
                game_over = True
        return game_over

    def report_scores(self):
        """Display `text` at coordinates `x` and `y`."""

        for id in self.players:
            color_wins = count_wins(self.players[id].color)
            square(self.players[id].text[0], self.players[id].text[1], 0, 'white')
            color(self.players[id].color)
            write(f"Score {self.players[id].score}\n"
                  f"Lives {self.players[id].lives}\n"
                  f"Wins {color_wins}", font=('Arial', 20, 'normal'))

    def randomize_patch(self, x_patch=0, y_patch=0):
        for x in range(-x_garden, x_garden, cell_size):
            for y in range(-y_garden, y_garden, cell_size):
                self.cells[x + x_patch, y - y_patch] = choice([True, False])

    def draw(self):
        """Draw all the squares."""
        self.step_count += 1

        if self.step_count % 10 == 0:
            for id in self.players:
                if self.players[id].alive and self.player_cells[tuple(self.players[id].pos)]:
                    self.players[id].score += 1
                    self.ding = True
            if self.verbose and self.ding:
                self.ding = False
                pass_go_beep = Thread(target=beep.beep(1))
                pass_go_beep.start()

            print(f"Step {self.step_count}")

        live_game = self.step()
        clear()

        for (x, y), alive in self.cells.items():
            # if self.burst_cells[(x, y)] and not self.player_cells[tuple(self.players[id].pos)]:
            #     self.player_cells[tuple(self.players[1].pos)] = True
            #     self.player_cells[tuple(self.players[2].pos)] = True
            #     square(x, y, cell_size, 'green')
            if self.burst_cells[(x, y)] or self.border_cells[(x, y)]:
                square(x, y, cell_size, 'darkred')
            elif alive:
                square(x, y, cell_size, 'grey')
            else:
                square(x, y, cell_size, 'darkgrey')

            for id in self.players:
                if self.player_cells[(x, y)] and [x, y] == self.players[id].pos and self.players[id].alive:
                    square(x, y, cell_size, self.players[id].color)
                    if alive:
                        self.players[id].score += 1
                        self.ding = True
                        self.players[id].remember_valhala(points=1, env=self.cells, env_1=self.prev_cells)


        if self.verbose and self.ding:
            self.ding = False
            points_beep = Thread(target=beep.beep(1))
            points_beep.start()

        """Set Characters"""
        self.report_scores()
        if self.verbose and self.damage:
            self.damage = False
            damage_beep = Thread(target=beep.beep(3))
            damage_beep.start()

        update()

        if not live_game:

            if self.verbose:
                end_beep = Thread(target=beep.beep(5))
                end_beep.start()
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


def setup_keys(game):
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
    return game

if __name__ == "__main__":

    game1 = game(number_of_players=PLAYERS, verbose=VERBOSE)
    game1 = setup_keys(game1)

    if os.path.isfile(PKL_PATH):
        with open(PKL_PATH, 'rb') as file:
            PLAYER_WINNERS = pickle.load(file)

    while game1.living:
        print(f"Gladiator Count: {len(PLAYER_WINNERS)}")
        if not game1.draw():
            winner = game1.get_best_player()
            PLAYER_WINNERS.append(winner)
            with open(PKL_PATH, 'wb') as file:
                pickle.dump(PLAYER_WINNERS, file)
            game1 = None
            game1 = game(number_of_players=PLAYERS, verbose=VERBOSE)
            game1 = setup_keys(game1)

    done()
