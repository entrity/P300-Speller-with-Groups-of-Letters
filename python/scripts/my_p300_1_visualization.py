import sys, os, os.path

# LOG = os.path.join(os.path.dirname(os.path.realpath('__file__')), '../../1-visualisation.log')
DIR = '/media/sf_desktop-tmp/P300-Speller-with-Groups-of-Letters/'
LOG = os.path.join(DIR,'1-visualisation.log')

import numpy as np
from sklearn import discriminant_analysis

# This import requires that a symlink to this directory exist in
# openvibe-1.3.0-src/dist/share/openvibe/plugins/python
import markham.my_gtk as my_gtk
from StimulationsCodes import OpenViBE_stimulation as stimcodes

rowbase = stimcodes['OVTK_StimulationId_Label_01']
colbase = stimcodes['OVTK_StimulationId_Label_07']

# Segment is one repetition through all columns and rows
# Trial is enough repetitions to make a selection
stimstart      = stimcodes['OVTK_StimulationId_ExperimentStart']
stimstop       = stimcodes['OVTK_StimulationId_ExperimentStop']
stimreststart  = stimcodes['OVTK_StimulationId_RestStart'] # Show next target
stimreststop   = stimcodes['OVTK_StimulationId_RestStop'] # Trial and segment will begin
stimsegstart   = stimcodes['OVTK_StimulationId_SegmentStart']
stimsegstop    = stimcodes['OVTK_StimulationId_SegmentStop']
stimtrain      = stimcodes['OVTK_StimulationId_Train']
stimtrialstart = stimcodes['OVTK_StimulationId_TrialStart']
stimtrialstop  = stimcodes['OVTK_StimulationId_TrialStop']
stimstimstart  = stimcodes['OVTK_StimulationId_VisualStimulationStart']
stimstimstop   = stimcodes['OVTK_StimulationId_VisualStimulationStop']

class State:
	NULL       = 0
	EXPERIMENT = 1<<0
	REST       = 1<<1 
	TRIAL      = 1<<2
	SEGMENT    = 1<<3
	VISUAL     = 1<<4

class MyOVBox(OVBox):
	def __init__(self):
		OVBox.__init__(self)
		global my_gtk
		my_gtk = reload(my_gtk) # kludge b/c openvibe seems to cache modules
		self.gui = None
		self.count = 0
		
	def initialize(self):
		print('Python version:', sys.version)
		print('LOG:', LOG)
		if os.path.exists(LOG): os.remove(LOG)
		self.gui = my_gtk.Base()
		self.state = State.NULL
		return
		
	def process(self):
		self.count += 1
		for i in range(len(self.input)):
			source = self.input[i]
			for chunkIndex in range( len(source) ):
				chunk = source.pop()
				if(type(chunk) == OVStimulationSet):
					self._process_stims([stim.identifier for stim in chunk], self.count)
					self._print_stims(chunk, self.count)
		return

	# For debugging
	def _print_stims(self, stims, chunk_id):
		global stimmap
		for stim in stims:
			if stim.identifier in stimmap:
				with open(LOG, 'a') as f:
					print >> f, _stimtext(stim, chunk_id)
					# if stim.identifier in range(rowbase, colbase+14):
					# 	if stim.identifier < colbase:
					# 		print >> f, 'Flash Row', stim.identifier - rowbase
					# 	else:
					# 		print >> f, 'Flash Col', stim.identifier - colbase
			else:
				sys.stderr.write(_stimtext(stim, chunk_id))

	def _process_stims(self, stimslist, chunk_id):
		stims = {s:True for s in stimslist}
		# Set state
		if stimstart in stims:
			self.state |= State.EXPERIMENT
		elif stimstop in stims:
			self.state &= ~State.EXPERIMENT
		if stimreststart in stims: # Show next target for a limited time
			self.state |= State.REST
			self.target_row = None
			self.target_col = None
		elif stimreststop in stims:
			self.state &= ~State.REST
		if stimsegstart in stims:
			self.state |= State.SEGMENT
		elif stimsegstop in stims:
			self.state &= ~State.SEGMENT
		if stimtrain in stims:
			pass
		if stimtrialstart in stims:
			self.state |= State.TRIAL
		elif stimtrialstop in stims:
			self.state &= ~State.TRIAL
		if stimstimstart in stims: # Flash row/col
			self.state |= State.VISUAL
		elif stimstimstop in stims:
			self.state &= ~State.VISUAL
		# Send commands to GUI
		for stim in stimslist:
			if stim in range(rowbase, rowbase+2):
				row = stim - rowbase
				if self.state & State.REST:
					self.target_row = row
					print 'New target row', row
					self._highlight_target_if_indicated()
				elif self.state & State.VISUAL:
					self.gui.highlight_row(row)
					print 'row', row
			elif stim in range(colbase, colbase+2):
				col = stim - colbase
				if self.state & State.REST:
					self.target_col = col
					print 'New target col', col
					self._highlight_target_if_indicated()
				elif self.state & State.VISUAL:
					self.gui.highlight_col(col)
					print 'col', col
		if stimreststart in stims:
			self.target_row = None
			self.target_col = None

	def _highlight_target_if_indicated(self):
		if self.target_row != None and self.target_col != None:
			self.gui.highlight_target(self.target_row, self.target_col)

	def uninitialize(self):
		if self.gui != None:
			self.gui.window.destroy()
		return

