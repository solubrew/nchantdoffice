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
class ImageWidget(pyqt.QWidget):
	def __init__(self,surface,parent=None):
		super(ImageWidget,self).__init__(parent)
		w=surface.get_width()
		h=surface.get_height()
		self.data=surface.get_buffer().raw
		self.image=pyqt.QImage(self.data,w,h,pyqt.QImage.Format_RGB32)

	def paintEvent(self,event):
		my_paint=pyqt.QPainter()
		# the definitions for PyQt4 and PyQt5 use QtGui.QPainter()
		my_paint.begin(self)
		my_paint.drawImage(0,0,self.image)
		my_paint.end()

class MainWindow(pyqt.QMainWindow):
	def __init__(self,surface,parent=None):
		super(MainWindow,self).__init__(parent)
		self.setFixedSize(640, 480)
		self.setCentralWidget(ImageWidget(surface))
# this part of source code need to be updated if you want to use animation
# init PyGame
pygame.init()
# define a surface
my_surface=pygame.Surface((640,480))
# fill the surface, see https://www.pygame.org/docs/ref/surface.html#pygame.Surface.fill
my_surface.fill((0,0,255,176))
# draw circle see https://www.pygame.org/docs/ref/draw.html#pygame.draw.circle
#pygame.draw.circle(my_surface,(0,0,127,255),(76,76),76)
# draw ellipse (surface, color(R,G,B), size (x,y,x+dx, y+y+dy) )
#pygame.draw.ellipse(my_surface,(127,0,0,0),(0,0,12,76))

# this part of source code will show
# the my_surface created with PyGame in PyQt5
# old definition for PyQt4
#app=QtGui.QApplication(sys.argv)
app=pyqt.QApplication(sys.argv)
my_window=MainWindow(my_surface)
my_window.show()
app.exec_()
