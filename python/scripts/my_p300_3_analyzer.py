import numpy as np
from sklearn import discriminant_analysis
from sklearn.externals import joblib
import os
from os.path import expanduser

TARGET_CHANNEL = 0
NONTARGET_CHANNEL = 1- TARGET_CHANNEL
ROW_STATE = 'ROW'
COL_STATE = 'COL'

DIR = expanduser("~")
DIR = '/media/sf_desktop-tmp/P300-Speller-with-Groups-of-Letters/'
if not os.path.exists(DIR):
	DIR = u'/home/markham/Desktop/tmp/P300-Speller-with-Groups-of-Letters'

class Analyzer:
	def __init__(self, feature_tsv, stim_tsv, n_rows):
		self.N = n_rows
		self.feature_tsv = feature_tsv
		self.stim_tsv = stim_tsv

	def run(self):
		# Read tsv files
		with open(self.feature_tsv) as f:
			f.next()
			self.features = [Feature(line) for line in f]
		with open(self.stim_tsv) as f:
			f.next()
			self.stims = [Stim(line) for line in f]
		self.data = sorted(self.features + self.stims, key=lambda d: d.start)
		# for d in self.data: print d.start
		# Build model
		self._build_lda()
		# Organized trials, count classifications {correct,error}
		self.trials = self._build_trial_generator()
		classifications = [t.is_correct() for t in self.trials]
		return classifications

	def _build_trial_generator(self):
		trial = None
		for d in self.data:
			if isinstance(d, Stim):
				if 'OVTK_StimulationId_TrialStart' in d.stims:
					trial = Trial(self, d)
				if 'OVTK_StimulationId_TrialStop' in d.stims:
					yield trial
				elif trial:
					trial.add_stim(d)
			elif isinstance(d, Feature):
				trial.add_feature(d)
			else:
				raise Exception('Illegal type %s' % str(d))

	def _build_lda(self):
		targs = np.asarray([f.features for f in self.features if f.channel == TARGET_CHANNEL])
		nongs = np.asarray([f.features for f in self.features if f.channel == NONTARGET_CHANNEL])
		ytargs = np.ones((targs.shape[0]))
		ynongs = np.zeros((nongs.shape[0]))
		y = np.append(ytargs, ynongs)
		X = np.append(targs, nongs, axis=0)
		self.model = discriminant_analysis.LinearDiscriminantAnalysis()
		self.model.fit(X, y)

# A series of Visual Stimulations for which a single prediction should be made
class Trial:
	def __init__(self, analyzer, stim):
		self.analyzer = analyzer
		self.model = analyzer.model
		self.visual_state = None
		self.target_r = stim.target_r
		self.target_c = stim.target_c
		self.r_predictions = np.zeros(analyzer.N)
		self.c_predictions = np.zeros(analyzer.N)
		self.add_stim(stim)
	def add_stim(self, stim):
		if 'OVTK_StimulationId_VisualStimulationStart' in stim.stims:
			self.r = stim.r
			self.c = stim.c
			if stim.r != None and stim.c == None:
				self.visual_state = ROW_STATE
			elif stim.c != None and stim.r == None:
				self.visual_state = COL_STATE
			else:
				raise Exception('illegal stim for visual state')
		elif 'OVTK_StimulationId_VisualStimulationStop' in stim.stims: # may occur on same line as 'start'
			self.visual_state = None
	def add_feature(self, feature):
		if self.visual_state != None:
			prediction = self.model.predict(np.asarray(feature.features).reshape(1,-1))[0]
			increment = 1 if prediction == 1 else -1
			if self.visual_state == ROW_STATE:
				self.r_predictions[self.r] += increment
			elif self.visual_state == COL_STATE:
				self.c_predictions[self.c] += increment
	def finalize(self):
		self.row = np.argmax(self.r_predictions)
		self.col = np.argmax(self.c_predictions)
		return self.row, self.col
	def is_correct(self):
		self.finalize()
		return self.row == self.target_r and self.col == self.target_c

# A feature or stim, as received by the outputter algorithm box
class Datum:
	def __init__(self):
		self.start = float(self.start)
		self.channel = int(self.channel)

class Feature(Datum):
	def __init__(self, tsv):
		self.start, \
		self.channel, \
		self.features = tsv.split('\t', 2)
		Datum.__init__(self)
		self.features = [float(f) for f in self.features.split('\t')]

class Stim(Datum):
	def __init__(self, tsv):
		self.start, \
		self.channel, \
		self.target_r, \
		self.target_c, \
		self.r, \
		self.c, \
		self.stims = tsv.split('\t', 6)
		Datum.__init__(self)
		self.target_r = int(self.target_r) if self.target_r != 'nan' else None
		self.target_c = int(self.target_c) if self.target_c != 'nan' else None
		self.r = int(self.r) if self.r != 'nan' else None
		self.c = int(self.c) if self.c != 'nan' else None

if __name__ == '__main__':
	import sys
	features = sys.argv[1] if len(sys.argv) > 1 else '../../features.tsv'
	stims = sys.argv[2] if len(sys.argv) > 2 else '../../stims.tsv'
	n = int(sys.argv[3]) if len(sys.argv) > 3 else 2
	a = Analyzer(features, stims, n)
	res = a.run()
	print(res)
	if (len(sys.argv) > 4):
		with open(sys.argv[4],'w') as f:
			f.write('\n'.join([str(b) for b in res]))
