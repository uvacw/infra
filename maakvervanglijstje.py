#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from io import open
import json
import ConfigParser
# TODO

'''
DEELS HIER, DEELS IN vervang.py
VERVANGPROGRAMMA
- koppeltekens
- é ä etc --> e a ae (meerdere spellingsvarianten toestaan) (functie voor alles!)
- uitzonderingen als E.ON (EON, eon,...)?? --> uitzonderingenlijstje

spaties
McDonald's
H & M --> H&M
Heineken Holding(s) --> ??
Reckitt Benckiser Group
& Co --> strippen!
Banco Santander --> Santander
Hyundai Heavy Industries
'''


config = ConfigParser.RawConfigParser()
config.read('config.conf')

nlwoordenbestand=config.get('files','dictionary')

ownreplacements=[config.get('files','ownreplacements')] 


outputbestand=config.get('files','replacementlist')
outputbestand2=config.get('files','replacementlistlastnames')
outputbestand3=config.get('files','replacementlistotherindicator')



def replacespaces(listwithwords):
	repldict={}
	wordswithspace=[woord for woord in listwithwords if woord.find(" ")>-1]
	print len(wordswithspace),"expressions containing spaces (from the dictionary) have been added to the replacement list"
	for woord in wordswithspace:
		repldict[woord]=woord.replace(" ","_")
	return repldict
	
	

def replaceown(inputfiles,col1,col2):
	'''
	col1 = column with the original expression
	col2 = column with the replacement
	'''
	repldict={}
	for fname in inputfiles:
		i=0
		with open(fname,mode="r",encoding="utf-8") as fi:
			for line in fi:
				i+=1
				bothcolumns=line.strip().split("\t")
				#print bothcolumns
				# alleen doorgaan als de kolom bestaat
				if len(bothcolumns)-1>=max(col1,col2):
					repldict[bothcolumns[col1]]=bothcolumns[col2]
		print i,"expressions from",fname,"have been added to the replacement list"
	return repldict
	
	
def replaceownindien(inputfiles,col1,col2,col3):
	'''
	col1 = column with the original expression
	col2 = column with the replacement
	col3= indien DIT genoemd wordt in het artikel
	'''
	repldict={}
	for fname in inputfiles:
		i=0
		with open(fname,mode="r",encoding="utf-8") as fi:
			for line in fi:
				i+=1
				bothcolumns=line.strip().split("\t")
				#print bothcolumns
				# alleen doorgaan als de kolom bestaat
				if len(bothcolumns)-1>=max(col1,col2):
					repldict[bothcolumns[col3]]=[bothcolumns[col1],bothcolumns[col2]]
		print i,"expressions from",fname,"have been added to the replacement list"
	return repldict



def main():
	complrepldict={}
	
	# STAP 1: VASTE UITDRUKKINGEN ('s ochtends --> 's_ochtends)
	alldutchwords=[line.strip() for line in open(nlwoordenbestand,mode="r",encoding="utf-8")]
	complrepldict.update(replacespaces(alldutchwords))

	# STAP 2: EIGEN VERVANGLIJSTJE (namen, bedrijven, ...), zelf aangemaakt tab-seperated file
	complrepldict.update(replaceown(ownreplacements,0,1))
	


	with open(outputbestand,mode="w",encoding="utf-8") as fo:
		fo.write(unicode(json.dumps(complrepldict,ensure_ascii=False)))
	
	print "Finished writing",outputbestand
	print "YOU'RE READY WITH THE GENERAL REPLACEMENT LIST!\n"
	
        
        # STAP 2b: WE DOEN HET NOG EEN KEER, WANT WE WILLEN NOG EEN VERVANGLIJSTJE DAT WE ALLEEN GAAN TOEPASSEN ALS NAMEN AL EEN KEER ZIJN GENOEMD; 
        
        complrepldict2={}
        complrepldict2.update(replaceown(ownreplacements,2,1))
	
	with open(outputbestand2,mode="w",encoding="utf-8") as fo:
		fo.write(unicode(json.dumps(complrepldict2,ensure_ascii=False)))
	
	print "Finished writing",outputbestand2
	print "YOU'RE READY WITH THE REPLACEMENT LIST FOR LAST NAMES/FULL NAMES!\n"



        # STAP 2c: WE DOEN HET NOG EEN KEER, VOOR VERVANINGEN INDIEN ANDER WOORD ERGENS IN HET ARTIKEL WORT GENOEMD
                
        complrepldict3={}
        complrepldict3.update(replaceownindien(ownreplacements,2,1,3))
	
	with open(outputbestand3,mode="w",encoding="utf-8") as fo:
		fo.write(unicode(json.dumps(complrepldict3,ensure_ascii=False)))
	
	print "Finished writing",outputbestand3
	print "YOU'RE READY WITH THE REPLACEMENT LIST FOR OTHER INDICATORS!\n"






	
if __name__ == "__main__":
	main()
	
