# -*- coding: utf-8 -*
"""Use the Cordes-Lazio NE2001 Galactic Free Electron Density Model to estimate the distance of a pulsar. 
If it can't find the distance of the pulsr from NE2001 model, try query ATNF catalog."""
import urllib
import urllib2
import re
from tools.html2plaintext import *
from PyATNF import Qatnf

url = 'http://rsd-www.nrl.navy.mil/7213/lazio/ne_model/#psr'
response = urllib2.urlopen(url)
html = response.read()
start = False
PSRDict = {}
for line in html.split('\n'):
    if line == '<OPTION VALUE="-1" SELECTED>':
        start = True
        continue
    if start == True:
        if line == '</select>':
            start = False
            continue
        key, psr = line.split('>')
        misc, opt = key.split('=')
        opt = opt.replace('"','')
        PSRDict.update({psr: opt})


#text = html2plaintext(html, encoding='UTF-8')
#print text.encode('UTF-8')

def psrDist(psr):
    name = psr.split()
    if len(name) == 2:
        if name[0] == 'PSR':
            psr = name[1]
        else:
            raise 'Can only deal with radio pulsar.'
    if PSRDict.has_key(psr):
        url = 'http://rsd-www.nrl.navy.mil/cgi-bin/pulsar.cgi' 
        values = {'pulsar': PSRDict[psr], "frequency": 1.}
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        the_page = response.read()
        text = html2plaintext(the_page, encoding='UTF-8')
        #print text
        p = re.compile('D = (.+) kpc\\n\((.+),(.+)\)', re.U)
        m = p.search(text)
        dist = [float(D) for D in m.groups(0)]
        return (dist[0], dist[1]-dist[0], dist[2]-dist[0])
    else:
        #raise "%s's information is not available" % psr
        dist = Qatnf(psr, ['Dist'])['Dist']
        return (float(dist[0]), dist[1])

