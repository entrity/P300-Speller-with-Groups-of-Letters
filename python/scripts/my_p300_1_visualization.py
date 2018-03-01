import sys, os, os.path

# LOG = os.path.join(os.path.dirname(os.path.realpath('__file__')), '../../1-visualisation.log')
DIR = '/media/sf_desktop-tmp/P300-Speller-with-Groups-of-Letters/'
LOG = os.path.join(DIR,'1-visualisation.log')
DEBUG = 0

import numpy as np
from sklearn import discriminant_analysis

# This import requires that a symlink to this directory exist in
# openvibe-1.3.0-src/dist/share/openvibe/plugins/python
import markham.my_gtk as my_gtk
import markham.state as stimstate

class MyOVBox(OVBox):
	def __init__(self):
		OVBox.__init__(self)
		global my_gtk
		my_gtk = reload(my_gtk) # kludge b/c openvibe seems to cache modules
		global stimstate
		stimstate = reload(stimstate) # kludge b/c openvibe seems to cache modules
		self.gui = None
		self.count = 0
		self.state = None
		
	def initialize(self):
		print('Python version:', sys.version)
		print('LOG:', LOG)
		if os.path.exists(LOG): os.remove(LOG)
		self.gui = my_gtk.Base()
		self.state = stimstate.State(self.gui)
		return
		
	def process(self):
		self.count += 1
		for i in range(len(self.input)):
			source = self.input[i]
			for chunkIndex in range( len(source) ):
				chunk = source.pop()
				if(type(chunk) == OVStimulationSet):
					self.state.process_stims([stim.identifier for stim in chunk], self.count)
		return

	def uninitialize(self):
		if self.gui != None:
			self.gui.window.destroy()
		return

with open(DIR + '/modules.txt', 'w') as f:
			print >> f, dir()
			print >> f, sys.modules
			print >> f, sys.argv
			print >> f, sys.path

box = MyOVBox()
