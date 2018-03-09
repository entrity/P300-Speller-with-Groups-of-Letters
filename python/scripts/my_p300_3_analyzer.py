import pdb

import numpy as np
from sklearn import discriminant_analysis
from sklearn.externals import joblib
import os
from os.path import expanduser
import re

TARGET_CHANNEL = 0
NONTARGET_CHANNEL = 1- TARGET_CHANNEL

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
			self.stims = [Stim(line) for line in f if len(line.strip())]
		self.data = sorted(self.features + self.stims, key=lambda d: d.start)
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
		self.lda_score = self.model.score(X,y)
		print('score %f' % self.lda_score)

class SegmentAccumulator:
	def __init__(self, analyzer):
		self.predictions = np.zeros(analyzer.N)
		self.stim_val = None
	def add_prediction(self, is_target):
		increment = 1 if is_target else -1
		self.predictions[self.stim_val] += increment

# A series of Visual Stimulations for which a single prediction should be made
class Trial:
	i = 0

	def __init__(self, analyzer, stim):
		Trial.i += 1
		self.analyzer = analyzer
		self.model = analyzer.model
		self.selected_accumulator = None
		self.label = None
		self.target_r = stim.target_r
		self.target_c = stim.target_c
		self.row = SegmentAccumulator(analyzer)
		self.col = SegmentAccumulator(analyzer)
		self.add_stim(stim)
		self.last_stim = None
	def add_stim(self, stim):
		self.last_stim = stim
		for name in stim.stims:
			m = re.match(r'^OVTK_StimulationId_Label_(\w+)', name)
			if m:
				lbl = int(m.group(1), 16) - 1
				if lbl >= 6:
					lbl -= 6
					self.col.stim_val = lbl
					self.selected_accumulator = self.col
				else:
					self.row.stim_val = lbl
					self.selected_accumulator = self.row
			# elif name == 'OVTK_StimulationId_VisualStimulationStop' in stim.stims: # may occur on same line as 'start'
			# 	self.selected_accumulator = None
	def add_feature(self, feature):
		# if self.selected_accumulator != None:
			is_target = self.model.predict(np.asarray(feature.features).reshape(1,-1))[0]
			# pdb.set_trace()
			# if is_target != 1-feature.channel:
			# 	print 'ERR'
			# 	sys.exit(8)
			self.selected_accumulator.add_prediction(is_target)
		# else:
			# pdb.set_trace()
	def finalize(self):
		self.predicted_row = np.argmax(self.row.predictions)
		self.predicted_col = np.argmax(self.col.predictions)
		# print(self.target_r, self.target_c, 'row pred', self.row.predictions)
		return self.predicted_row, self.predicted_col
	def is_correct(self):
		self.finalize()
		return self.predicted_row == self.target_r and self.predicted_col == self.target_c

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
		try:
			self.start, \
			self.channel, \
			self.target_r, \
			self.target_c, \
			self.r, \
			self.c, \
			self.stims = tsv.split('\t', 6)
		except ValueError as ex:
			print tsv
			raise ex
		self.stims = [s.strip() for s in self.stims.split('\t')]
		Datum.__init__(self)
		self.target_r = int(self.target_r) if self.target_r != 'nan' else None
		self.target_c = int(self.target_c) if self.target_c != 'nan' else None
		self.r = int(self.r) if self.r != 'nan' else None
		self.c = int(self.c) if self.c != 'nan' else None
	def __str__(self):
		return '%10f %d (%s %s) [%s %s] | %s' % (self.start, self.channel, str(self.target_r), str(self.target_c), str(self.r), str(self.c), ' '.join(self.stims))

if __name__ == '__main__':
	import sys
	featurestsv = sys.argv[1] if len(sys.argv) > 1 else '../../features.tsv'
	stimstsv = sys.argv[2] if len(sys.argv) > 2 else '../../stims.tsv'
	print(featurestsv)
	n = int(sys.argv[3]) if len(sys.argv) > 3 else 2
	a = Analyzer(featurestsv, stimstsv, n)
	res = a.run()
	print(res)
	correct_selections = sum(int(x) for x in res)
	print('correct selections: %d / %d   (%f)' % (correct_selections, len(res), float(correct_selections)/len(res)))

	if n == 2:
		correct_char = correct_selections / 3.0
		false0 = len([b for b in res[0::3] if b == False])
		false1 = len([b for b in res[1::3] if b == False])
		false2 = len([b for b in res[2::3] if b == False])
		discounted_output = correct_char - 2 * (false2) - 2 / 3.0 * (false0 + false1)
	else:
		correct_char = correct_selections
		falses = len([b for b in res if b == False])
		discounted_output = correct_char - 2 * falses
	print('dchar %.3f' % discounted_output)


	interface = sys.argv[5] if len(sys.argv) > 5 else os.path.basename(os.path.dirname(stimstsv))
	if re.search('emg', interface): # 2x2x1x30 x (0.3+1.5)
		seconds = 2*2*1*30 * (0.3+1.5)
	elif re.search('2x2', interface): # 2x2x4x30 x (0.2+0.1)
		seconds = 2*2*4*30 * (0.2+0.1)
	elif re.search('6x6', interface): # 6x6x4x10 x (0.2+0.1)
		seconds = 6*6*4*10 * (0.2+0.1)
	else:
		print('ERR: unknown interface', interface)
		sys.exit(7)
	throughput = discounted_output / seconds

	if (len(sys.argv) > 4):
		with open(sys.argv[4],'a') as f:
			f.write('%d\t' % n)
			f.write('\t'.join(sys.argv[5:]))
			f.write('\t%s' % stimstsv)
			f.write('\n')
			f.write('%15s %15s %15s %15s %15s %15s \n' % ('interface', 'lda score', 'correct sel', 'correct char', 'discounted outp', 'throughput'))
			f.write('%15s %15f %15f %15f %15f %15f \n' % (interface, a.lda_score, correct_selections, correct_char, discounted_output, throughput))
			f.write('\t'.join([str(b) for b in res]))
			f.write('\n\n')
