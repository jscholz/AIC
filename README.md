
NAUSEA, short for "Numerical Adjustment Using Sentiment Entropy Analysis",
is a package for re-scoring numerical reviews using the output of a 
stochastic sentiment analysis pipeline.  Its intended application is for
massaging review scores on sites such as Amazon.com and Rottentomates.com
in which users provide both text and review scores (which don't always agree).
Typically the review text is for human consumption only, but with the advent 
of NLP tools for sentiment analysis, it is now possible to use this textual
information to refine the numerical evaluation of the reviewed products.  

NAUSEA implements a simple model for score adjustment which uses a non-linear 
entropy


This software was tested on a 2013 macbook pro running OSX 10.10.2


Requirements:
- python 2.7
	[pre-installed or apt-get install it]
- numpy (tested on 1.8.0)
	$ sudo pip install numpy
- matplotlib 
	$ sudo pip install matplotlib
- simplejson
	$ sudo pip install simplejson
- stanford-corenlp (http://nlp.stanford.edu/software/corenlp.shtml)
	$ wget http://nlp.stanford.edu/software/stanford-corenlp-full-2015-01-29.zip

Preparing to use Nausa:
After downloading stanford-corenlp, move/copy it to the nausea directory so 
that the python pipe interface (snlp_pipe.py) can find it.  

Reviews in the format we use can be obtained from the follow link:
http://snap.stanford.edu/data/web-Amazon.html
These are private, so you'll probably have to contact Julian McAuley 
(jmcauley@cs.stanford.edu) to obtain access (he was nice to us!).

Running Nausea:
Open main.py and specify the desired review file and maximum number
of reviews to load.

Then execute the following
$ python main.py

If all goes well, this command will load and parse the reviews, 
obtain sentiment analysis rankings from stanford-corenlp's SA module,
and run the NAUSEA model to adjust the review scores.

Results will be plotted for you to show your boss.  
