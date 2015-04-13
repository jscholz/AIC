# Copyright (c) 2008-2012, Georgia Tech Research Corporation
# All rights reserved.
#
# Author(s): Jonathan Scholz <jkscholz@gatech.edu>
# Georgia Instutiute of Technology
#
# This file is provided under the following "BSD-style" License:
#
#   Redistribution and use in source and binary forms, with or
#   without modification, are permitted provided that the following
#   conditions are met:
#
#  * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#
#  * Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the following
#     disclaimer in the documentation and/or other materials provided
#     with the distribution.
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
#   CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
#   INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
#   MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#   DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
#   AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#   LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
#   ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#   POSSIBILITY OF SUCH DAMAGE.

'''
@title Entropy-Based Refinment of Textual Review Scores Using Sentiment Analysis
Created on April 10, 2015

@author: Jonathan Scholz
@author: Kaushik Subramanian
@author: Chad Stolper


Implements NAUSEA model, short for "numerical adjustment using
sentiment entropy analysis".  The purpose of this model is to
refine the numerical scores provided for short textual reviews,
e.g. from Rottentomatoes or Amazon, using the probabilistic 
output of modern sentiment-analysis tools.  

The adjustment performs an entropy-weighted mean of the raw
score and the analysis score.  
'''

import numpy as np
from pylab import *


def entropy(x):
	'''
	Computes the entropy of the discrete vector x.
	:param x: A numpy array representing a normalized
		discrete (a.k.a. categorical) distribution
	:return: The distribution entropy
	'''
	pad = 1e-10
	xp = np.array(x) + pad
	xpmf = xp/np.sum(xp)
	unif = np.ones(len(x))/len(x)
	norm = -np.sum(unif * np.log2(unif))
	return -np.sum(xpmf * np.log2(xpmf))/norm

def conf_func(x, beta):
	'''
	The core confidence-function in the NAUSEA model.
	This is a function which maps entropy to a subjective notion
	of confidence in the mean score of a distribution.  
	This was initially just negatively proportional to entropy, 
	such that confidence fell off linear with increasing entropy.
	However, we later changed it to a "radial norm" (?) in order to 
	decrease its sensitivity at low entropy values.  I.E. we 
	wanted the bias from the analysis to not be over-penalized
	for small amounts of uncertainty [~0-0.4].
	:param beta: The power of the norm.  Higher values closer to 
		box function, which flattens the response to entropy 
		(i.e. makes it closer to constant at 1).  Lower values
		(min 1) push towards the negative identity function.
	'''
	# return 1-x ## original linear version
	return np.power(1 - np.power(x, beta), 1./beta)  ## ellipsoidal version

def confidence(x, alpha=0.75, beta=4):
	'''
	:param x: The review distribution (1x5 array)
	:param alpha: Baseline confidence in sentiment system as a whole
	:param beta: confidence function parameter (higher values penalize
		higher entropy less in confidence score)
	'''
	out = alpha * conf_func(entropy(x), beta=beta)
	return out

def print_review_dist(x):
	'''
	Prints the review PDF and associated confidence.
	'''
	flattened = flatten_multi_sent_reviews(x)
	print "Review distribution: \n", x,\
	 "\nflattened: ", flattened,\
	 "\nmean score: ", np.sum(flattened*np.arange(1,len(flattened)+1)),\
	 "\nconfidence: ", confidence(flattened), "\n"

def flatten_multi_sent_reviews(review):
	'''
	Compresses multi-sentence review distributions into a single
	vector.  Currently takes an unweighted average.
	:param review: A 2D array containing a multi-sentence review distribution
	'''
	rev = np.atleast_2d(review)
	out = np.sum(rev, axis=0)/rev.shape[0]
	return out

def get_adjusted_score(raw, sentiment_dist, scores=None):
	'''
	Returns the final adjusted score using the provided raw score 
	and given sentiment distribution.  The output is a linear combination
	of the raw score and the expectation of the sentiment analysis
	score, weighted by analysis confidence.  

	:param raw: The raw score provided with the review
	:param sentiment_dist: The sentiment distribution for the 
		associated review text
	'''
	if scores is None:
		scores = np.arange(1, len(sentiment_dist)+1)

	sa_score = np.sum(scores * sentiment_dist)
	adjusted_score = raw + confidence(sentiment_dist) * (sa_score - raw)
	return adjusted_score, sa_score
