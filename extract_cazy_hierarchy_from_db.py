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
parser.add_argument('--db', dest='sqlite_db', type=str, nargs='?',
                required=True, help='the sqlite database', default=None)
parser.add_argument('-t', dest='table_name', type=str, nargs='?',
                required=True, help='the table name', default=None)
parser.add_argument('-o', dest='output', type=str, nargs='?',
                required=True, help='output file name', default=None)


def print_protein_lines(output, none_pattern, values, subfam=False):
    """
    print family lines based on the case
    """
    
    if subfam == False:
        for v in values:
            line = "\t\t\t\t"
            if (none_pattern.match(v[1]) != None or v[1] == ""):
                continue
            line += (str(v[1]).strip() + "\t")
            if (none_pattern.match(v[0]) == None and v[0] != ""):
                line += ( " " + str(v[0]).strip() )
            if (none_pattern.match(v[3]) == None and v[3] != ""):
                line += ( " (" + str(v[3]).strip() + ")" )
            if (none_pattern.match(v[2]) == None and v[2] != ""):
                line += ( " [" + str(v[2]).strip() + "]" )
            # write out line
            output.write( line + "\n" )
    else:
        for v in values:
            line = "\t\t\t\t"
            if (none_pattern.match(v[1]) != None or v[1] == ""):
                continue
            line += (str(v[1]).strip() + "\t")
            if (none_pattern.match(v[0]) == None and v[0] != ""):
                line += ( " " + str(v[0]).strip() )
            if (none_pattern.match(v[3]) == None and v[3] != ""):
                line += ( " (" + str(v[3]).strip() + ")" )
            if (none_pattern.match(v[2]) == None and v[2] != ""):
                line += ( " [" + str(v[2]).strip() + "]" )
            # write out line
            output.write( line + "\n" )

def main():
    args = vars(parser.parse_args())
    
    # connect to the database
    conn = sqlite3.connect(args["sqlite_db"])
    c = conn.cursor()
    
    family_order = ["GH", "GT", "PL", "CE", "AA", "CBM"]
    translate_family = {"GH" : "Glycoside Hydrolases",
                        "GT" : "GlycosylTransferases",
                        "PL" : "Polysaccharide Lyases",
                        "CE" : "Carbohydrate Esterases",
                        "AA" : "Auxiliary Activities",
                        "CBM" : "Carbohydrate-Binding Modules"}
    none_pattern = re.compile("None")
    
    output = open(args["output"], "w")
    
    # get unique families
    sql = "SELECT DISTINCT(fam) FROM CAZY_2014_09_04"
    c.execute(sql)
    fam = c.fetchall()
    for f in family_order:
        output.write( translate_family[f] + "\n")
        sql = "SELECT DISTINCT(num) FROM CAZY_2014_09_04 WHERE fam='" + str(f) + "'"
        c.execute(sql)
        fam_num = c.fetchall()
        temp_fam_num = []
        for num in fam_num:
            temp_fam_num.append(int(num[0]))
        temp_fam_num.sort()
        fam_num = temp_fam_num
        for num in fam_num:
            output.write( "\t" + (f + str(num)) + "\n" )
            # check for subfamilies 
            sql = "SELECT DISTINCT(subf) FROM CAZY_2014_09_04 WHERE fam='" + str(f) + "'" + " AND " + "num='" + str(num) + "'"
            c.execute(sql)
            subfs = c.fetchall()
            
            if len(subfs) <= 1:
                output.write( "\t\t" + (f + str(num)) + "\n" )
                # family had no subfamilies
                sql = "SELECT DISTINCT(super) FROM CAZY_2014_09_04 WHERE fam='" + str(f) + "'" + " AND " + "num='" + str(num) + "'"
                c.execute(sql)
                super_class = c.fetchall()
                for super_c in super_class:
                    output.write( "\t\t\t" + str(super_c[0]) + "\n" )
                    sql = "SELECT protein, genbank, org, ec, uniprot, subf FROM CAZY_2014_09_04 WHERE fam='" +\
                                                                        str(f) + "' AND " +\
                                                                        "num='" + str(num) + "' AND " +\
                                                                        "super='" + str(super_c[0]) + "' AND " +\
                                                                        "NOT (genbank LIKE '% %' OR genbank LIKE '%None%')"
                    c.execute(sql)
                    values = c.fetchall()
                    print_protein_lines(output, none_pattern, values, subfam=False)
                        # line = "\t\t\t"
                        # if (none_pattern.match(v[1]) != None or v[1] == ""):
                        #     continue
                        # line += (str(v[1]).strip() + "\t")
                        # if (none_pattern.match(v[0]) == None and v[0] != ""):
                        #     line += ( " " + str(v[0]).strip() )
                        # if (none_pattern.match(v[3]) == None and v[3] != ""):
                        #     line += ( " (" + str(v[3]).strip() + ")" )
                        # if (none_pattern.match(v[2]) == None and v[2] != ""):
                        #     line += ( " [" + str(v[2]).strip() + "]" )
                        # # write out line
                        # output.write( line + "\n" )
            else:
                # iterate through subfamilies
                
                # fix order of subfamilies
                subfs_temp = []
                for subf in subfs:
                    if subf[0] != "None":
                        try:
                            int(subf[0])
                        except:
                            continue
                        subfs_temp.append(int(subf[0]))
                    else:
                        subfs_temp.append(str(subf[0]))
                
                subfs_temp.sort()
                subfs = subfs_temp
                
                # print subfs
                
                for subf in subfs:
                    if subf != "None":
                        output.write("\t" + "\t" + ( str(f) + str(num) + "_" + str(subf) ) + "\n")
                        
                    else:
                        output.write("\t" + "\t" + str(subf) + "\n")
                    
                    sql = "SELECT DISTINCT(super) FROM CAZY_2014_09_04 WHERE fam='" + str(f) + "'" + " AND " + "num='" + str(num) + "' AND subf='" + str(subf) + "'" 
                    c.execute(sql)
                    super_class = c.fetchall()
                    for super_c in super_class:
                        output.write( "\t" + "\t" + "\t" + str(super_c[0]) + "\n" )
                        sql = "SELECT protein, genbank, org, ec, uniprot, subf FROM CAZY_2014_09_04 WHERE fam='" +\
                                                                            str(f) + "' AND " +\
                                                                            "num='" + str(num) + "' AND " +\
                                                                            "super='" + str(super_c[0]) + "' AND " +\
                                                                            "subf='" + str(subf) + "'"
                        c.execute(sql)
                        values = c.fetchall()
                        print_protein_lines(output, none_pattern, values, subfam=True)
                            # line = "\t\t\t\t"
                            # if (none_pattern.match(v[1]) != None or v[1] == ""):
                            #     continue
                            # line += (str(v[1]).strip() + "\t")
                            # if (none_pattern.match(v[0]) == None and v[0] != ""):
                            #     line += ( " " + str(v[0]).strip() )
                            # if (none_pattern.match(v[3]) == None and v[3] != ""):
                            #     line += ( " (" + str(v[3]).strip() + ")" )
                            # if (none_pattern.match(v[2]) == None and v[2] != ""):
                            #     line += ( " [" + str(v[2]).strip() + "]" )
                            # # write out line
                            # output.write( line + "\n" )
    output.close()
    
# call the main function
if __name__ == "__main__":
    sys.exit(main())
