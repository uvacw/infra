#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
from io import open
import json
from pymongo import MongoClient, Connection, TEXT
import argparse
import ConfigParser
from collections import Counter, defaultdict
import sys
from nltk.stem import SnowballStemmer
from itertools import combinations, chain
import ast
from numpy import log
from gensim import corpora, models, similarities
import numpy as np
from sklearn.metrics import pairwise_distances
from scipy.spatial.distance import cosine
from sklearn.decomposition import PCA
from sklearn import preprocessing

import os



#################################
# TODO

# evtl k-means clustering inbouwen:
# http://scikit-learn.org/stable/auto_examples/document_clustering.html#example-document-clustering-py

################



# read config file and set up MongoDB
config = ConfigParser.RawConfigParser()
config.read('config.conf')
dictionaryfile=config.get('files','dictionary')
networkoutputfile=config.get('files','networkoutput')
lloutputfile=config.get('files','loglikelihoodoutput')
cosdistoutputfile=config.get('files','cosdistoutput')
compscoreoutputfile=config.get('files','compscoreoutput')
databasename=config.get('mongodb','databasename')
collectionname=config.get('mongodb','collectionname')
collectionnamecleaned=config.get('mongodb','collectionnamecleaned')
client = MongoClient(config.get('mongodb','url'))
db = client[databasename]
collection = db[collectionname]
collectioncleaned = db[collectionnamecleaned]



print "Ensure that the articles are properly indexed..."
collectioncleaned.ensure_index([("text", TEXT)], cache_for=300,default_language="nl",language_override="nl")
print "Done building index."



def stemmed(text,language):
	stemmer= SnowballStemmer(language)
	tas=text.split()
	text=""
	for word in tas:
		text=" ".join((text,stemmer.stem(word)))
	return text.lstrip()



def split2ngrams(txt, n):
	if n==1:
		return txt.split()
	else:
		return [tuple(txt.split()[i:i+n]) for i in range(len(txt.split())-(n-1))]


def frequencies_nodict():
    '''
    returns a counter object of word frequencies
    '''
    if ngrams!= 1:
         print "This function does not make sense to run with ngrams, ignoring the argument."

    # .replace is nodig omdat we ervan uitgaan dat alle spaties in de tekst door _ zijn vervangen (met de clean-functie)
    #knownwords = set([line.strip().replace(" ","_").lower() for line in open(dictionaryfile,mode="r",encoding="utf-8")])
    # we moeten deze woorden natuurlijk ook stemmen als we collection_cleaned hebben gestemd
    #stemmer=SnowballStemmer("dutch")
    #knownwords = set([stemmer.stem(line.strip().replace(" ","_").lower()) for line in open(dictionaryfile,mode="r",encoding="utf-8")])
    
    if stemming==0:
	    knownwords = set([line.strip().replace(" ","_").lower() for line in open(dictionaryfile,mode="r",encoding="utf-8")])
    else:
	    knownwords = set([stemmed(line.strip().replace(" ","_").lower(),stemming_language) for line in open(dictionaryfile,mode="r",encoding="utf-8")])

    all=collectioncleaned.find(subset,{"text": 1, "_id":0})
    aantal=all.count()
    #print all[50]["text"]
    unknown=[]
    i=0
    for item in all:
       i+=1
       print "\r",i,"/",aantal," or ",int(i/aantal*100),"%",
       sys.stdout.flush()

       if stemming==0:
	       unknown+=[woord for woord in item["text"].split() if woord not in knownwords]
       else:
	       unknown+=[woord for woord in stemmed(item["text"],stemming_language).split() if woord not in knownwords]

    c=Counter(unknown)

    return c



def frequencies():
    '''
    returns a counter object of word frequencies
    '''
    
    all=collectioncleaned.find(subset,{"text": 1, "_id":0})
    aantal=all.count()
    # print all[50]["text"]
    c=Counter()
    i=0
    for item in all:
       i+=1
       print "\r",i,"/",aantal," or ",int(i/aantal*100),"%",
       sys.stdout.flush()
       #c.update([woord for woord in item["text"].split()])
       if stemming==0:
	       c.update([woord for woord in split2ngrams(item["text"],ngrams)]) 
       else:
	       c.update([woord for woord in split2ngrams(stemmed(item["text"],stemming_language),ngrams)])  
    return c






