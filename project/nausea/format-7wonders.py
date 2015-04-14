import csv
import sys

with open('reviews/unformated-7wonders.tsv','r') as csvfile:
  reader = csv.DictReader(csvfile,delimiter="\t")
  for row in reader:
    print "review/score: "+str(float(row['review/score']))
    print "review/rescore: "+str(float(row['review/rescore']))
    print "review/text: "+row["review/text"]
    print ""
