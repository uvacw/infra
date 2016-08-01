#!/bin/bash

./analysis.py --ll --subset="{'\$text':{'\$search':'kpn rabobank google sns ing airfranceklm apple royaldutchshell philips albertheijn'},'suspicious':False}" --subset2="{'suspicious':False}"

./removesearchterms.py output/llcorp1.txt output/llcorp1_top10.txt 'kpn rabobank google sns ing airfranceklm apple royaldutchshell philips albertheijn'

head -75 output/llcorp1_top10.txt > output/llcorp1_top10_75.txt

./analysis.py --pca_ownwords output/llcorp1_top10_75.txt 5 --varimax --subset="{'\$text':{'\$search':'kpn rabobank google sns ing airfranceklm apple royaldutchshell philips albertheijn'},'suspicious':False}"

./analysis.py --kmeans_ownwords output/llcorp1_top10_75.txt 5 --varimax --subset="{'\$text':{'\$search':'kpn rabobank google sns ing airfranceklm apple royaldutchshell philips albertheijn'},'suspicious':False}"


cp output/llcorp1_top10_75.txt ~/Dropbox/uva/onderzoeksprojecten_lopend/2014-damianjeroen/1.\ Bestanden\ Jeroen/20150130

cp output/compscores.csv ~/Dropbox/uva/onderzoeksprojecten_lopend/2014-damianjeroen/1.\ Bestanden\ Jeroen/20150130

cp output/cosinedistance.csv ~/Dropbox/uva/onderzoeksprojecten_lopend/2014-damianjeroen/1.\ Bestanden\ Jeroen/20150130

cp output/clusters.csv ~/Dropbox/uva/onderzoeksprojecten_lopend/2014-damianjeroen/1.\ Bestanden\ Jeroen/20150130


