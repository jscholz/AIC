import gzip
import simplejson
import ast

class Review(object):
	def __init__(self, text=None, raw=None, sa=None, adjusted=None):
		self.text = text
		self.raw = raw
		self.sa = sa
		self.adjusted = adjusted

	def __str__(self):
		out = ""
		if self.raw is not None:
			out += "raw score: %f\n" % self.raw
		if self.sa is not None:
			out += "sa score: %f\n" % self.sa
		if self.adjusted is not None:
			out += "adjusted score: %f\n" % self.adjusted
		if self.text is not None:
			out += "text:\n%s\n" % self.text
		return out

	def __repr__(self):
		return str(self)

def parse(filename, zipped=False):
	if zipped:
		f = gzip.open(filename, 'r')
	else:
		f = open(filename, 'r')
	entry = {}
	for l in f:
		l = l.strip()
		colonPos = l.find(':')
		if colonPos == -1:
			yield entry
			entry = {}
			continue
		eName = l[:colonPos]
		rest = l[colonPos+2:]
		entry[eName] = rest
	yield entry


def extract_reviews(filename, zipped=False, max_reviews=None):
	reviews = []
	i = 0
	for e in parse(filename, zipped=zipped):
		i += 1
		if max_reviews is not None and i >= max_reviews:
			break
		print "Parsing review %d" % i
		
		parsed = simplejson.dumps(e)
		if parsed != '{}':
			full_review = ast.literal_eval(parsed)
			review = Review(text=full_review['review/text'], raw=float(full_review['review/score']))
			# print review
			reviews.append(review)

	return reviews

if __name__ == '__main__':
	# rev = extract_reviews('reviews/example_review.txt', zipped=False)
	# rev = extract_reviews('reviews/Cell_Phones_&_Accessories.txt', zipped=False)
	rev = extract_reviews('reviews/Arts.txt.gz', zipped=True)
			
	import ipdb;ipdb.set_trace()
	