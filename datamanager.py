#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
from io import open
import json
from pymongo import MongoClient, Connection
import re, sys, unicodedata
from os import listdir, walk
from os.path import isfile, join, splitext
import ConfigParser
import argparse
from collections import defaultdict, OrderedDict

# read config file and set up MongoDB
config = ConfigParser.RawConfigParser()
config.read('config.conf')
replacementlistfile = config.get('files', 'replacementlist')
stopwordsfile = config.get('files', 'stopwords')
replacementlistlastnamesfile = config.get('files', 'replacementlistlastnames')
replacementlistsindienfile = config.get('files', 'replacementlistotherindicator')
databasename = config.get('mongodb', 'databasename')
collectionname = config.get('mongodb', 'collectionname')
collectionnamecleaned = config.get('mongodb', 'collectionnamecleaned')
client = MongoClient(config.get('mongodb', 'url'))
db = client[databasename]
collection = db[collectionname]
collectioncleaned = db[collectionnamecleaned]



# hier wordt de functie voor het vervangen van leestekens gedefinieerd. Ze worden ERUIT gehaald, niet vervangen door spaties, en dat is juist wat we willen: willem-alexander --> willemalexander
tbl = dict.fromkeys(i for i in xrange(sys.maxunicode) if unicodedata.category(unichr(i)).startswith('P'))


def remove_punctuation(text):
    return text.replace("`","").replace("´","").translate(tbl)


