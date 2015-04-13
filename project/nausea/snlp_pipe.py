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

import subprocess
import numpy as np

class NLPPiper(object):
	"""
	Implements a simple pipe-based interface to the stanford NLP 
	sentiment analysis toolkit.  NLPPiper communicates via 
	Unix pipes to stdin/stdout with the NLP module, which is 
	spawned as a java subprocess.  
	Unfortunately, the SentimentPipeline tool does not send 
	and EOF or stop token when a parse is complete, which means
	that calling readline (a blocking call) past the end of the 
	available input will lock the caller.  NLPPiper implements
	a small workaround using a predefined stop query which
	gets sent with ever query.  We also implement a call-counter
	to keep the program from locking when attempting to read
	results before text has been sent (which will also lock).
	"""

	defaultcmd = 'java -cp \"stanford-corenlp-full-2015-01-29/*\" -mx5g edu.stanford.nlp.sentiment.SentimentPipeline -stdin -output PROBABILITIES'
	test_review = 'Nobody so far can tell the difference.\n'

	stopquery = 'stop\n'
	stopreply = [
		'(0 stop)\n', 
		'  0:  0.0070  0.0342  0.9210  0.0283  0.0096\n']

	def __init__(self, cmd=None):
		if cmd is None:
			cmd = NLPPiper.defaultcmd

		self.process = subprocess.Popen(cmd, 
			stdin=subprocess.PIPE, 
			stdout=subprocess.PIPE, 
			shell=True)

		# sync send_review and get_result_str calls (protects against locks)
		self._sr_calls = 0
		self._grs_calls = 0

	def send_review(self, text):
		'''
		Sends the provided text to the sentiment analysis module.
		'''
		self._sr_calls += 1
		self.process.stdin.write(text)
		self.process.stdin.write(self.stopquery)

	def get_result_str(self):
		'''
		Returns a list containing the raw result strings from the
		analysis module.  This list is read from buffered stdin, so 
		it will contain the results for all the reviews passed using
		send_review() since the last call to get_result_str().
		'''
		if self._grs_calls >= self._sr_calls:
			return
		self._grs_calls += 1

		lines = []
		while True:
			line = self.process.stdout.readline()
			if line == self.stopreply[0]:
				# if stop detected, clear the parse and exit
				nextline = self.process.stdout.readline()
				assert(nextline == self.stopreply[1])
				break
			else:
				lines.append(line)

		return lines

	def parse_result_str(self, lines):
		'''
		Parses the output from the SentimentPipeline module.
		For now we are only interested in the aggregate score
		probabilities at the root-node, and we ignore the result
		of the parse tree.

		The output for a single review is organized as follows:
		l1) The sentence parse tree in parantheses notation.
			E.G. for the query "Nobody so far can tell the difference.\n":
			'(0 (1 Nobody) (2 (3 (4 so) (5 far)) (6 (7 (8 can) (9 (10 tell) 
			 (11 (12 the) (13 difference)))) (14 .))))\n)
		l2-n) The sentiment scores for each node in the tree.
			E.G. the aggregate analysis for the root node is:
			'  0:  0.0218  0.1074  0.2754  0.5326  0.0629\n'

			Each score line contains parse node and scores as follows
			 [parse_node: prob(-2), prob(-1), prob(0), prob(1), prob(2)]
			 where prob(x) indicates the probability of sentiment x on the
			 scale -2:2.
		'''
		if len(lines) < 2:
			return None

		root_scores = [] 
		for sc in lines[1].split(':')[1].strip('\n').split(' '):
			try:
				root_scores.append(float(sc))
			except:
				pass
		assert(len(root_scores) == 5)
		return np.array(root_scores)

if __name__ == '__main__':	
	piper = NLPPiper()
	piper.send_review(NLPPiper.test_review)
	test_output_str =  piper.get_result_str()
	print piper.parse_result_str(test_output_str)
	import ipdb;ipdb.set_trace()
