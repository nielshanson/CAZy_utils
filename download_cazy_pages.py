#!/usr/bin/python

import urllib2
import time
import difflib
## http://www.cazy.org/GH1_all.html
## http://www.cazy.org/GH1_all.html?debut_PRINC=1000#pagination_PRINC

CAZY_base = "http://www.cazy.org/"
# Families = {"GH":133, "GT":96, "PL":23, "CE":16, "AA":12}
Families = {"CBM":71}

def write_html(html_text, file_name):
    try:
        output_handle = open(file_name,"w")
    except:
        "couldn't open file " + file_name
    
    output_handle.write(html_text)
    output_handle.close()
    return
    
    
    
# find all gh families
for fam in Families.keys():
    for i in range(1,Families[fam]+1):
        link = CAZY_base + fam + str(i) + "_all.html"
        html_old = ""
        for j in range(0,50001,1000):
            download_link = link + "?debut_PRINC=" + str(j) + "#pagination_PRINC"
            html = None
            try :
                response = urllib2.urlopen(download_link)
                html = response.read()
                
            except ValueError:
                print "couldn't download file "  + download_link
            if html:
                seq=difflib.SequenceMatcher(a=html, b=html_old)
                ratio = seq.real_quick_ratio()
                cazy_file = "CAZy" + "_" + fam + str(i) + "_" + "page" + str(j) + ".html"
                if ratio != 1.0:
                    write_html(html, cazy_file)
                else:
                    break
                html_old = html
            time.sleep(1)
        
    