def _stimtext(stim, input):
	return 'Received in %6d stim %d %s stamped at %lf' % (input, stim.identifier, stimmap.get(stim.identifier,'ERR'), stim.date)

stimmap = {	
	0x00008001: 'OVTK_StimulationId_ExperimentStart',
	0x00008002: 'OVTK_StimulationId_ExperimentStop',
	0x00008003: 'OVTK_StimulationId_SegmentStart',
	0x00008004: 'OVTK_StimulationId_SegmentStop',
	0x00008005: 'OVTK_StimulationId_TrialStart',
	0x00008006: 'OVTK_StimulationId_TrialStop',
	0x00008007: 'OVTK_StimulationId_BaselineStart',
	0x00008008: 'OVTK_StimulationId_BaselineStop',
	0x00008009: 'OVTK_StimulationId_RestStart',
	0x0000800a: 'OVTK_StimulationId_RestStop',
	0x0000800b: 'OVTK_StimulationId_VisualStimulationStart',
	0x0000800c: 'OVTK_StimulationId_VisualStimulationStop',
	0x00008010: 'OVTK_StimulationId_VisualSteadyStateStimulationStart',
	0x00008011: 'OVTK_StimulationId_VisualSteadyStateStimulationStop',
	0x00008012: 'OVTK_StimulationId_Button1_Pressed',
	0x00008013: 'OVTK_StimulationId_Button1_Released',
	0x00008014: 'OVTK_StimulationId_Button2_Pressed',
	0x00008015: 'OVTK_StimulationId_Button2_Released',
	0x00008016: 'OVTK_StimulationId_Button3_Pressed',
	0x00008017: 'OVTK_StimulationId_Button3_Released',
	0x00008018: 'OVTK_StimulationId_Button4_Pressed',
	0x00008019: 'OVTK_StimulationId_Button4_Released',
	0x00008100: 'OVTK_StimulationId_Label_00',
	0x00008101: 'OVTK_StimulationId_Label_01',
	0x00008102: 'OVTK_StimulationId_Label_02',
	0x00008103: 'OVTK_StimulationId_Label_03',
	0x00008104: 'OVTK_StimulationId_Label_04',
	0x00008105: 'OVTK_StimulationId_Label_05',
	0x00008106: 'OVTK_StimulationId_Label_06',
	0x00008107: 'OVTK_StimulationId_Label_07',
	0x00008108: 'OVTK_StimulationId_Label_08',
	0x00008109: 'OVTK_StimulationId_Label_09',
	0x0000810a: 'OVTK_StimulationId_Label_0A',
	0x0000810b: 'OVTK_StimulationId_Label_0B',
	0x0000810c: 'OVTK_StimulationId_Label_0C',
	0x0000810d: 'OVTK_StimulationId_Label_0D',
	0x0000810e: 'OVTK_StimulationId_Label_0E',
	0x0000810f: 'OVTK_StimulationId_Label_0F',
	0x00008110: 'OVTK_StimulationId_Label_10',
	0x00008111: 'OVTK_StimulationId_Label_11',
	0x00008112: 'OVTK_StimulationId_Label_12',
	0x00008113: 'OVTK_StimulationId_Label_13',
	0x00008114: 'OVTK_StimulationId_Label_14',
	0x00008115: 'OVTK_StimulationId_Label_15',
	0x00008116: 'OVTK_StimulationId_Label_16',
	0x00008117: 'OVTK_StimulationId_Label_17',
	0x00008118: 'OVTK_StimulationId_Label_18',
	0x00008119: 'OVTK_StimulationId_Label_19',
	0x0000811a: 'OVTK_StimulationId_Label_1A',
	0x0000811b: 'OVTK_StimulationId_Label_1B',
	0x0000811c: 'OVTK_StimulationId_Label_1C',
	0x0000811d: 'OVTK_StimulationId_Label_1D',
	0x0000811e: 'OVTK_StimulationId_Label_1E',
	0x0000811f: 'OVTK_StimulationId_Label_1F',
	0x00000000: 'OVTK_StimulationId_Number_00',
	0x00000001: 'OVTK_StimulationId_Number_01',
	0x00000002: 'OVTK_StimulationId_Number_02',
	0x00000003: 'OVTK_StimulationId_Number_03',
	0x00000004: 'OVTK_StimulationId_Number_04',
	0x00000005: 'OVTK_StimulationId_Number_05',
	0x00000006: 'OVTK_StimulationId_Number_06',
	0x00000007: 'OVTK_StimulationId_Number_07',
	0x00000008: 'OVTK_StimulationId_Number_08',
	0x00000009: 'OVTK_StimulationId_Number_09',
	0x0000000a: 'OVTK_StimulationId_Number_0A',
	0x0000000b: 'OVTK_StimulationId_Number_0B',
	0x0000000c: 'OVTK_StimulationId_Number_0C',
	0x0000000d: 'OVTK_StimulationId_Number_0D',
	0x0000000e: 'OVTK_StimulationId_Number_0E',
	0x0000000f: 'OVTK_StimulationId_Number_0F',
	0x00000010: 'OVTK_StimulationId_Number_10',
	0x00000011: 'OVTK_StimulationId_Number_11',
	0x00000012: 'OVTK_StimulationId_Number_12',
	0x00000013: 'OVTK_StimulationId_Number_13',
	0x00000014: 'OVTK_StimulationId_Number_14',
	0x00000015: 'OVTK_StimulationId_Number_15',
	0x00000016: 'OVTK_StimulationId_Number_16',
	0x00000017: 'OVTK_StimulationId_Number_17',
	0x00000018: 'OVTK_StimulationId_Number_18',
	0x00000019: 'OVTK_StimulationId_Number_19',
	0x0000001a: 'OVTK_StimulationId_Number_1A',
	0x0000001b: 'OVTK_StimulationId_Number_1B',
	0x0000001c: 'OVTK_StimulationId_Number_1C',
	0x0000001d: 'OVTK_StimulationId_Number_1D',
	0x0000001e: 'OVTK_StimulationId_Number_1E',
	0x0000001f: 'OVTK_StimulationId_Number_1F',
	0x00008201: 'OVTK_StimulationId_Train',
	0x00008202: 'OVTK_StimulationId_Beep',
	0x00008203: 'OVTK_StimulationId_DoubleBeep',
	0x00008204: 'OVTK_StimulationId_EndOfFile',
	0x00008205: 'OVTK_StimulationId_Target',
	0x00008206: 'OVTK_StimulationId_NonTarget',
	0x00008207: 'OVTK_StimulationId_TrainCompleted',
	0x00008208: 'OVTK_StimulationId_Reset',
}

with open(DIR + '/modules.txt', 'w') as f:
			print >> f, dir()
			print >> f, sys.modules
			print >> f, sys.argv
			print >> f, sys.path

box = MyOVBox()