def insert_lexisnexis(pathwithlnfiles, recursive):
    """
    Usage: insert_lexisnexis(pathwithlnfiles,recursive)
    pathwithlnfiles = path to a directory where lexis nexis output is stored
    recursive: TRUE = search recursively all subdirectories, but include only files ending on .txt
               FALSE = take ALL files from directory supplied, but do not include subdirectories
    """
    tekst = {}
    byline = {}
    section = {}
    length = {}
    loaddate = {}
    language = {}
    pubtype = {}
    journal = {}
    pubdate_day = {}
    pubdate_month = {}
    pubdate_year = {}
    pubdate_dayofweek = {}

    if recursive:
        alleinputbestanden = []
        for path, subFolders, files in walk(pathwithlnfiles):
            for f in files:
                if isfile(join(path, f)) and splitext(f)[1].lower() == ".txt":
                    alleinputbestanden.append(join(path, f))
    else:
        # print  listdir(pathwithlnfiles)
        alleinputbestanden = [join(pathwithlnfiles, f) for f in listdir(pathwithlnfiles) if
                              isfile(join(pathwithlnfiles, f)) and splitext(f)[1].lower() == ".txt"]
        print alleinputbestanden
    artikel = 0
    for bestand in alleinputbestanden:
        print "Now processing", bestand
        with open(bestand, "r", encoding="utf-8") as f:
            i = 0
            for line in f:
                i = i + 1
                # print "Regel",i,": ", line
                line = line.replace("\r", " ")
                if line == "\n":
                    continue
                matchObj = re.match(r"\s+(\d+) of (\d+) DOCUMENTS", line)
                matchObj2 = re.match(r"\s+(\d{1,2}) (januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december) (\d{4}) (maandag|dinsdag|woensdag|donderdag|vrijdag|zaterdag|zondag)", line)
                if matchObj:
                    artikel += 1
                    tekst[artikel] = ""
                    continue
                if line.startswith("BYLINE"):
                    byline[artikel] = line.replace("BYLINE: ", "").rstrip("\n")
                elif line.startswith("SECTION"):
                    section[artikel] = line.replace("SECTION: ", "").rstrip("\n")
                elif line.startswith("LENGTH"):
                    length[artikel] = line.replace("LENGTH: ", "").rstrip("\n").rstrip(" woorden")
                elif line.startswith("LOAD-DATE"):
                    loaddate[artikel] = line.replace("LOAD-DATE: ", "").rstrip("\n")
                elif matchObj2:
                    pubdate_day[artikel]=matchObj2.group(1)
                    pubdate_month[artikel]=matchObj2.group(2)
                    pubdate_year[artikel]=matchObj2.group(3)
                    pubdate_dayofweek[artikel]=matchObj2.group(4)
                elif line.startswith("LANGUAGE"):
                    language[artikel] = line.replace("LANGUAGE: ", "").rstrip("\n")
                elif line.startswith("PUBLICATION-TYPE"):
                    pubtype[artikel] = line.replace("PUBLICATION-TYPE: ", "").rstrip("\n")
                elif line.startswith("JOURNAL-CODE"):
                    journal[artikel] = line.replace("JOURNAL-CODE: ", "").rstrip("\n")
                elif line.lstrip().startswith("Copyright ") or line.lstrip().startswith("All Rights Reserved"):
                    pass
                elif line.lstrip().startswith("AD/Algemeen Dagblad") or line.lstrip().startswith(
                        "De Telegraaf") or line.lstrip().startswith("Trouw") or line.lstrip().startswith(
                        "de Volkskrant") or line.lstrip().startswith("NRC Handelsblad") or line.lstrip().startswith(
                        "Metro") or line.lstrip().startswith("Spits"):
                    pass
                else:
                    tekst[artikel] = tekst[artikel] + " " + line.rstrip("\n")
    print "Done!", artikel, "articles added."

    if not len(journal) == len(loaddate) == len(section) == len(language) == len(byline) == len(length) == len(tekst) == len(pubdate_year) == len(pubdate_dayofweek) ==len(pubdate_day) ==len(pubdate_month):
        print "!!!!!!!!!!!!!!!!!!!!!!!!!"
        print "Ooooops! Not all articles seem to have data for each field. These are the numbers of fields that where correctly coded (and, of course, they should be equal to the number of articles, which they aren't in all cases."
        print "journal", len(journal)
        print "loaddate", len(loaddate)
        print "pubdate_day",len(pubdate_day)
        print "pubdate_month",len(pubdate_month)
        print "pubdate_year",len(pubdate_year)
        print "pubdate_dayofweek",len(pubdate_dayofweek)
        print "section", len(section)
        print "language", len(language)
        print "byline", len(byline)
        print "length", len(length)
        print "tekst", len(tekst)
        print "!!!!!!!!!!!!!!!!!!!!!!!!!"
        print
        print "Anyhow, we're gonna proceed and set those invalid fields to 'NA'. However, you should be aware of this when analyzing your data!"


    else:
        print "No missing values encountered."

    suspicious=0
    for i in range(artikel):
        try:
            art_source = journal[i + 1]
        except:
            art_source = "NA"
        try:
            art_loaddate = loaddate[i + 1]
        except:
            art_loaddate = "NA"
        try:
            art_pubdate_day = pubdate_day[i + 1]
        except:
            art_pubdate_day = "NA"
        try:
            art_pubdate_month = pubdate_month[i + 1]
        except:
            art_pubdate_month = "NA"
        try:
            art_pubdate_year = pubdate_year[i + 1]
        except:
            art_pubdate_year = "NA"
        try:
            art_pubdate_dayofweek = pubdate_dayofweek[i + 1]
        except:
            art_pubdate_dayofweek = "NA"
        try:
            art_section = section[i + 1]
        except:
            art_section = "NA"
        try:
            art_language = language[i + 1]
        except:
            art_language = "NA"
        try:
            art_length = length[i + 1]
        except:
            art_length = "NA"
        try:
            art_text = tekst[i + 1]
        except:
            art_text = "NA"
        try:
            art_byline = byline[i + 1]
        except:
            art_byline = "NA"

        # here, we are going to add an extra field for texts that probably are no "real" articles
        # first criterion: stock exchange notacions and similiar lists:
        ii=0
        jj=0
        for token in art_text.replace(",","").replace(".","").split():
            ii+=1
            if token.isdigit():
                jj+=1
        # if more than 25% of the tokens are numbers, then suspicious = True.
        art_suspicious = jj > .16 * ii
        if art_suspicious: suspicious+=1

        art = {"source": art_source.lower(), "loaddate": art_loaddate, "pubdate_day":art_pubdate_day, "pubdate_month":art_pubdate_month, "pubdate_year":art_pubdate_year, "pubdate_dayofweek":art_pubdate_dayofweek, "section": art_section.lower(),
               "language": art_language.lower(), "length": art_length, "text": art_text, "byline": art_byline,
               "from-database": "lexisnexis", "suspicious":art_suspicious}
        article_id = collection.insert(art)
    print '\nInserted',len(tekst),"articles, out of which",suspicious,"might not be real articles, but, e.g., lists of stock shares. "

