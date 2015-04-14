#!/usr/bin/env python

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
'''

import glob
import time
import numpy as np
from matplotlib import pyplot, interactive, rc

from snlp_pipe import NLPPiper
from nausea_model import flatten_multi_sent_reviews, get_adjusted_score
from parser import extract_reviews

def get_review_sentences(text):
	'''
	Loads the review at the specified path and returns a list
	contain each sentence of the review
	'''
	# split into sentences and return with newlines
	sentences = text.split('.')
	return [sent+".\n" for sent in sentences if len(sent) > 0]

# def find_reviews(rootdir, wexp=None):	
# 	if wexp is None:
# 		wexp = '*'
# 	path = rootdir + '/' + wexp
# 	return glob.glob(path)

def _r2(x, y):
	"""Computes an r^2 statistic given x,y"""
	xbar = np.mean(x)
	ss_tot = np.sum(np.power(x-xbar,2))
	ss_res = np.sum(np.power(x-y,2))
	return 1-(ss_res/ss_tot)

def plot_output(raw_scores, sa_scores, adjusted_scores, human_rescores):
	review_data = np.vstack([
		raw_scores, sa_scores, adjusted_scores, human_rescores])
	review_data.T.sort(axis=0)

	font = {'family' : 'normal',
			'weight' : 'bold',
			'size'   : 18}
	rc('font', **font)
			
	# generate "regression to the mean" plot
	pyplot.figure()
	pyplot.ylim((0,6))
	pyplot.title('Review Score Adjustments')
	pyplot.plot(review_data.T)
	pyplot.legend(['Raw', 'Sentiment', 'NAUSEA', 'Human'], loc=4)
	pyplot.xlabel('Sorted Review Index')
	pyplot.ylabel('Score')
	cc_raw_sa = np.corrcoef(review_data[0,:], review_data[1,:])[0,1]
	cc_raw_adj = np.corrcoef(review_data[0,:], review_data[2,:])[0,1]
	pyplot.text(20, 5.5, 'Raw-Sentiment corr: %1.2f' % cc_raw_sa)
	pyplot.text(20, 5.1, 'Raw-Adjusted corr:   %1.2f' % cc_raw_adj)

	# import ipdb;ipdb.set_trace()

def plot_validation(raw_scores, sa_scores, adjusted_scores, human_rescores, max_reviews=5):
	review_data = np.vstack([
		raw_scores, sa_scores, adjusted_scores, human_rescores])
	font = {'family' : 'normal',
			'weight' : 'bold',
			'size'   : 18}
	rc('font', **font)
	colors = ['b','g','r','c','m','y']
			
	# generate validation plot
	n_bars = 4
	n_revs = min(review_data.shape[1], max_reviews)
	pyplot.figure()
	pyplot.ylim((0,6))
	ind = np.arange(n_revs)
	
	width = 1./n_bars - 0.1/n_bars
	for i in range(n_bars):
		pyplot.bar(ind + i*width, review_data[i,0:max_reviews], width, color=colors[i])
	pyplot.xticks(np.arange(n_revs)+width*n_bars/2, ['%d ' %i for i in np.arange(n_revs)+1])
	pyplot.legend(['Raw', 'Sentiment', 'NAUSEA', 'Human'], loc=0)
	pyplot.ylabel('Score')
	pyplot.xlabel('Review Index')

	import ipdb;ipdb.set_trace()

if __name__ == '__main__':
	max_reviews = 1500
	# all_reviews = extract_reviews('reviews/example_review.txt', 
	# 	zipped=False, max_reviews=max_reviews)
	# all_reviews = extract_reviews('~/Downloads/amazon_reviews/Arts.txt.gz', 
	# 	zipped=True, max_reviews=max_reviews)
	# all_reviews = extract_reviews('~/Downloads/amazon_reviews/Cell_Phones_&_Accessories.txt.gz', 
	# 	zipped=True, max_reviews=max_reviews)
	# all_reviews = extract_reviews('~/Downloads/amazon_reviews/Automotive.txt.gz', 
	# 	zipped=True, max_reviews=max_reviews)
	all_reviews = extract_reviews('/Users/jscholz/Downloads/amazon_reviews/Movies_&_TV.txt.gz', 
		zipped=True, max_reviews=max_reviews)
	# all_reviews = extract_reviews('reviews/7wonders.txt', 
		# zipped=False, max_reviews=max_reviews)

	# create piper to obtain sentiment analysis results	
	piper = NLPPiper()

	# process all reviews
	raw_scores = []
	sa_scores = []
	adjusted_scores = []
	human_rescores = []
	i = 0
	for review in all_reviews:
		print "Processing review %d... " % i,
		# obtain review scores for each sentence in the review
		sentences = get_review_sentences(review.text)
		review_sa_scores = []
		for sent in sentences:
			# import ipdb;ipdb.set_trace()
			piper.send_review(sent)
			output_str = piper.get_result_str()
			review_sa_scores.append(piper.parse_result_str(output_str))

		# obtain adjusted overall score
		raw_score = review.raw
		review_dist = flatten_multi_sent_reviews(review_sa_scores)
		adjusted_score, sa_score = get_adjusted_score(raw_score, review_dist)
		rescore = review.rescore if review.rescore is not None else 0.

		# plug into review struct
		review.sentiment = sa_score
		review.adjusted = adjusted_score
		
		# add to list and continue
		raw_scores.append(raw_score)
		sa_scores.append(sa_score)
		adjusted_scores.append(adjusted_score)
		human_rescores.append(rescore)

		print "adjusted score: %f" % adjusted_score
		i+=1

	print "raw scores: \n", raw_scores
	print "sentiment analysis scores: \n", sa_scores
	print "final adjusted scores: \n", adjusted_scores

	pyplot.interactive(True)
	plot_output(raw_scores, sa_scores, adjusted_scores, human_rescores)
	plot_validation(raw_scores, sa_scores, adjusted_scores, 
		human_rescores, max_reviews=5)

	import ipdb;ipdb.set_trace()
	