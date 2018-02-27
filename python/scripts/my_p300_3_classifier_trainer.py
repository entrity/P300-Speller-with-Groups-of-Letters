import sys, os.path, os
from os.path import expanduser
import numpy as np
from sklearn import discriminant_analysis
from sklearn.externals import joblib

DIR = expanduser("~")
DIR = '/media/sf_desktop-tmp/P300-Speller-with-Groups-of-Letters/'
inputLbls = ('target', 'nontarget')
tsv = tuple([os.path.join(DIR,'%s.tsv') % lbl for lbl in inputLbls])
log = tuple([os.path.join(DIR,'%s.log') % lbl for lbl in inputLbls])
print 'tsv', tsv

class MyOVBox(OVBox):
	def __init__(self, d):
		OVBox.__init__(self)
		print("expanduser", DIR)
		print('dir', d)
		with open(os.path.join(DIR, 'explore.txt'), 'w') as f:
			print >> f, dir(self)
			print >> f, 'var:', self.var.keys()
			print >> f, 'setting', self.setting.keys()
		
	def initialize(self):
		print('Python version:', sys.version)
		for inputIndex in range(2):
			for arr in (tsv, log):
				if os.path.exists(arr[inputIndex]):
					os.remove(arr[inputIndex])
		return
		
	def process(self):
		global stimmap
		assert len(self.input) == 2
		for inputIndex in range(2):
			for chunkIndex in range( len(self.input[inputIndex]) ):
				chunk = self.input[inputIndex].pop()
				if type(chunk) == OVStreamedMatrixBuffer:
					with open(os.path.join(DIR,'tmp.txt'),'w') as f:
						print >> f, 'dir(chunk) :', dir(chunk), '\n'
						print >> f, 'chunk :', chunk, '\n'
						print >> f, 'type(chunk) :', type(chunk), '\n'
						print >> f, 'len :', len(chunk), '\n'
						print >> f, 'count :', 
						for i in range(90):
							print >> f, chunk.count(chunk[i]),
						print >> f, '\n'
						print >> f, 'startTime :', chunk.startTime, '\n'
						print >> f, 'endTime :', chunk.endTime, '\n'
					with open(log[inputIndex], 'a') as f:
						print >> f, chunk.startTime, '\t', chunk.endTime, '\t', chunk
					with open(tsv[inputIndex], 'a') as f:
						f.write('\t'.join(str(f) for f in chunk))
						f.write('\n')
				elif OVStreamedMatrixHeader == type(chunk):
					with open(os.path.join(DIR,'header-%d.txt' % inputIndex),'w') as f:
						print >> f, 'dir(chunk)', dir(chunk)
						print >> f, 'dimensionLabels', chunk.dimensionLabels
						print >> f, 'dimensionSizes', chunk.dimensionSizes
						print >> f, 'endTime', chunk.endTime
						print >> f, 'getBufferElementCount', chunk.getBufferElementCount()
						print >> f, 'getDimensionCount', chunk.getDimensionCount()
						print >> f, 'startTime', chunk.startTime
				else:
					print 'Received chunk of type ', type(chunk), " looking for StimulationSet"
		return
		
	# Create the lda model?
	def uninitialize(self):
		TARGETS = tsv[0]
		NONTARGETS = tsv[1]
		if os.path.exists(TARGETS) and os.path.exists(NONTARGETS):
			# Build model, save to file
			print('Building model...')
			targs = np.loadtxt(TARGETS, delimiter='\t')
			nongs = np.loadtxt(NONTARGETS, delimiter='\t')
			ytargs = np.ones((targs.shape[0]))
			ynongs = np.zeros((nongs.shape[0]))
			y = np.append(ytargs, ynongs)
			X = np.append(targs, nongs, axis=0)
			model = discriminant_analysis.LinearDiscriminantAnalysis()
			model.fit(X, y)
			joblib.dump(model, os.path.join(DIR, 'classifier.pkl'))
			print('Model saved.')
			# Print training error
			print('Score', model.score(X, y))
		else:
			sys.stderr.write("Missing one or more tsv files. Maybe you didn't let the recording run long enough to get stims and features for both classes?\n")
		return

box = MyOVBox(dir())