def adhocclean(bestand):
    repldict = {}
    with open(bestand, "r", encoding="utf-8") as fi:
        for line in fi:
            comline = line.strip().split("\t")
            repldict[comline[0]] = comline[1]
    print "It contains the following rules:"
    print repldict
    replpatterns = set(re.compile("\\b" + k + "\\b") for k in repldict)
    allarticles = collectioncleaned.find()
    aantal = collectioncleaned.count()
    i = 0
    numbsub = defaultdict(int)
    for art in allarticles:
        i += 1
        print "\r", i, "/", aantal, " or ", int(i / aantal * 100), "%",
        sys.stdout.flush()
        thisart = art["text"]
        doesthisartneedupdate = 0
        for pat in replpatterns:
            subst = pat.subn(repldict[pat.pattern[2:-2]], thisart)  # [2:-2] to strip the \b
            thisart = subst[0]
            numbsub[pat.pattern[2:-2]] += subst[1]
            doesthisartneedupdate += subst[1]
        if doesthisartneedupdate > 0:
            print "Updating article", art["_id"]
            # print collectioncleaned.find({"_id":art["_id"]})[0]
            collectioncleaned.update({"_id": art["_id"]}, {"$set": {"text": thisart}})
    print
    for k in numbsub:
        print k, "replaced", numbsub[k], "times"
    print "Done"


def clean_database():
    # initialize new database for cleaned collection
    c = Connection()
    c[databasename].drop_collection(collectionnamecleaned)

    # load replacement lists
    # replacement list 1: always replace
    with open(replacementlistfile, mode="r", encoding="utf-8") as fi:
        repldict = json.load(fi, object_pairs_hook=OrderedDict)
    replpatterns = set(re.compile("\\b" + k + "\\b") for k in repldict)
    # replacement list 2: replace if already replaced according to list 1
    with open(replacementlistlastnamesfile, mode="r", encoding="utf-8") as fi:
        repldictpersons = json.load(fi, object_pairs_hook=OrderedDict)
    # replacement list 3: replace only if another expression is mentioned
    with open(replacementlistsindienfile, mode="r", encoding="utf-8") as fi:
        repldictindien = json.load(fi, object_pairs_hook=OrderedDict)


    allarticles = collection.find()
    aantal = collection.count()
    i = 0
    for art in allarticles:
        i += 1
        print "\r", i, "/", aantal, " or ", int(i / aantal * 100), "%",
        sys.stdout.flush()
        thisart = art["text"].replace("\n", " ")
        numbsub = 0
        for pat in replpatterns:
            subst = pat.subn(repldict[pat.pattern[2:-2]], thisart)  #[2:-2] to strip the \b
            thisart = subst[0]
            numbsub += subst[1]
        # only if sth has been substituted at all, check if it's a last name that has to be substituted as well
        # functie 1b: als iemand een keer met z'n volledige naam genoemd wordt, ook de volgende keren dat alleen z'n achternaam wordt genoemd deze vervangen
        if numbsub > 0:
            for k, v in repldictpersons.iteritems():
                #print "For",k,", there are",len(v),"rules."
                for vv in v:
                    if vv in thisart:
                        thisart = re.sub("\\b" + k + "\\b", vv, thisart)
                        #print "Replaced",k,"by",vv
        for k, v in repldictindien.iteritems():
            if re.findall("\\b" + k + "\\b",thisart):
                for vv in v:
                    print "checking vv",vv,"and k",k
                    thisart = re.sub("\\b" + vv[0] + "\\b", vv[1], thisart)
                print "Replaced", vv[0], "by", vv[1], "because", k, "was mentioned"


        thisart = remove_punctuation(thisart.lower())
        stops = [line.strip().lower() for line in open(stopwordsfile, mode="r", encoding="utf-8")]
        tas = thisart.split()
        thisart = ""
        for woord in tas:
            if (woord not in stops) and (not woord.isdigit()):
                thisart = " ".join([thisart, woord])
        # replace original text with  modified text and put the whole item in the cleaned collection
        art["text"] = thisart
        article_id = collectioncleaned.insert(art)