def coocnet(n,minedgeweight):
    ''' 
    n = top n words
    minedgeweight = minimum number of co-occurances (=edgeweight) to be included
    '''


    '''
    TODO
    
    GIVE THE OPTION TO DETERMINE WHAT HAS TO BE INCLUDED BASED ON LOGLIKELIHOOD ETC INSTEAD OF RAW FREQUENCIES
    '''
    
    cooc=defaultdict(int)
    
    print "Determining the",n,"most frequent words...\n"
    c=frequencies()
    topnwords=set([a for a,b in c.most_common(n)])
   
    all=collectioncleaned.find(subset,{"text": 1, "_id":0})
    aantal=all.count()
    
    print "\n\nDetermining the cooccurrances of these words with a minimum cooccurance of",minedgeweight,"...\n"
    i=0
    for item in all:
        i+=1
        print "\r",i,"/",aantal," or ",int(i/aantal*100),"%",
        #words=item["text"].split()

	if stemming==0:
		words=split2ngrams(item["text"],ngrams)
	else:
		words=split2ngrams(stemmed(item["text"],stemming_language),ngrams)

        wordsfilterd=[w for w in words if w in topnwords]		
        uniquecombi = set(combinations(wordsfilterd,2))
        for a,b in uniquecombi:
            if (b,a) in cooc:
                continue
            else:
                if a!=b:
                    cooc[(a,b)]+=1


    with open(networkoutputfile,mode="w",encoding="utf-8") as f:
        f.write("nodedef>name VARCHAR, width DOUBLE\n")
        algenoemd=[]
        verwijderen=[]
        for k in cooc:
                if cooc[k]<minedgeweight:
                        verwijderen.append(k)
                else:
                        if k[0] not in algenoemd:
                                #f.write(k[0]+","+str(c[k[0]])+"\n")
                                f.write(unicode(k[0])+","+unicode(c[k[0]])+"\n")
                                algenoemd.append(k[0])
                        if k[1] not in algenoemd:
                                #f.write(k[1]+","+str(c[k[1]])+"\n")
                                f.write(unicode(k[1])+","+unicode(c[k[1]])+"\n")
                                algenoemd.append(k[1])
        for k in verwijderen:
                del cooc[k]

        f.write("edgedef>node1 VARCHAR,node2 VARCHAR, weight DOUBLE\n")
        for k, v in cooc.iteritems():
                # next line is necessary for the case of ngrams (we want the INNER TUPLES (the ngrams) become strings
                k2=[unicode(partofngram) for partofngram in k]
                regel= ",".join(k2)+","+str(v)
                f.write(regel+"\n")

    print "\nDone. Network file written to",networkoutputfile
    





def llcompare(corpus1,corpus2,llbestand):
	# using the same terminology as the cited paper:
	# a = freq in corpus1
	# b = freq in corpus2
	# c = number of words corpus1
	# d = number of words corpus2
	# e1 = expected value corpus1
	# e2 = expected value corpus2

	c = len(corpus1)
	d = len(corpus2)
	ll={}
	e1dict={}
	e2dict={}
	
	for word in corpus1:
		a=corpus1[word]
		try:
			b=corpus2[word]
		except KeyError:
			b=0
		e1 = c * (a + b) / (c + d)
		e2 = d * (a + b) / (c + d)
		# llvalue=2 * ((a * log(a/e1)) + (b * log(b/e2)))
		# if b=0 then (b * log(b/e2)=0 and NOT nan. therefore, we cannot use the formula above
		if a==0:
			part1=0
		else:
			part1=a * log(a/e1)
		if b==0:
			part2=0
		else:		
			part2=b * log(b/e2)
		llvalue=2*(part1 + part2)
		ll[word]=llvalue
		e1dict[word]=e1
		e2dict[word]=e2
	
	for word in corpus2:
		if word not in corpus1:
			a=0
			b=corpus2[word]
			e2 = d * (a + b) / (c + d)
			llvalue=2 * (b * log(b/e2))
			ll[word]=llvalue
			e1dict[word]=0
			e2dict[word]=e2
	print "Writing results..."
	with open(llbestand, mode='w', encoding="utf-8") as f:
            f.write("ll,word,freqcorp1,expectedcorp1,freqcorp2,expectedcorp2\n")
            for word,value in sorted(ll.iteritems(), key=lambda (word,value): (value, word), reverse=True):
                    # print value,word
                    try:
                            freqcorp1=corpus1[word]
                    except KeyError:
                            freqcorp1=0
                    try:
                            freqcorp2=corpus2[word]
                    except KeyError:
                            freqcorp2=0
                    e1=str(e1dict[word])
                    e2=str(e2dict[word])
                    f.write(str(value)+","+word+","+str(freqcorp1)+","+e1+","+str(freqcorp2)+","+e2+"\n")
	print "Output written to",llbestand



