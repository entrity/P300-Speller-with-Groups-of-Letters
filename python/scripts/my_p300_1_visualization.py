import sys, os, os.path
import pygtk
pygtk.require('2.0')
import gtk

# LOG = os.path.join(os.path.dirname(os.path.realpath('__file__')), '../../1-visualisation.log')
DIR = '/media/sf_desktop-tmp/P300-Speller-with-Groups-of-Letters/'
LOG = os.path.join(DIR,'1-visualisation.log')

import numpy as np
from sklearn import discriminant_analysis


CHARS = [ chr(x) for x in range(65,91) ] + [ chr(x) for x in range(48,58) ]

def make_label():
  l = gtk.Label()
  l.set_justify(gtk.JUSTIFY_CENTER)
  l.show()
  return l

class Base:
  def __init__(self):
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self.lbls = [make_label() for i in range(4)]
    # Table
    self.table = gtk.Table(rows=2, columns=2, homogeneous=True)
    self.table.attach(self.lbls[0], 0, 1, 0, 1)
    self.table.attach(self.lbls[1], 1, 2, 0, 1)
    self.table.attach(self.lbls[2], 0, 1, 1, 2)
    self.table.attach(self.lbls[3], 1, 2, 1, 2)
    self.table.show()
    # Target
    self.text  = gtk.TextBuffer()
    self.text.set_text("Target : ")
    self.label = gtk.TextView(self.text)
    self.label.show()
    # Main container
    self.vbox = gtk.VBox(False, 0)
    self.vbox.pack_start(self.table, expand=True, fill=True)
    self.vbox.pack_end(self.label, expand=False, fill=True)
    self.vbox.show()
    # Window
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self.window.resize(600,600)
    self.window.add(self.vbox)
    self.window.show()
    self._set_view((1,))

  def _get_chars(self, selections):
    threes = [CHARS[i:i+3] for i in range(0, len(CHARS), 3)]
    triptrips = [threes[i:i+3] for i in range(0, len(threes), 3)]
    if len(selections) == 0:
      str9s = ['\n'.join(' '.join(x) for x in y) for y in triptrips]
      return str9s
    elif len(selections) == 1:
      return [' '.join(x) for x in triptrips[selections[0]]] + ['<back>']
    else:
      return triptrips[selections[0]][selections[1]] + ['<back>']

  def _set_view(self, selections):
    lists = self._get_chars(selections)
    print(lists)
    for i in range(4):
      size = 50000 if len(selections) == 0 else 100000
      self.lbls[i].set_markup(('<span size="%d">' % size)+lists[i]+'</span>')
    if len(selections) > 0:
      self.lbls[3].set_markup('<span size="40000">&lt;back&gt;</span>')

  def main(self):
    gtk.main()

class MyOVBox(OVBox):
	def __init__(self):
		OVBox.__init__(self)
		self.gui = None
		
	def initialize(self):
		print('Python version:', sys.version)
		print('LOG:', LOG)
		if os.path.exists(LOG): os.remove(LOG)
		self.gui = Base()
		return
		
	def process(self):
		global stimmap
		for i in range(len(self.input)):
			source = self.input[i]
			for chunkIndex in range( len(source) ):
				chunk = source.pop()
				if(type(chunk) == OVStimulationSet):
					for stimIdx in range(len(chunk)):
						stim=chunk.pop();
						if stim.identifier in stimmap:
							with open(LOG, 'a') as f:
								print >> f, _stimtext(stim, i)
						else:
							sys.stderr.write(_stimtext(stim, i))
		return


	def uninitialize(self):
		if self.gui != None:
			self.gui.window.destroy()
		return

def _stimtext(stim, input):
	return 'Received in %d stim %d %s stamped at %lf' % (input, stim.identifier, stimmap.get(stim.identifier,'ERR'), stim.date)

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

box = MyOVBox()
