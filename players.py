import random
import time
import copy
from copy import deepcopy
import pygame
import math
from connect4 import connect4

class connect4Player(object):
	def __init__(self, position, seed=0, CVDMode=False):
		self.position = position
		self.opponent = None
		self.seed = seed
		random.seed(seed)
		if CVDMode:
			global P1COLOR
			global P2COLOR
			P1COLOR = (227, 60, 239)
			P2COLOR = (0, 255, 0)

	def play(self, env: connect4, move: list) -> None:
		move = [-1]

class human(connect4Player):

	def play(self, env: connect4, move: list) -> None:
		move[:] = [int(input('Select next move: '))]
		while True:
			if int(move[0]) >= 0 and int(move[0]) <= 6 and env.topPosition[int(move[0])] >= 0:
				break
			move[:] = [int(input('Index invalid. Select next move: '))]

class human2(connect4Player):

	def play(self, env: connect4, move: list) -> None:
		done = False
		while(not done):
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()

				if event.type == pygame.MOUSEMOTION:
					pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
					posx = event.pos[0]
					if self.position == 1:
						pygame.draw.circle(screen, P1COLOR, (posx, int(SQUARESIZE/2)), RADIUS)
					else: 
						pygame.draw.circle(screen, P2COLOR, (posx, int(SQUARESIZE/2)), RADIUS)
				pygame.display.update()

				if event.type == pygame.MOUSEBUTTONDOWN:
					posx = event.pos[0]
					col = int(math.floor(posx/SQUARESIZE))
					move[:] = [col]
					done = True

class randomAI(connect4Player):

	def play(self, env: connect4, move: list) -> None:
		possible = env.topPosition >= 0
		indices = []
		for i, p in enumerate(possible):
			if p: indices.append(i)
		move[:] = [random.choice(indices)]

class stupidAI(connect4Player):

	def play(self, env: connect4, move: list) -> None:
		possible = env.topPosition >= 0
		indices = []
		for i, p in enumerate(possible):
			if p: indices.append(i)
		if 3 in indices:
			move[:] = [3]
		elif 2 in indices:
			move[:] = [2]
		elif 1 in indices:
			move[:] = [1]
		elif 5 in indices:
			move[:] = [5]
		elif 6 in indices:
			move[:] = [6]
		else:
			move[:] = [0]

