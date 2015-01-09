#!/usr/bin/env python
from __future__ import unicode_literals
from io import open
import argparse

parser=argparse.ArgumentParser('This tool is part of INFRA (c) ... \n It removes words from a newline-terminated list"\n\nExample: ./removesearchterms llcorp1.txt "hema bijenkorf vend" \n')
parser.add_argument("filein",help="Inputfile")
parser.add_argument("fileout",help="Outputfile")
parser.add_argument("words",help='a space-seperated list of words to remove from FILE. The list has to be enclosed by " "')

args= parser.parse_args()

with open(args.filein,encoding="utf-8") as fi:
    lines=fi.readlines()

output=[line for line in lines if line.strip() not in args.words]

with open(args.fileout,encoding="utf-8", mode="w") as fo:
    fo.writelines(output)

print "\nOutput written to",args.fileout,"\n"
