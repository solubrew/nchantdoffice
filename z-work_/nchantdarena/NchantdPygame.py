#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@nchantdTree - Main@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
'''  #																			||
---  #																			||
<(META)>:  #																	||
	docid:    #								||
	name: Nchantd Moon Bags#													||
	description: >  #															||

	expirary: <[expiration]>  #													||
	version: <[version]>  #														||
	path: <[LEXIvrs]>  #														||
	outline: <[outline]>  #														||
	authority: document|this  #													||
	security: sec|lvl2  #														||
	<(WT)>: -32  #																||
''' #																			||
# -*- coding: utf-8 -*-#														||
#=================================Core Modules==================================||
import sys
from os.path import abspath, dirname, exists, join, expanduser
import pygame
from datetime import timedelta
#===============================================================================||
import crow
#===============================================================================||
from condor import condor#										||
from nchantrs.dstruct import trees as dtrees
from nchantrs.nchantrs import NchantdCloak
from nchantrs.models.applicationmodels import NchantdCloakModel
from nchantrs.libraries import pyqt
from nchantrs.widgets.trees import NchantdTimeTree
#===============================================================================||
there = abspath(join(''))#												||set path at pheonix level
here = join(dirname(__file__),'')#												||
version = '0.0.0.0.0.0'#														||
log = True
#===============================================================================||

# pygame.init()
# s=pygame.Surface((640,480))
# pygame.draw.circle(s,(255,255,255,255),(100,100),50)

class GameWidget(pyqt.QWidget):
	''' '''
	def __init__(self):
		''' '''
		super(GameWidget, self).__init__()
		pygame.init()
		self.surfaceHeight = 640
		self.surfaceWidth = 480
		self.surface = pygame.Surface((self.surfaceHeight, self.surfaceWidth))
		self.display = pygame.display.set_mode((self.surfaceHeight, self.surfaceWidth))
		self.setBackground()
		self.loop()
	def setBackground(self):
		''' '''
		#self.surface.fill(colors['white'])
		self.surface.fill((0,0,255,176))
		#pygame.draw.circle(self.surface,(0,0,127,255),(76,76),76)
		# draw ellipse (surface, color(R,G,B), size (x,y,x+dx, y+y+dy) )
		#pygame.draw.ellipse(self.surface,(127,0,0,0),(0,0,12,76))
		return
	def player(self):
		''' '''
		return
	def loadAssets(self, xpos, ypos):
		''' '''
		ball(self.display, xpos, ypos)
		return self
	def loop(self):
		''' '''
		gameClock = pygame.time.Clock()
		xd, yd = self.surfaceHeight*0.45, self.surfaceWidth*0.8
		carwidth = 25
		self.setBackground()
		gameExit = False
		while not gameExit:
			for event in pygame.event.get():#gets all events
				if log: print('Event', event.__dir__())
				xd0, yd0 = self.trigger(event)
				xd += xd0
				yd += yd0
			self.loadAssets(xd, yd)
			if xd > self.surfaceWidth - carwidth or xd < 0:
				crash()
				gameExit = True
			pygame.display.update()
			gameClock.tick(60)
	def trigger(self, event):
		''' '''
		x_delta = 0
		y_delta = 0
		if attr(pos, event):
			#mouse event
		if attr(key, event):
			#keyboard event
		if event.type == pygame.QUIT:
			pygame.quit()
			quit()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_LEFT:
				x_delta = -1
			elif event.key == pygame.K_RIGHT:
				x_delta = 1
			elif event.key == pygame.K_DOWN:
				y_delta = 1
			elif event.key == pygame.K_UP:
				y_delta = -1
		if event.type == pygame.KEYUP:
			x_delta = 0
			y_delta = 0
		return x_delta, y_delta
class Asset(object):
	''' '''
	def __init__(self):
		''' '''
	def loadSprites(self):
		''' '''
		return self
	def setShape(self):
		'''Allow for mulitiple polyhedra shapes for boundaries of the asset '''
		return self
	def setWidth(self):
		return self
	def setHeight(self):
		return self
def ball(display, x,y):
	ballImg = pygame.image.load('blueStone.png')
	display.blit(ballImg, (x,y))

class ImageWidget(pyqt.QWidget):
	def __init__(self, arena, parent=None):
		super(ImageWidget,self).__init__(parent)
		w = arena.surface.get_width()
		h = arena.surface.get_height()
		self.data = arena.surface.get_buffer().raw
		self.image = pyqt.QImage(self.data, w, h, pyqt.QImage.Format_RGB32)
	def paintEvent(self, event):
		qp = pyqt.QPainter()
		qp.begin(self)
		qp.drawImage(0, 0, self.image)
		qp.end()
class MainWindow(pyqt.QMainWindow):
	def __init__(self, parent=None):
		super(MainWindow,self).__init__(parent)
		arena = GameWidget()
		self.setFixedSize(640, 480)
		self.setCentralWidget(ImageWidget(arena))
app=pyqt.QApplication(sys.argv)
w=MainWindow()
w.show()
app.exec_()
