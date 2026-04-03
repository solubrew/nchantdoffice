# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
	docid:
	name:
	description: >
	version: 0.0.0.0.0.0
	authority: filesystem
	security: seclvl2
	<(WT)>: -32
"""
# -*- coding: utf-8 -*
# ======================================Standard Library Modules======================================================||
from os.path import abspath, dirname, join
import datetime as dt
import sys

# ======================================3rd Party Library Modules=====================================================||
import pygame
from colors import Colors

# ======================================Solutions Brewer Library Modules==============================================||
from condor import condor
from nchantrs.packages.nchantdarena.games.models import GameModel
from ogma.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), '')  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, '_data_', 'games.yaml')
GAME_UPDATE = pygame.USEREVENT

class Game():
	""""""
	def __init__(self, cfg=None):
		""""""
		self.config = condor.instruct(pxcfg).select('').override(cfg)
		self.game_model = GameModel(self.config)
		self.screen = None
		self.clock = None
		self.title_font = None
		self.score_surface = None
		self.next_surface = None
		self.game_over_surface = None
		self.score_rect = None
		self.next_rect = None
		self.running = False
		self.fps = 60
		self.score = Score()

	def init(self):
		""""""
		pygame.init()
		self.title_font = pygame.font.Font(None, 40)
		self.score_surface = self.title_font.render("Score", True, Colors.white)
		self.next_surface = self.title_font.render("Next", True, Colors.white)
		self.game_over_surface = self.title_font.render("GAME OVER", True, Colors.white)
		self.score_rect = pygame.Rect(320, 55, 170, 60)
		self.next_rect = pygame.Rect(320, 215, 170, 180)
		self.screen = pygame.display.set_mode((500, 620))
		pygame.display.set_caption("Python Tetris")
		self.clock = pygame.time.Clock()
		pygame.time.set_timer(GAME_UPDATE, 200)

	def run(self):
		self.running = True
		while self.running:
			self.clock.tick(self.fps)
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.KEYDOWN:
					if self.game_model.game_over == True:
						self.game_model.game_over = False
						self.game_model.reset()
					if event.key == pygame.K_LEFT and self.game_model.game_over is False:
						self.game_model.move_left()
					if event.key == pygame.K_RIGHT and self.game_model.game_over is False:
						self.game_model.move_right()
					if event.key == pygame.K_DOWN and self.game_model.game_over is False:
						self.game_model.move_down()
						self.game_model.update_score(0, 1)
					if event.key == pygame.K_UP and self.game_model.game_over is False:
						self.game_model.rotate()
				if event.type == GAME_UPDATE and self.game_model.game_over is False:
					self.game_model.move_down()
			self.draw()
			pygame.display.update()

	def draw(self):
		""""""
		# Drawing
		score_value_surface = self.title_font.render(str(self.game_model.score), True, Colors.white)
		self.screen.fill(Colors.dark_blue)
		self.screen.blit(self.score_surface, (365, 20, 50, 50))
		self.screen.blit(self.next_surface, (375, 180, 50, 50))
		if self.game_model.game_over == True:
			self.screen.blit(self.game_over_surface, (320, 450, 50, 50))
		pygame.draw.rect(self.screen, Colors.light_blue, self.score_rect, 0, 10)
		score_surface = score_value_surface.get_rect(centerx=self.score_rect.centerx, centery=self.score_rect.centery)
		self.screen.blit(score_value_surface, score_surface)
		pygame.draw.rect(self.screen, Colors.light_blue, self.next_rect, 0, 10)
		self.game.draw(self.screen)

	def set_fps(self, fps):
		""""""
		self.fps = fps
		return self

class GameLibrary():
	""""""
	def __init__(self, cfg=None):
		""""""
		self.config = condor.instruct(pxcfg).select('').override(cfg)
		self.games_available = []

	def get_games_list(self):
		"""connect to service and see what games can be downloaded"""

	def get_game_details(self, game_id):
		""""""

	def download_games(self):
		""""""

	def download_game(self, game_id):
		""""""




class Score():
	"""Need a way to score each game against a common scale

		scoring metrics:
		- average time to complete vs time to complete
			- use averages from overall game and specific boards
		- total score
		- difficulty of board
			use a 1 to 32 difficulty scale where
			1 is a simple word search
			32 is a high level tetris level
		- % completion of level
		- unique in game actions?
		-
	"""
	def __init__(self, cfg=None):
		""""""
		self.config = condor.instruct(pxcfg).select('').override(cfg)
		self.point_score = 0
		self.game_time = 0
		self.difficulty = 16
		self.level_completion = 0
		self.unique_game_actions = 16

	def calculate(self):
		""""""

	def get_score(self):
		""""""

	def send_score(self):
		""""""



class LeaderBoard():
	""""""
	def __init__(self, cfg=None):
		""""""
		self.config = condor.instruct(pxcfg).select('').override(cfg)

	def get_leaderboard(self):
		""""""

	def submit_score(self):
		""""""


class MiniGames():
	""""""
	def __init__(self, cfg=None):
		""""""
		self.config = condor.instruct(pxcfg).select('').override(cfg)

	def load(self):
		""""""
		return self

	def get_games_list(self):
		"""
		Start with 5 games
		- tetris
		- pacman
		- space invaders
		- pong
		- memory
		- mazes
		- word search
		:return:
		"""
		return self



# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||







