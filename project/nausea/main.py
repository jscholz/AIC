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

from snlp_pipe import NLPPiper
from nausea_model import flatten_multi_sent_reviews, get_adjusted_score

def load_review(path):
	'''
	Loads the review at the specified path and returns a list
	contain each sentence of the review
	'''
	f = open(path)
	lines = f.readlines()
	f.close()

	# split into sentences
	sentences = " ".join(lines).split('.')
	return [sent+".\n" for sent in sentences if len(sent) > 0]

def find_reviews(rootdir, wexp=None):	
	if wexp is None:
		wexp = '*'
	path = rootdir + '/' + wexp

	return glob.glob(path)

if __name__ == '__main__':

	piper = NLPPiper()

	all_reviews = find_reviews('reviews/')

	# process all reviews
	raw_scores = []
	sa_scores = []
	adjusted_scores = []
	for review in all_reviews:
		# obtain review scores for each sentence in the review
		sentences = load_review(review)
		review_sa_scores = []
		for sent in sentences:
			piper.send_review(sent)
			output_str = piper.get_result_str()
			review_sa_scores.append(piper.parse_result_str(output_str))

		# obtain adjusted overall score
		review_dist = flatten_multi_sent_reviews(review_sa_scores)
		adjusted_score, sa_score = get_adjusted_score(3, review_dist)
		
		# add to list and continue
		sa_scores.append(sa_score)
		adjusted_scores.append(adjusted_score)


	import ipdb;ipdb.set_trace()	