import sys, os, os.path

# LOG = os.path.join(os.path.dirname(os.path.realpath('__file__')), '../../1-visualisation.log')
DIR = '/media/sf_desktop-tmp/P300-Speller-with-Groups-of-Letters/'
LOG = os.path.join(DIR,'1-visualisation.log')
FEATURE_TSV = os.path.join(DIR,'features.tsv')
STIM_TSV = os.path.join(DIR,'stims.tsv')
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
		with open(STIM_TSV, 'w') as f:
			f.write('\t'.join(('start', 'in-channel', 'tar-row', 'tar-col', 'cur-row', 'cur-col', 'stims...')) + '\n')
		with open(FEATURE_TSV, 'w') as f:
			f.write('\t'.join(('start', 'in-channel', 'features...')) + '\n')
		self.state = stimstate.State(None)
		return

	def process(self):
		self.count += 1
		for i in range(len(self.input)):
			source = self.input[i]
			for chunkIndex in range( len(source) ):
				chunk = source.pop()
				if type(chunk) == OVStreamedMatrixBuffer:
					with open(FEATURE_TSV, 'a') as f:
						# Format:
						# timestamp, class, features...
						f.write('\t'.join([str(x) for x in (chunk.startTime, i)]))
						f.write('\t')
						f.write('\t'.join(str(x) for x in chunk)) # features
						f.write('\n')
				elif type(chunk) == OVStimulationSet:
					self.state.process_stims([stim.identifier for stim in chunk], self.count)
					with open(os.path.join(DIR, 'stim.tmp'), 'a') as f:
						f.write('\n\nCHUNK\n')
						f.write(str(chunk))
						for stim in chunk:
							f.write('\n')
							f.write(str(stim))
							f.write('\ndir')
							f.write(str(dir(stim)))
							f.write('\nid')
							f.write(str(stim.identifier))
							f.write('\n')
					with open(STIM_TSV, 'a') as f:
						# Format:
						# timestamp, class, target-row, target-col, cur-row, cur-col, labels...
						labels = [stimstate.stimmap[stim.identifier] for stim in chunk if stim.identifier in stimstate.stimmap]
						if len(labels):
							f.write('\t'.join([str(x) for x in (chunk.startTime, i)]))
							f.write('\t')
							f.write('\t'.join([str(float('nan') if x == None else x) for x in (self.state.target_row, self.state.target_col, self.state.row, self.state.col)]))
							f.write('\t')
							f.write('\t'.join(labels))
							f.write('\n')
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
