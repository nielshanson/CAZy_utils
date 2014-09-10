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
    
except:
     import_exception = """ Could not load some modules """
     print import_exception 
     sys.exit(3)

what_i_do = "a script to parce CAZy HTML files and load into a sqlite database"
parser = argparse.ArgumentParser(description=what_i_do)
# add arguments to the parser
parser.add_argument('-i', dest='input_files', type=str, nargs='+',
                required=True, help='a selection of input CAZy HTML files (required)', default=None)          
parser.add_argument('--db', dest='sqlite_db', type=str, nargs='?',
                required=True, help='the target database', default=None)

def parse_cazy_row(row, fields):
    """
    Given a beaultiful soup node at the row of a cazy protein, the function will extract all
    all the propreate fields
    """
    children = row.findChildren("td")
    i = 0
    protein = {}
    result = ""
    for c in children:
        # each child td is a part of the field
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
            # found data field, parse and qc
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
        return protein
    


def parse_cazy_and_insert(file_handle, family, family_num, db_cursor):
    """
    Opens CAZy HTML file, its family and family number and the nosql db cursor, and loads
    values into a pre-specified table in the nosql database having the appropreate fields.
    """
    soup = BeautifulSoup(file_handle, "html5lib")
    file_handle.close()
    tr = soup.find_all("tr")
    collection = {}
    super_group = "Unknown" # Bacteria, Archaea, etc.
    fields = [ "protein", "ec", "organism", "genbank", "uniprot", "pdb", "subf"]
    db_insert_set = []
    
    for rows in tr:
        # for each tr
        if 'class' in rows.attrs:
            # this is a supergroup row
            if rows.td.span.a == None:
                # update super_group with Bacteria
                super_group = rows.td.span.get_text().strip()
        elif 'valign' in rows.attrs:
            # this is a data row
            if rows['valign'] == "top":
                # parse the rows of the CAZy Table
                protein = parse_cazy_row(rows, fields)
                protein['super_group'] = super_group
                protein['family'] = family
                protein['family_num'] = family_num
                if 'subf' not in protein:
                    # no subfamily
                    protein['subf'] = None 
                try:
                    # check for strange characters
                    protein['protein'] = str(protein['protein'])
                except:
                    # put in dummy statement if fail
                    protein['protein'] = "None"
                try:
                    protein['organism'] = str(protein['organism'])
                except:
                    protein['organism'] = "None"
                
                # construct database fields
                db_values = (str(protein['family']), \
                             str(protein['family_num']), \
                             str(protein["super_group"]), \
                             str(protein['organism']), \
                             str(protein['protein']), \
                             str(protein['ec']), \
                             str(protein['genbank']), \
                             str(protein['uniprot']), \
                             str(protein['pdb']), \
                             str(protein['subf']) \
                             )
                # add to insert set
                db_insert_set.append(db_values)
    
    # load db_insert_set into Table
    sql = "INSERT INTO 'CAZY_2014_09_04' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    db_cursor.executemany(sql, db_insert_set)


def main():
    
    args = vars(parser.parse_args())
    
    # for each file
    for f in args["input_files"]:
        # connect to database
        conn = sqlite3.connect(args["sqlite_db"])
        c = conn.cursor()
        
        # extract the base name from the filename/filepath
        basename = os.path.basename(f) 
        print "Loading:", basename
        
        # extract the Family and the family number from the filename
        results = re.search("_([A-z]+?)([0-9]+?)_", basename)
        family = results.group(1)
        family_num = results.group(2)
        
        # open the file an parse lines using parse_cazy_and_insert
        try:
            f_handle = open(f, "r")
        except:
            print "could not open file " + f
        results = parse_cazy_and_insert(f_handle, family, family_num, c)
        
        # commit changes to the database
        conn.commit()
    
    

# call the main function
if __name__ == "__main__":
    sys.exit(main())


