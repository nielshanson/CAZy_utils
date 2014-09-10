#!python
"""
do_something_script.py

Created by Niels Hanson on 2013-04-21.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
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
    
except:
     import_exception = """ Could not load some modules """
     print import_exception 
     sys.exit(3)



# a script to parce GH5 families
what_i_do = "a script to parce CAZy HTML files"
parser = argparse.ArgumentParser(description=what_i_do)
# add arguments to the parser
parser.add_argument('-i', dest='input_files', type=str, nargs='+',
                required=True, help='a selection of input files (required)', default=None)
parser.add_argument('-f', dest='family', type=str, nargs=1,
                required=True, help='A CAZy family is required i.e. GH, AA, etc.', default=None)
parser.add_argument('-n', dest='family_num', type=int, nargs=1,
                required=True, help='A CAZy family number is required (integer)', default=None)               
                
parser.add_argument('-o', dest='output_files', type=str, nargs='?',
               required=True, help='the output file (required)', default=None)
               

# helper function to get directories from a given path
def get_directories(path):
   ret = []
   for f in os.listdir(path):
       if not os.path.isfile(os.path.join(path,f)):
           ret.append(f.strip())
   return ret

def check_arguments(arguments):
   for file in arguments["input_files"]:
       try:
           open(file)
           close(file)
       except IOError:
           print "Could not open " + file
           sys.exit(1)
           
def parse_cazy_rows(file_handle):
    soup = BeautifulSoup(file_handle, "html5lib")
    file_handle.close()
    tr = soup.find_all("tr", valign="top")
    collection = {}
    fields = [ "protein", "ec", "organism","genbank","uniprot","pdb","subf"]
    for rows in tr:
        children = rows.findChildren("td")
        i = 0
        protein = {}
        result = ""
        for c in children:
            node = c
            if i == 0:
                node = c
            elif i == 1:
                if c.a:
                    node = c.a
            elif i == 2:
                if c.a:
                    node = c.a
            elif i == 3:
                if c.a:
                    node = c.a
                if node.b:
                    node = node.b
            elif i == 4:
                if c.a:
                    node = c.a
            elif i == 5:
                if c.a:
                    node = c.a
            elif i == 6:
                node = c
            else:
                node = c
            
            if node.string:
                result = node.string.replace(u'\xa0',u'').strip()
                result = result.replace(u'\u03b1', u'alpha')
                result = result.replace(u'\u03b2', u'beta')
                result = result.replace(u'\u03b3', u'gamma')
                result = result.replace(u'\u03b4', u'delta')
                result = result.replace(u'\u03b5', u'epsilon')
                result = re.sub(u'(\\xa0|[^A-Za-z0-9 \[\]\._\(\)];)+',u'', result)
                result = result.strip()
                if result == u'':
                    result = None
            protein[fields[i]] = result
            i += 1
        if protein:
            collection[str(protein["protein"]) + "," + str(protein["genbank"])] = protein
            
    return collection

def add_family(sequence, fasta_header_pattern, family, family_num, annotation):
    result = sequence.split('\n')
    result = filter(None, result)
    for i in range(len(result)):
        if fasta_header_pattern.match(result[i]):
            if annotation["subf"] != None:
                result[i] = result[i] + " (" + str(family) + ":" + str(family_num) + "_" + str(annotation["subf"]) + ")"
            else:
                result[i] = result[i] + " (" + str(family) + ":" + str(family_num) + ")"
            
    result = result + [""]
    return "\n".join(result)


def main():
    args = vars(parser.parse_args())
    family = str(args["family"][0])
    family_num = int(args["family_num"][0])
    ncbi_url = "http://www.ncbi.nlm.nih.gov/sviewer/viewer.cgi?val=ABCDEFGHI&db=protein&dopt=fasta&extrafeat=0&fmt_mask=0&maxplex=1&sendto=t&log$=seqview&pid=0"
    fasta_header_pattern = re.compile("^>")
    output_handle = open(args["output_files"], "w")
    
    for f in args["input_files"]:
        try:
            f_handle = open(f, "r")
        except:
            print "count not open file " + f
        results = parse_cazy_rows(f_handle)
        
        j = 0
        for i in results:
            time.sleep(0.05)
            if results[i]["genbank"]:
                myurl = ncbi_url.replace("ABCDEFGHI", results[i]["genbank"])
            else:
                continue
            try:
                response = urllib2.urlopen(myurl)
                sequence = response.read()
                if fasta_header_pattern.match(sequence):
                    print "Sequence found!"
                    new_seq = add_family(sequence, fasta_header_pattern, family, family_num, results[i])
                    output_handle.write(new_seq)
                    j = j+1
                    print j
                else:
                    print "Unsure of sequence"

            except:
                "Print failed to connect to GenBank"
                continue
            
        
    output_handle.close()    
    

# call the main function
if __name__ == "__main__":
    sys.exit(main())


