#!python
"""
load_cazy_db.py

Created by Niels Hanson on 2014-09-04.
Copyright (c) 2013. All rights reserved.
"""

# load some packages
from __future__ import division
try:
    import re
    import sys
    import os
    import types
    import argparse
    from bs4 import *
    import html5lib
    import urllib2
    import time
    import sqlite3
    from python_libs.fastareader import *
    
except:
     import_exception = """ Could not load some modules """
     print import_exception 
     sys.exit(3)

what_i_do = "a script to parce CAZy HTML files and load into a sqlite database"
parser = argparse.ArgumentParser(description=what_i_do)
# add arguments to the parser      
parser.add_argument('--db', dest='sqlite_db', type=str, nargs='?',
                required=True, help='the sqlite database', default=None)
parser.add_argument('-t', dest='table_name', type=str, nargs='?',
                required=True, help='the table name', default=None)
parser.add_argument('-o', dest='output', type=str, nargs='?',
                required=True, help='the table name', default=None)

def add_cazy_family(sequences, gi_to_cazyfamily, ids):
    lines = sequences.split("\n")
    new_lines = []
    count = 0
    for l in lines:
        hits = re.search(">", l)
        if hits:
            new_lines.append(l + " [[" + ids[count] + "]]" +" (" + gi_to_cazyfamily[ids[count]] + ")")
            count += 1
        else:
            new_lines.append(l)
    
    return "\n".join(new_lines)
    

def main():
    args = vars(parser.parse_args())
    
    # connect to the database
    conn = sqlite3.connect(args["sqlite_db"])
    c = conn.cursor()
    
    table_name = args['table_name'].strip()
    
    # get unique genbank ids
    sql = "SELECT DISTINCT(genbank), fam, num, subf FROM " + table_name + " WHERE NOT (genbank LIKE '% %' OR genbank LIKE '%None%')"
    c.execute(sql)
    gi_list = [] # list of genbank ids
    found = []
    not_found = [] # list of genbank ids not found
    gi_to_cazyfamily = {}
    for gi in c.fetchall():
        gi_list.append(gi[0].strip())
        if gi[0].strip() not in gi_to_cazyfamily:
            if gi[3].strip() == "None":
                gi_to_cazyfamily[gi[0].strip()] = gi[1].strip() + gi[2].strip()
            else:
                gi_to_cazyfamily[gi[0].strip()] = gi[1].strip() + gi[2].strip() + "_" + gi[3].strip()
    
    query = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=protein&id=XXXXXXXXXXX&rettype=fasta&retmode=text"
    n=500
    out = open(args["output"], 'w')
    for i in range(0,len(gi_list),n):
        time.sleep(2)
        ids = ",".join(gi_list[i:i+n])
        myurl = query.replace("XXXXXXXXXXX", ids)
        print myurl
        try:
            response = urllib2.urlopen(myurl)
            sequences = response.read()
            sequences = add_cazy_family(sequences, gi_to_cazyfamily, gi_list[i:i+n])
        except:
            print "Could not connect to NCBI"
        
        out.write(sequences)
    
    out.close()
    exit()
    # reader = FastaReader(args['refseq'].strip())
    #     
    #     count = 0
    #     for record in reader:
    #         fields = record.name.split("|")
    #         if fields[3] in gi_list:
    #             found.append(fields[3])
    #         else:
    #             not_found.append(fields[3])
    #         count += 1
    #         if count % 100 == 0:
    #             print count
    #             print "Found:", len(found)
    #             print "Not Found:", len(not_found)
    #     print count
    #     print "Found:", len(found)
    #     print "Not Found:", len(not_found)
    
    
    
                
# call the main function
if __name__ == "__main__":
    sys.exit(main())
