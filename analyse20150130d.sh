#!/bin/bash

./analysis.py --ll --subset="{'\$text':{'\$search':'twitter facebook kpn rabobank google sns ing airfranceklm apple royaldutchshell philips albertheijn abnamro ziggo youtube postnl heineken imtech microsoft bmw unilever samsung ahoy sky mercedesbenz jupiler tntexpress hema belkin aegon achmea ansaldobreda ford sony américamóvil ikea bam audi disney ferrari sanoma volkswagen nokia ahold tomtom asml dsm vodafone henm amazon mcdonalds redbull renault nuon akzonobel sbmoffshore vacansoleil tvm kpmg eplus oad grolsch essent ryanair cocacola linkedin honda boskalis spotify argos tata deutschebank bp peugeot jpmorganchase upc toyota siemens amstel generalmotors yahoo corendon starbucks luxor deltalloyd alitalia bolcom barclays citroën skype efteling whatsapp arcadis frieslandcampina tmg dell opel aldi goldmansachs lidl'},'suspicious':False,'cluster':1}" --subset2="{'suspicious':False}"

./removesearchterms.py output/llcorp1.txt output/llcorp1_top100.txt 'twitter facebook kpn rabobank google sns ing airfranceklm apple royaldutchshell philips albertheijn abnamro ziggo youtube postnl heineken imtech microsoft bmw unilever samsung ahoy sky mercedesbenz jupiler tntexpress hema belkin aegon achmea ansaldobreda ford sony américamóvil ikea bam audi disney ferrari sanoma volkswagen nokia ahold tomtom asml dsm vodafone henm amazon mcdonalds redbull renault nuon akzonobel sbmoffshore vacansoleil tvm kpmg eplus oad grolsch essent ryanair cocacola linkedin honda boskalis spotify argos tata deutschebank bp peugeot jpmorganchase upc toyota siemens amstel generalmotors yahoo corendon starbucks luxor deltalloyd alitalia bolcom barclays citroën skype efteling whatsapp arcadis frieslandcampina tmg dell opel aldi goldmansachs lidl'

head -150 output/llcorp1_top100.txt > output/llcorp1_top100_150.txt

./analysis.py --pca_ownwords output/llcorp1_top100_150.txt 5 --varimax --subset="{'\$text':{'\$search':'twitter facebook kpn rabobank google sns ing airfranceklm apple royaldutchshell philips albertheijn abnamro ziggo youtube postnl heineken imtech microsoft bmw unilever samsung ahoy sky mercedesbenz jupiler tntexpress hema belkin aegon achmea ansaldobreda ford sony américamóvil ikea bam audi disney ferrari sanoma volkswagen nokia ahold tomtom asml dsm vodafone henm amazon mcdonalds redbull renault nuon akzonobel sbmoffshore vacansoleil tvm kpmg eplus oad grolsch essent ryanair cocacola linkedin honda boskalis spotify argos tata deutschebank bp peugeot jpmorganchase upc toyota siemens amstel generalmotors yahoo corendon starbucks luxor deltalloyd alitalia bolcom barclays citroën skype efteling whatsapp arcadis frieslandcampina tmg dell opel aldi goldmansachs lidl'},'suspicious':False, 'cluster':1}"

# ./analysis.py --kmeans_ownwords output/llcorp1_top100_150.txt 5 --varimax --subset="{'\$text':{'\$search':'twitter facebook kpn rabobank google sns ing airfranceklm apple royaldutchshell philips albertheijn abnamro ziggo youtube postnl heineken imtech microsoft bmw unilever samsung ahoy sky mercedesbenz jupiler tntexpress hema belkin aegon achmea ansaldobreda ford sony américamóvil ikea bam audi disney ferrari sanoma volkswagen nokia ahold tomtom asml dsm vodafone henm amazon mcdonalds redbull renault nuon akzonobel sbmoffshore vacansoleil tvm kpmg eplus oad grolsch essent ryanair cocacola linkedin honda boskalis spotify argos tata deutschebank bp peugeot jpmorganchase upc toyota siemens amstel generalmotors yahoo corendon starbucks luxor deltalloyd alitalia bolcom barclays citroën skype efteling whatsapp arcadis frieslandcampina tmg dell opel aldi goldmansachs lidl'},'suspicious':False}"


cp output/llcorp1_top100_150.txt ~/Dropbox/uva/onderzoeksprojecten_lopend/2014-damianjeroen/1.\ Bestanden\ Jeroen/20150130

cp output/compscores.csv ~/Dropbox/uva/onderzoeksprojecten_lopend/2014-damianjeroen/1.\ Bestanden\ Jeroen/20150130

cp output/cosinedistance.csv ~/Dropbox/uva/onderzoeksprojecten_lopend/2014-damianjeroen/1.\ Bestanden\ Jeroen/20150130

cp output/clusters.csv ~/Dropbox/uva/onderzoeksprojecten_lopend/2014-damianjeroen/1.\ Bestanden\ Jeroen/20150130


