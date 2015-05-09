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
from datetime import date
from time import sleep
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

  #user = "3kwJhIcAAAAJ" #szell
  #user = "PL8nGh4AAAAJ" # sinatra
  user = "vsj2slIAAAAJ" # barabasi
  #user = "jXTPa_AAAAAJ" # latora
  excludelargeteams = True


  rooturl = "http://scholar.google.com"
  # GET USERNAME
  cstart = 0
  url = rooturl + "/citations?hl=en&user=" + user + "&view_op=list_works&pagesize=100&view_op=list_works&sortby=pubdate&cstart=" + str(cstart)
  response = urllib2.urlopen(url, timeout=3)
  htmldoc = response.read()
  soup = BeautifulSoup(htmldoc, "lxml")
  namediv = soup.find("div", { "id" : "gsc_prf_in" }).getText()
  username, userfullname = getname(namediv)
  careerstart = date.today().year
  careerend = 0

  # GET PUBLICATIONS
  with open("../data/paperweb_" + username + ".json", "w") as jsonfile:

    print "Retrieving PaperWeb of user " + userfullname + " (" + user + ")"
    publications = []
    coauthors = set()
    links1 = dict() # links between user and coauthor
    links0 = dict() # links between coauthors

    while True:
      sleep(10)
      if cstart != 0:
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
      paperyears = paperyears[1:-1]
      paperlinks = soup.findAll("a", { "class" : "gsc_a_at" })
      paperlinks = [a['href'] for a in paperlinks if a.has_attr('href')]

      for t,y,pl in zip(divcontents, paperyears, paperlinks):
        if y != '': # drop papers that do not have a publication year
          careerstart = min([careerstart, int(y)])
          careerend = max([careerend, int(y)])
          # get authors
          coauthors_thispaper = set()
          authors = t.split(',')
          # check for "...". If so, we can go a level deeper to retrieve all coauthors
          if not(excludelargeteams) and " ..." in authors:
            sleep(1)
            urlpaper = rooturl + pl
            responsepaper = urllib2.urlopen(urlpaper, timeout=3)
            htmldocpaper = responsepaper.read()
            souppaper = BeautifulSoup(htmldocpaper, "lxml")
            t = souppaper.find("div", { "class" : "gsc_value" })
            t = t.text
            authors = t.split(',')
          for a in authors:
            newauthor, fullname = getname(a)
            if newauthor and newauthor != username:
              coauthors.add(newauthor)
              coauthors_thispaper.add(newauthor)
              # add to links1
              if newauthor in links1:
                links1[newauthor]["value"] += 1
                links1[newauthor]["yearfirst"] = min([links1[newauthor]["yearfirst"], y])
                links1[newauthor]["yearlast"] = max([links1[newauthor]["yearlast"], y])
              else:
                links1[newauthor] = {"value": 1, "yearfirst": y, "yearlast": y, "fullname": fullname}

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

      #if cstart == 200:
      #  break
      if htmldoc.find('id="gsc_bpf_next" aria-label="Next" class') != -1: # otherwise it is disabled
        cstart += 100  # Next page
      else:
        break
      #sys.exit("Planned Stop.")

    #print links0
    #print links1
    finaljson = dict()
    finaljson["nodes"] = [{"name":username, "group":1, "fullname": userfullname, "yearfirst":careerstart, "yearlast":careerend}]
    for link1 in links1:
      try:
        finaljson["nodes"].append({"name":link1, "group":2, "fullname": links1[link1]["fullname"], "yearfirst":int(links1[link1]["yearfirst"]), "yearlast":int(links1[link1]["yearlast"])})
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


def getname(a):
  aparts = a.strip()
  aparts = aparts.split(' ')
  if len(aparts) >= 2:
    fullname = unidecode(strip_accents(aparts[0][0])) + ". " + unidecode(strip_accents(aparts[-1])).title()
    lastname = unidecode(strip_accents(aparts[-1].lower())) + "_" + unidecode(strip_accents(aparts[0][0]).lower()) # casefold would be better for gross
    return lastname, fullname;
  else:
    return False, False

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