class minimaxAI(connect4Player):

	def play(self, env: connect4, move: list) -> None:
		valid_move = self.valid_col_location(env)
		env = deepcopy(env)
		env.visualize = False
		max_score = -math.inf
		depth = 3

		if len(env.history[0]) == 0:
			move[:] = [3]  # if first move --> start at center
		else:
			for good_option in valid_move:
				child = deepcopy(env)
				self.potential_moves(child, good_option, self.position)
				child_value = self.minimize(child, depth - 1)
				if child_value > max_score:
					move[:] = [good_option]
					max_score = child_value



	def maximize(self, env, depth):
		child = deepcopy(env)
		max_score = -math.inf
		valid_move = self.valid_col_location(env)

		if env.gameOver(env.history[0][-1], self.opponent.position):
			return -100000
		if depth == 0:
			return self.score_function(env.board)  # eval for current player

		for good_option in valid_move:
			self.potential_moves(child, good_option, self.position)
			option_val = self.minimize(child, depth - 1)
			max_score = max(max_score, option_val)
		return max_score

	def minimize(self, env, depth):
		child = deepcopy(env)
		max_score = math.inf
		valid_move = self.valid_col_location(env)
		if env.gameOver(env.history[0][-1], self.position):
			return 100000
		if depth == 0:
			return self.score_function(env.board)  # eval for current player

		for good_option in valid_move:
			self.potential_moves(child, good_option, self.opponent.position)
			option_val = self.maximize(child, depth - 1)
			max_score = min(max_score, option_val)
		return max_score

	def potential_moves(self, env, move, player):
		env.board[env.topPosition[move]][move] = player
		env.topPosition[move] -= 1
		env.history[0].append(move)
		return env

	def evaluate(self, window):
		# calculate streak counts for both players
		opp = self.opponent.position
		my_piece = self.position

		score = 0
		window = list(window)

		if window.count(my_piece) == 3 and window.count(0) == 1:  # checks if 3x in the window and there is an empty space.
			score += 10000
		if window.count(my_piece) == 2 and window.count(0) == 2:
			score += 500
		if window.count(my_piece) == 1 and window.count(0) == 3:
			score += 100

		if window.count(opp) == 3 and window.count(0) == 1:  # blocks if opp has 3 and theres an empty space in the window
			score -= 10000
		if window.count(opp) == 2 and window.count(0) == 1:  # blocks if opp has 2 and theres an empty space in the window
			score -= 500
		if window.count(opp) == 1 and window.count(0) == 3:
			score -= 100

		return score

	def score_function(self, env):
		piece = self.position  # default

		score = 0
		# heavier weight to prioritize scoring center column

		center_count = 0
		for row in env:
			if row[COLUMN_COUNT // 2] == piece:
				center_count += 1
		score += center_count * 12

		# check entire board to evaluate score

		# score horizontal

		for r in range(ROW_COUNT):  # Get the current row as a list of integers
			for c in range(COLUMN_COUNT):
				window = env[r, c:c + window_length]  # Get the window of four consecutive columns
				score += self.evaluate(window)  # Evaluate the window and add the score

		# score vertical

		for c in range(COLUMN_COUNT):
			for r in range(ROW_COUNT - 3):
				window = env[r:r + window_length, c]
				score += self.evaluate(window)

		# 	window = [board[i][c] for i in range(r, r + window_length)]
		# + diag
		for row in range(3):
			for col in range(4):
				window = [env[row + i][col + i] for i in range(window_length)]
				score += self.evaluate(window)
		# diagonal evaluation

		# -diag
		for row in range(3, 6):
			for col in range(3, 7):
				window = [env[row - i][col - i] for i in range(window_length)]
				score += self.evaluate(window)
		return score

	def valid_col_location(self, env):  # valid columns
		possible_move = env.topPosition >= 0  # can add coin bc column not full
		index = []
		for i, p in enumerate(possible_move):  # keeps track of possible move
			if p:
				index.append(i)
		return index

class alphaBetaAI(connect4Player):

	def play(self, env: connect4, move: list) -> None:
		valid_move = self.valid_col_location(env)
		env = deepcopy(env)
		env.visualize = False
		max_score = -math.inf
		beta = math.inf
		alpha = -math.inf
		depth = 3
		

		if len(env.history[0]) == 0:
			move[:] = [3]  # if first move always start down center
		else:
			for good_option in valid_move:
				child = deepcopy(env)
				self.potential_moves(child, good_option, self.position)
				child_value = self.minimize(child, depth - 1, alpha, beta)
				if child_value > max_score:
					max_score = child_value
					move[:] = [good_option]

	def maximize(self, env, depth, alpha, beta):

		child = deepcopy(env)
		max_score = -math.inf
		valid_move = self.valid_col_location(env)

		if env.gameOver(env.history[0][-1], self.opponent.position):
			return -100000
		if depth == 0:
			return self.score_function(env.board)  # eval for current player

		for good_option in valid_move:
			self.potential_moves(child, good_option, self.position)
			option_val = self.minimize(child, depth - 1, alpha, beta)
			max_score = max(max_score, option_val)
			alpha = max(alpha, max_score)
			if max_score >= beta:
				break
		return max_score

	def minimize(self, env, depth, alpha, beta):

		child = deepcopy(env)
		max_score = math.inf
		valid_move = self.valid_col_location(env)
		if env.gameOver(env.history[0][-1], self.position):
			return 100000
		if depth == 0:
			return self.score_function(env.board)  # eval for current player

		for good_option in valid_move:
			self.potential_moves(child, good_option, self.opponent.position)
			option_val = self.maximize(child, depth - 1, alpha, beta)
			max_score = min(max_score, option_val)
			beta = min(beta, option_val)
			if max_score <= alpha:
				break
		return max_score

	def potential_moves(self, env, move, player):
		env.board[env.topPosition[move]][move] = player
		env.topPosition[move] -= 1
		env.history[0].append(move)
		return env

	def evaluate(self, window):
		# calculate streak counts for both players
		opp = self.opponent.position
		my_piece = self.position

		score = 0
		window = list(window)

		if window.count(my_piece) == 3 and window.count(
				0) == 1:  # checks if 3x in the window and there is an empty space.
			score += 10000
		if window.count(my_piece) == 2 and window.count(0) == 2:
			score += 500
		if window.count(my_piece) == 1 and window.count(0) == 3:
			score += 100

		if window.count(opp) == 3 and window.count(
				0) == 1:  # blocks if opp has 3 and theres an empty space in the window
				score -= 10000
		if window.count(opp) == 2 and window.count(
				0) == 1:  # blocks if opp has 2 and theres an empty space in the window
			score -= 500
		if window.count(opp) == 1 and window.count(0) == 3:
			score -= 100

		return score

	def score_function(self, env):
		piece = self.position  # default

		score = 0
		# prioritize scoring center column, heavier weight

		center_count = 0
		for row in env:
			if row[COLUMN_COUNT // 2] == piece:
				center_count += 1
		score += center_count * 12

		# below we go over every single window in different directions and adding up their values to the score

		# vertical score

		for c in range(COLUMN_COUNT):
			for r in range(ROW_COUNT - 3):
				window = env[r:r + window_length, c]
				score += self.evaluate(window)
				

		# horizontal score 

		for r in range(ROW_COUNT):  # Get the current row as a list of integers
			for c in range(COLUMN_COUNT):
				window = env[r, c:c + window_length]  # Get the window of four consecutive columns
				score += self.evaluate(window)  # Evaluate the window and add the score


		# 	window = [board[i][c] for i in range(r, r + window_length)]
		# + diag
		for row in range(3):
			for col in range(4):
				window = [env[row + i][col + i] for i in range(window_length)]
				score += self.evaluate(window)
		# diagonal evaluation

		# -diag
		for row in range(3, 6):
			for col in range(3, 7):
				window = [env[row - i][col - i] for i in range(window_length)]
				score += self.evaluate(window)
		return score

	def valid_col_location(self, env):  # valid columns
		possible_move = env.topPosition >= 0  # can add coin bc column not full
		index = []
		for i, p in enumerate(possible_move):  # keeps track of possible moves
			if p:
				index.append(i)
		return index




SQUARESIZE = 100
BLUE = (0,0,255)
BLACK = (0,0,0)
P1COLOR = (255,0,0)
P2COLOR = (255,255,0)

ROW_COUNT = 6
COLUMN_COUNT = 7

pygame.init()

window_length = 4

SQUARESIZE = 100

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE/2 - 5)

screen = pygame.display.set_mode(size)