def main():
    parser = argparse.ArgumentParser(
        description="This program is part of VETTE NAAM BEDENKEN PLUS VERWIJZING NAAR ONS PAPER. UITLEG GEVEN HOE HET WERKT.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--overview", help="Give an overview of the data stored in the collection", action="store_true")
    group.add_argument("--overview_cleaned", help="Give an overview of the data stored in the cleaned collection",
                       action="store_true")
    group.add_argument("--insert_ln",
                       help="Inserts LexisNexis articles. Name the folder with the input data after --insert_ln", )
    group.add_argument("--clean",
                       help="Creates a cleaned version of your collection by removing punctuation and replacing words as specified in the configuration files.",
                       action="store_true")
    group.add_argument("--adhocclean",
                       help="Creates a cleaned version of your collection by removing punctuation and replacing words as specified in the configuration files.",
                       nargs=1, metavar="FILE")

    group.add_argument("--delete_all", help="Deletes everything in your database (!!!)", action="store_true")
    parser.add_argument("--recursive", help="Indicates that all subfolders are processed as well", action="store_true")
    # parser.add_argument("folder", help = "The folder in which data to be inserted is stored", nargs="?")

    args = parser.parse_args()

    if args.delete_all:
        print "Do you REALLY want to ERASE the whole collection", collectionname, "within the database", databasename, "?"
        cont = raw_input('Type "Hell, yeah!" and hit Return if you want to continue: ')
        if cont == "Hell, yeah!":
            c = Connection()
            c[databasename].drop_collection(collectionname)
            print "Done. RIP", collectionname
        else:
            print "OK, you changed your mind. Fine."

    if args.overview:
        # alles=collection.find()
        # for artikel in alles:
        #        print artikel["date"],artikel["source"]
        overview1 = collection.aggregate([{"$group": {"_id": "$source", "number": {"$sum": 1}}}])
        #print overview1["result"]
        for combi in overview1["result"]:
            print combi["_id"], "\t", combi["number"]

    if args.overview_cleaned:
        overview1 = collectioncleaned.aggregate([{"$group": {"_id": "$source", "number": {"$sum": 1}}}])
        for combi in overview1["result"]:
            print combi["_id"], "\t", combi["number"]

    if args.insert_ln:
        print "Starting to insert", args.insert_ln
        print "Including subfolders?", args.recursive
        print "This can take some time..."
        insert_lexisnexis(args.insert_ln, args.recursive)

    if args.clean:
        print "Do you REALLY want to clean the whole collection", collectionname, "within the database", databasename, "right now? This can take VERY long, and you might consider doing this overnight."
        cont = raw_input('Type "I have time!" and hit Return if you want to continue: ')
        if cont == "I have time!":
            clean_database()
        else:
            print "OK, maybe next time."

    if args.adhocclean:
        bestand = args.adhocclean[0]
        print "Re-processing the cleaned database with the instructions provided in", bestand, "\n"
        adhocclean(bestand)


if __name__ == "__main__":
    main()