def ll():
    corpus1=frequencies()
    print len(corpus1)
    global subset
    subsetbak=subset
    subset=subset2
    corpus2=frequencies()
    print len(corpus2)
    subset=subsetbak
    llcompare(corpus1,corpus2,lloutputfile)




def lda(ntopics,minfreq):
    c=frequencies()
    all=collectioncleaned.find(subset,{"text": 1, "_id":0})
    
    
    if stemming ==0:
	    # oude versie zonder ngrams: texts =[[word for word in item["text"].split()] for item in all]
	    texts =[[word for word in split2ngrams(item["text"],ngrams)] for item in all]
    else:
	    texts =[[word for word in split2ngrams(stemmed(item["text"],stemming_language),ngrams)] for item in all]
    # unicode() is neccessary to convert ngram-tuples to strings
    texts =[[unicode(word) for word in text if c[word]>=minfreq] for text in texts]
    
    # Create Dictionary.
    id2word = corpora.Dictionary(texts)

    # Creates the Bag of Word corpus.
    mm =[id2word.doc2bow(text) for text in texts]
    # Trains the LDA models.
    lda = models.ldamodel.LdaModel(corpus=mm, id2word=id2word, num_topics=ntopics, update_every=1, chunksize=10000, passes=1)
    # Prints the topics.
    for top in lda.print_topics(): 
        print "\n",top



def tfcospca(n,file,comp,varimax):
	'''
	n = N most frequent words to include
	file = alternative to n, use words from inputfile file
	comp = number of components or, if 0<n<1, min eigenvalue of each component
	varimax = bool to indicate whether a varimax rotation should be performed 
	'''
	
	if n>0 and file=="":
		c=frequencies()
		topnwords=[a for a,b in c.most_common(n)]
	elif n==0 and file!="":
		topnwords=[line.strip().lower() for line in open(file,mode="r",encoding="utf-8")]
	
	#all=collectioncleaned.find(subset,{"text": 1, "_id":0})
	# We moeten meer info hebben om de dataset met factorscores op te slaan
	all=collectioncleaned.find(subset,{"text": 1, "_id":1, "source":1})
	# TF=np.empty([n,n-1])
	docs=[]
	foroutput_source=[]
	foroutput_firstwords=[]
	foroutput_id=[]
	for item in all:
		foroutput_firstwords.append(item["text"][:20])
		foroutput_source.append(item["source"])
		foroutput_id.append(item["_id"])
		if stemming==0:
			c_item=Counter(split2ngrams(item["text"],ngrams))
		else:
			c_item=Counter(split2ngrams(stemmed(item["text"],stemming_language),ngrams))
		tf_item=[]
		for word in topnwords:
			tf_item.append(c_item[word])
		docs.append(tf_item)
	TF=np.array(docs).T
	print "\n\nCreated a {} by {} TF-document matrix which looks like this:".format(*TF.shape)
	print TF
	COSDIST = 1-pairwise_distances(TF, metric="cosine") 
	print "\nAs a {} by {} cosine distance matrix, it looks like this:".format(*COSDIST.shape)
	print COSDIST

	print "\nConducting a principal component analysis..."
	# method following http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html
	pca = PCA(n_components=comp)
	# volgende regel is eigenlijk overbodig, zouden niet moeten standardiseren (alles toch op dezelfde schaal gemeten + cosinus-transformatie gedaan), maar in het kader van vergelijkbaarheid met SPSS/STATA/R-output doen we het toch...
	# COSDIST-preprocessing.scale(COSDIST)
	pca.fit(COSDIST)
	# wel te repiceren in stata met pca *, components(3) covariance , SPSS Heeft wat afwijkingen maar klopt in principe ook als je covariance ipv correlation matrix kiest
	
	print "\nExplained variance of each component:",pca.explained_variance_ratio_,"\n"
	#loadings= pca.transform(COSDIST).tolist()
	#print len(pca.transform(COSDIST).tolist())
	
	loadings= pca.components_.T.tolist()   # let ook hier op het transposen 
	if varimax:
		loadings=rotvarimax(pca.components_.T).tolist()
		print "\nThe rotated component loadings (varimax) are:"

	else:
		loadings= pca.components_.T.tolist()   # let ook hier op het transposen 
		print "\nThe component loadings are:"


	i=0
	for row in loadings:
		print topnwords[i],"\t\t",
		print '\t'.join(["{:.3f}".format(loading) for loading in row]) 
		i+=1
	i=0
	
	
	
	print "\n\nThe transformed scores are:"
	
	# DIT HIER KLOPT NIET (iig vlgs SPSS/STATA):
	# scores=pca.transform(COSDIST).tolist()
	# Dus maar zelf doen:
	
	scores=np.dot(COSDIST,loadings)
	
	for row in scores:
		print topnwords[i],"\t\t",
		print '\t'.join(["{:.3f}".format(loading) for loading in row]) 
		i+=1
	
	# save loadings to a dataset
	
	print "\nFor further analysis, a dataset with the component loadings for each document is saved to",compscoreoutputfile
	i=0
	
	# DAN IS DUS OOK DIT FOUT:
	# scores=pca.transform(TF.T).tolist()
	# nieuwe oplossing:
	
	scoresperdoc=np.dot(TF.T,loadings)

	
	with open(compscoreoutputfile,"w",encoding="utf-8") as fo:
		for row in scoresperdoc:
			fo.write(unicode(foroutput_id[i])+","+foroutput_source[i]+","+foroutput_firstwords[i]+",")
			fo.write(','.join(["{:0.3f}".format(loading) for loading in row]))
			fo.write("\n")
			i+=1

	print "\nFor further analysis, a copy of the cosine distance matrix is saved to",cosdistoutputfile
	# hiervoor heb je numpy > 1.7 nodig (vanwege header)
	#np.savetxt(cosdistoutputfile,COSDIST,fmt=str("%.6f"),delimiter=",",header=",".join(topnwords))
	# om te voorkomen dat numpy 1.7 of hoger nodig is, workaround zonder "header"
	np.savetxt(cosdistoutputfile+"TEMP",COSDIST,fmt=str("%1.6f"),delimiter=",")
	with open(cosdistoutputfile,"w",encoding="utf-8") as fo:
		fo.write(",".join(topnwords))
		fo.write("\n")
		with open (cosdistoutputfile+"TEMP","r",encoding="utf-8") as fi:
			fo.write(fi.read())
	os.remove(cosdistoutputfile+"TEMP")


