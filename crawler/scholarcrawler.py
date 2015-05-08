#! /usr/bin/env python
## -*- coding: utf-8 -*-

# usage: scholarcrawler.py
# This script crawls google scholar, retrieving all coauthors and some co-publication data for one user in json format
# Contact: Michael Szell, m.szell@neu.edu


import os
import sys
import glob
import urllib2
import string
import re
import time
import datetime
from collections import defaultdict
from random import randint
from bs4 import BeautifulSoup, Comment, NavigableString
from HTMLParser import HTMLParser
import unicodedata
from unidecode import unidecode
from itertools import combinations
import json


## ##################################################
## ##################################################
## ##################################################



def main():
# usage: scholarcrawlercrawler.py
#
# optional arguments: -

  rooturl = "http://scholar.google.com"

  #user = "3kwJhIcAAAAJ"
  #user = "PL8nGh4AAAAJ"
  user = "vsj2slIAAAAJ"
  #username = "szell"
  #username = "sinatra"
  username = "barabasi"

  # GET PUBLICATIONS
  with open("../data/paperweb_" + username + ".json", "a") as jsonfile:

    print "Retrieving paperweb of user " + username + " (" + user + ")"
    publications = []
    coauthors = set()
    links1 = dict() # links between user and coauthor
    links0 = dict() # links between coauthors

    cstart = 0
    while True:
      url = rooturl + "/citations?hl=en&user=" + user + "&view_op=list_works&pagesize=100&view_op=list_works&sortby=pubdate&cstart=" + str(cstart)
      response = urllib2.urlopen(url, timeout=3)
      htmldoc = response.read()
      soup = BeautifulSoup(htmldoc, "lxml")

      anchors = soup.findAll('a')
      links = [a['href'] for a in anchors if a.has_attr('href')]

      graydivs = soup.findAll("div", { "class" : "gs_gray" })
      divcontents = [row.text for row in graydivs]
      divcontents = divcontents[0:-1:2]
      yearspans = soup.findAll("span", { "class" : "gsc_a_h" })
      paperyears = [row.text for row in yearspans]
      paperyears =paperyears[1:-1]
      for t,y in zip(divcontents, paperyears):
        # get authors
        coauthors_thispaper = set()
        authors = t.split(',')
        for a in authors:
          aparts = a.strip()
          aparts = aparts.split(' ')
          if len(aparts) == 2:
            newauthor = unidecode(strip_accents(aparts[1].lower())) # casefold would be better for gross
            if newauthor != username:
              coauthors.add(newauthor)
              coauthors_thispaper.add(newauthor)
              # add to links1
              if newauthor in links1:
                links1[newauthor]["value"] += 1
                links1[newauthor]["yearfirst"] = min([links1[newauthor]["yearfirst"], y])
                links1[newauthor]["yearlast"] = max([links1[newauthor]["yearlast"], y])
              else:
                links1[newauthor] = {"value": 1, "yearfirst": y, "yearlast": y}

        # we need to connect all coauthors to each other
        if len(coauthors_thispaper) >= 2:
          temp = combinations(coauthors_thispaper, 2)
          authorpairs = []
          for p in temp:
            authorpairs.append(p)
          for p in authorpairs:
            pset = frozenset(p)
            if pset in links0:
              links0[pset]["value"] += 1
              links0[pset]["yearfirst"] = min([links0[pset]["yearfirst"], y])
              links0[pset]["yearlast"] = max([links0[pset]["yearlast"], y])
            else:
              links0[pset] = {"value": 1, "yearfirst": y, "yearlast": y}

      if cstart == 200:
        break
      if htmldoc.find('id="gsc_bpf_next" aria-label="Next" class') != -1: # otherwise it is disabled
        cstart += 100  # Next page
      else:
        break
      #sys.exit("Planned Stop.")

    #print links0
    #print links1
    finaljson = dict()
    finaljson["nodes"] = [{"name":username, "group":1, "fullname": username, "yearfirst":2010, "yearlast":2015}]
    for link1 in links1:
      try:
        finaljson["nodes"].append({"name":link1, "group":2, "fullname": link1, "yearfirst":int(links1[link1]["yearfirst"]), "yearlast":int(links1[link1]["yearlast"])})
      except:
        pass
    finaljson["links"] = []
    for link1 in links1:
      try:
        finaljson["links"].append({"source":username, "target":link1, "value":int(links1[link1]["value"]), "yearfirst":int(links1[link1]["yearfirst"]), "yearlast":int(links1[link1]["yearlast"]), "typ":1})
      except:
        pass
    for link0 in links0:
      try:
        link0list = list(link0)
        finaljson["links"].append({"source":link0list[0], "target":link0list[1], "value":int(links0[link0]["value"]), "yearfirst":int(links0[link0]["yearfirst"]), "yearlast":int(links0[link0]["yearlast"]), "typ":0})
      except:
        pass

    json.dump(finaljson, jsonfile)
  sys.exit("Planned Stop.")


def strip_accents(s):
  return ''.join(c for c in unicodedata.normalize('NFD', s)
    if unicodedata.category(c) != 'Mn')


## ##################################################
## ##################################################
## ##################################################

if __name__ == "__main__":
    main()

## ##################################################
## ##################################################
## ##################################################

