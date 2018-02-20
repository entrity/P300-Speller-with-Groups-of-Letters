#!/usr/bin/python2

# Reference: discriminant_analysis.LinearDiscriminantAnalysis
# http://scikit-learn.org/stable/modules/generated/sklearn.discriminant_analysis.LinearDiscriminantAnalysis.html#sklearn.discriminant_analysis.LinearDiscriminantAnalysis

import numpy as np
from sklearn import discriminant_analysis

TARGETS = '../target.tsv'
NONTARGETS = '../nontarget.tsv'

targs = np.loadtxt(TARGETS, delimiter='\t')
nongs = np.loadtxt(NONTARGETS, delimiter='\t')
ytargs = np.ones((targs.shape[0]))
ynongs = np.zeros((nongs.shape[0]))
y = np.append(ytargs, ynongs)
X = np.append(targs, nongs, axis=0)

model = discriminant_analysis.LinearDiscriminantAnalysis()
model.fit(X, y)

# Print training error
model.score(X, y)

model.coef_ # coefficients
model.get_params() # parameters