def rotvarimax(Phi, gamma = 1, q = 20, tol = 1e-6):
    from numpy import eye, asarray, dot, sum, diag
    from numpy.linalg import svd
    p,k = Phi.shape
    R = eye(k)
    d=0
    for i in xrange(q):
        d_old = d
        Lambda = dot(Phi, R)
        u,s,vh = svd(dot(Phi.T,asarray(Lambda)**3 - (gamma/p) * dot(Lambda, diag(diag(dot(Lambda.T,Lambda))))))
        R = dot(u,vh)
        d = sum(s)
        if d/d_old < tol: break
    print "The following Component Transformation Matrix has been determined for the rotation:"
    print R
    return dot(Phi, R)














def main():
    parser=argparse.ArgumentParser("This program is part of VETTE NAAM BEDENKEN EN ZO VERDER")
    group=parser.add_mutually_exclusive_group()
    group.add_argument("--frequencies",metavar="N",help="List the N most common words")
    group.add_argument("--frequencies_nodict",metavar="N",help="List the N most common words, but only those which are NOT in the specified dictionary (i.e., list all non-dutch words)")
    group.add_argument("--lda",metavar=("N1","N2"),help="Perform a Latent Diriclet Allocation analysis  based on words with a minimum frequency of N1 and generate N2 topics",nargs=2)
    group.add_argument("--ll",help="Compare the loglikelihood of the words within the subset with the whole dataset",action="store_true")
    group.add_argument("--network",metavar=("N1","N2"),help="Create .gdf network file to visualize word-cooccurrances of the N1 most frequently used words with a minimum edgeweight of N2. E.g.: --network 200 50",nargs=2)
    group.add_argument("--pca",metavar=("N1","N2"),help="Create .a document-tf- matrix with all selected articles and the N1 most frequent words, transform it to a cosine dissimilarity matrix and carry out a principal component analysis, resulting in N2 components",nargs=2)
    group.add_argument("--pca_ownwords",metavar=("FILE","N"),help="Create .a document-tf- matrix with all selected articles and the words stored in FILE (UTF-8, one per line), transform it to a cosine dissimilarity matrix and carry out a principal component analysis, resulting in N components. If 0<N<1, then all components, then all components with an explained variance > N are listed.",nargs=2)

    group.add_argument("--search", metavar="SEARCHTERM",help="Perform a simple search, no further options possible. E.g.:  --search hema")
    parser.add_argument("--subset", help="Use MongoDB-style .find() filter in form of a Python dict. E.g.:  --subset=\"{'source':'de Volkskrant'}\" or --subset=\"{'\\$text':{'\\$search':'hema'}}\" or a combination of both: --subset=\"{'\\$text':{'\\$search':'hema'}}\",'source':'de Volkskrant'}\"")
    parser.add_argument("--subset2", help="Compare the first subset specified not to the whole dataset but to another subset. Only evaluated together with --ll.")
    parser.add_argument("--varimax", help="If specified with --pca or --pca_ownwords, a varimax rotation is performed",action="store_true")
    parser.add_argument("--ngrams",metavar="N",help="By default, all operations are carried oud on single words. If you want to use bigrams instead, specify --ngram=2, or 3 for trigrams and so on.",nargs=1)
    parser.add_argument("--stemmer",metavar="language",help='Invokes the snowball stemming algorithm. Specify the language: --stemmer="dutch"',nargs=1)
    # parser.add_argument("--search", help="Use MongoDB-style text search in form of a Python dict. E.g.:  --subset \"{'\\$text':{'\\$search':'hema'}}\"")
    



    '''
    TODO TEXT SEARCH
    ---search
    FILTEREN OP ZOEKTERMEN
    http://blog.mongodb.org/post/52139821470/integrating-mongodb-text-search-with-a-python-app
    '''


    args=parser.parse_args()
    global ngrams
    if not args.ngrams:
    	ngrams=1
    else:
    	ngrams=int(args.ngrams[0])

    global stemming
    global stemming_language
    if not args.stemmer:
	    stemming=0
    else:
	    stemming=1
	    stemming_language=args.stemmer[0]


    global subset
    if not args.subset:
        subset={}
    else:
        try:
            subset=ast.literal_eval(args.subset)
        except:
            print "You specified an invalid filter!"
            sys.exit()

        if type(subset) is not dict:
            print "You specified an invalid filter!"
            sys.exit()

        print "Analysis will be based on a dataset filterd on",subset


    global subset2
    if not args.subset2:
        subset2={}
    else:
        try:
            subset2=ast.literal_eval(args.subset2)
        except:
            print "You specified an invalid filter for subset2!"
            sys.exit()

        if type(subset2) is not dict:
            print "You specified an invalid filter for subset2!"
            sys.exit()
        print  "Subset to compare with is",subset2


    if args.search:
        query=db.command('text',collectionnamecleaned,search=args.search, language="nl")
        print "Finished with search,",len(query["results"]),"matching articles found."
        print "Some stats:",query["stats"]
        print "relevance\tsource\tdate"
        for results in query["results"]:
            print results["score"],"\t",results["obj"]["source"],"\t",results["obj"]["date"]


    if args.ll:
        ll()

    if args.lda:
        lda(int(args.lda[1]),int(args.lda[0]))

    if args.pca:
        tfcospca(int(args.pca[0]),"",float(args.pca[1]),args.varimax)
        
    if args.pca_ownwords:
        tfcospca(0,args.pca_ownwords[0],float(args.pca_ownwords[1]),args.varimax)



    if args.frequencies:
        c=frequencies()
        for k,v in c.most_common(int(args.frequencies)):
            print v,"\t",k
            # willen we de woorden nog opslaan? zo ja, iets toevoegen zoals hieronder. of met set() als we de duplicaten eruit willen halen
            '''
            with open(outputbestand,"w", encoding="utf-8") as f:
            for woord in belangrijk:
            f.write(woord+"\n")
            '''



    if args.frequencies_nodict:
        c=frequencies_nodict()
        for k,v in c.most_common(int(args.frequencies_nodict)):
            print v,"\t",k
            # willen we de woorden nog opslaan? zo ja, iets toevoegen zoals hieronder. of met set() als we de duplicaten eruit willen halen
            '''
            with open(outputbestand,"w", encoding="utf-8") as f:
            for woord in belangrijk:
            f.write(woord+"\n")
            '''

    if args.network:
        coocnet(int(args.network[0]),int(args.network[1]))



if __name__ == "__main__":
    main()
