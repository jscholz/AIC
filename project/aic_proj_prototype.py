import numpy as np
from pylab import *

def entropy(x):
	pad = 1e-10
	xp = np.array(x) + pad
	xpmf = xp/np.sum(xp)
	# import ipdb;ipdb.set_trace()
	unif = np.ones(len(x))/len(x)
	norm = -np.sum(unif * np.log2(unif))
	return -np.sum(xpmf * np.log2(xpmf))/norm

def conf_func(x, k=2):
	# return 1-x ## original linear version
	return np.power(1 - np.power(x, k), 1./k)  ## ellipsoidal version

def confidence(x, alpha=0.75, beta=4):
	'''
	:param alpha: Baseline confidence in sentiment system as a whole
	'''

	out = alpha * conf_func(entropy(x), k=beta)

	return out

def print_review(x):
	flattened = flatten_multi_sent_reviews(x)
	print "Review distribution: \n", x,\
	 "\nflattened: ", flattened,\
	 "\nmean score: ", np.sum(flattened*np.arange(1,len(flattened)+1)),\
	 "\nconfidence: ", confidence(flattened), "\n"

def adjusted(raw, sentiment_dist):
	out =  raw + confidence(sentiment_dist) * (np.sum(np.arange(1,len(sentiment_dist)+1) * sentiment_dist) - raw)
	return out

def flatten_multi_sent_reviews(review):
	rev = np.atleast_2d(review)
	# return rev[0]
	out = np.sum(rev, axis=0)/rev.shape[0]
	return out

if __name__ == '__main__':

	# print entropy([0.2, 0.2, 0.2, 0.2, 0.2])
	# print entropy([0.4, 0.3, 0.2, 0.05, 0.05])
	# print entropy([1.0, 0., 0., 0.0, 0.0])

	# print_review([0.2, 0.2, 0.2, 0.2, 0.2])
	# print_review([0.4, 0.3, 0.2, 0.05, 0.05])
	# print_review([1.0, 0., 0., 0.0, 0.0])

	# print_review([0.2, 0.2, 0.2, 0.2, 0.2])
	# print_review([0.4, 0.3, 0.2, 0.05, 0.05])
	# print_review([0.0, 0., 1., 0.0, 0.0])
	# print_review([0.0, 0., 0.25, 0.0, 0.75])

	# print adjusted(2.0, [0.0, 0.0, 0.0, 0.0, 1.0]) # expect 3.5
	# print adjusted(2.0, [0.0, 1.0, 0.0, 0.0, 0.0]) # expect 2
	# print adjusted(2.0, [0.0, 0.5, 0.0, 0.0, 0.5]) # expect in between 

	# print adjusted(3.0, [0.2, 0.2, 0.2, 0.2, 0.2]) # expect r
	# print adjusted(5.0, [0.0, 0.0, 0.0, 1.0, 0.0]) # expect 4.5 ish

	## plot confidence weight function:
	# x = np.arange(0, 1, 0.005)
	# y = conf_func(x)
	# interactive(True)
	# plot(x,y)

	## amazon data
	# Super fun game, but so many glitches! The characters keep freezing or getting stuck. it's very irritating when it happens, and we've had to re- do levels several times.
	amazon_r1 = np.array([
		[.01, .01, .10, .79, 0.09],
		[.10, .55, 0.23, .10, .02],
		[.35, .51, .12, .01, .01]])

	# "Fifty Shades of Grey," which gingerly crosses over into the questionable subject mark, may not be the film some of the books readers were hoping to witness.
	rt_r1 = np.array([.14, .59, .23, .03, .01]) # rating: fresh

	# 'Despite its miniscule degree of ambiguity, the goal and outcomes of American Sniper are clear: a great man done a great thing for a great country.'
	rt_r2 = np.array([.01, .01, .04, .79, .15])	# rating: splat

	print "Amazon data (flattened):"
	print_review(amazon_r1)

	# (Yodelling Pickle) My twelve year-old niece asked for the Justin Bieber CD for Christmas, so I bought her this yodeling pickle. Nobody so far can tell the difference.
	# http://www.amazon.com/Accoutrements-11761-Yodelling-Pickle/dp/B0010VS078/ref=pd_sbs_indust_15?tag=apartmentth0a-20
	amazon_r4 = np.array([.06, .42, .45, .07, 0.1]) # actual rating: 5/5

	print "Rottentomatoes (flattened):"
	print_review(rt_r1) 
	print_review(rt_r2)

	print "Adjusted scores: "
	print "Amazon 1", adjusted(3.0, flatten_multi_sent_reviews(amazon_r1)) # expect 3-4 ish (closer to 2)
	print "Rottentomatoes 1", adjusted(4.0, flatten_multi_sent_reviews(rt_r1)) # expect <2.5 (splat)
	print "Rottentomatoes 1", adjusted(2.0, flatten_multi_sent_reviews(rt_r2)) # expect >2.5 (fresh)

	# import ipdb;ipdb.set_trace()