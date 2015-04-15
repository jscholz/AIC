import numpy as np
import csv
from matplotlib import pyplot, interactive, rc

def plot_review_hist(review_scores, good=False):
	colors = ['b', 'r']
	if good:
		color = colors[0]
	else:
		color = colors[1]
	counts, bins = np.histogram(review_scores, bins=range(1,7))
	pyplot.figure()
	n_bars = 1
	width = 1./n_bars - 0.1/n_bars
	pyplot.bar(range(1,6), counts, width, color=color)
	pyplot.xlim((1,6))
	pyplot.ylim((0,20))
	# import ipdb;ipdb.set_trace()

if __name__ == '__main__':
	
	scores = []
	with open('reviews/responses-raw.tsv', 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter='\t')
		for row in reader:
			scores.append([float(s) for s in row[1:]])

	scores = np.array(scores).T
	good_idxs = np.array([ 0,  6,  8,  9, 13, 15, 16, 19, 20, 21, 22, 23, 24])
	bad_idxs = np.array([ 1,  2,  3,  4,  5,  7, 10, 11, 12, 14, 17, 18, 25])

	pyplot.interactive(True)
	# import ipdb;ipdb.set_trace()
	for i in range(scores.shape[0]):
		print "%d: %s" % (i, "good" if i in good_idxs else "bad")
		plot_review_hist(scores[i,:], good=i in good_idxs)
	
	# print "good std: ", np.std(scores[good_idxs, :], axis=1)
	# print "bad std: ", np.std(scores[bad_idxs, :], axis=1)
	print "good std: ", np.std(scores[good_idxs, :])
	print "bad std: ", np.std(scores[bad_idxs, :])