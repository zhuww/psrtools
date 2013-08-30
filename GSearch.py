#!/usr/bin/python
import sys
import urllib
import simplejson

query = urllib.urlencode({'q' : sys.argv[1]})
url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s' \
  % (query)
search_results = urllib.urlopen(url)
json = simplejson.loads(search_results.read())
results = json['responseData']['results']
for i in results:
    print i['title'].encode('utf8') + ": " + i['url']

