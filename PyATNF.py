"""
A small code that Queries ATNF pulsar catolog
use regular expression to grab the numbers and parse them into python dictions.

Weiwei Zhu
2011-Feb-03
zhuwwpku@gmail.com
"""
import urllib2
import urllib, sys, re, commands
from tools.html2plaintext import *



def _retrieve(line, keylist, pattern):
    def KeyListGen(keylist):
        for key in keylist:
            yield key
    KG = KeyListGen(keylist)
    results = {}
    #print line
    for match in pattern.finditer(line):
        value = str(match.group('value'))
        #print 'value: ', value
        if value == '*' or value == 'NONE': value = None
        uncertainty = str(match.group('uncertainty')).replace('(','').replace(')','')
        if uncertainty == '*' or uncertainty == 'NONE' or uncertainty == 'None':uncertainty = None
        #print 'uncertainty: ', uncertainty
        try: 
            #match.group('ref'):
            ref = str(match.group('ref'))
            if ref == '*' or ref == 'NONE' or ref == 'None':ref = None
            #print 'ref: ', ref
            results[KG.next()] = (value, uncertainty, ref)
        except:
            try:
                results[KG.next()] = (value, uncertainty)
            except StopIteration:
                print results, value, uncertainty
                print line
    try:
        missing = KG.next()
        badlist1 = set(['J0451-67','J0418+5732','J1748-2446ad','J2007+2722','J1635-4735'])
        badlist2 = set(['J1808-2024','J1846-0258'])
        name = results['Name'][0]
        if name in badlist1:
            keys = list(set(keylist).difference(set(['Age','Bsurf','Edot','P1'])))
            print 'Searching for %s of %s' % (keys,name)
            return Qatnf(name, keys)
        elif name in badlist2:
            age = {'J1808-2024':218, 'J1846-0258':728}
            keys = list(set(keylist).difference(set(['Age'])))
            return Qatnf(name, keys).update({'Age':age[name]})
        else:
            print  '''Pulsar %s's  %s not found from line :
            %s
            the last found number is (%s, %s, %s)''' % (name, missing, line, value, uncertainty, ref) 
            print 'searching for %s' % keylist
            print 'The collected keys are: %s\n\n' % (results)
    except StopIteration:pass
    except KeyError:return None
    return results



def LQatnf(psr, Query=('RaJ', 'DecJ'), condition=None):
    if psr == 'all':psr=''
    keylist = list(Query)
    Nkey = len(keylist)
    if condition:
        text = commands.getoutput('''psrcat -c "%(keylist)s" %(pulsar)s -l "%(condition)s"''' % {'pulsar':psr, 'keylist':' '.join(keylist), 'condition':condition})
    else:
        text = commands.getoutput('''psrcat -c "%(keylist)s" %(pulsar)s ''' % {'pulsar':psr, 'keylist':' '.join(keylist)})
    text = '\n'.join(text.split('\n')[4:-1]) + '\n'
    #print text
    #p = re.compile(r"""(?P<Number>\d+)
            #(?P<line>(\s+
            #(?P<value>-*\+*(\d{2,2}\:)*(\d+\.*\d*(e-*\+*\d+)*)|\*|([JB]\d{4}[-\+]\d{2,4})|(AXP|HE|NRAD|XDINS|RRAT)(\,(AXP|HE|NRAD|XDINS|RRAT)){0,1})
            #(\s+(?P<uncertainty>\d{1,2}))*
            #(?P<ref>(\s+|\[*)[a-z]+\+*\d+\]*)*
            #\s*){1,%d})\n""" % (Nkey), re.VERBOSE)
    #pattern = re.compile(r"""\s+
            #(?P<value>(-*\+*(\d{2,2}\:)*\d+\.*\d*(e-*\+*\d+)*)|\*|([JB]\d{4}[-\+]\d{2,4})|(AXP|HE|NRAD|XDINS|RRAT)(\,(AXP|HE|NRAD|XDINS|RRAT)){0,1})
            #(\s+(?P<uncertainty>\d{1,2})\s+){0,1}
            #(\s*\[*(?P<ref>[a-z]+\+{0,1}\d+)\]*)*
            #""", re.VERBOSE)
    p = re.compile(r"""(?P<Number>\d+)\s
            (?P<line>(.*))\n""" , re.VERBOSE)
    pattern = re.compile(r"""
            \s(?P<value>((-*\+*(\d{2,2}\:){1,2}){0,1}\d+(\.\d*){0,1}([eE]-*\+*\d+){0,1})|NONE|\*|([JB]\d{4}[-\+]\d{2,5}([A-Z]|-\d|[a-z]{1,2}){0,1})|(AXP|HE|NRAD|XDINS|XINS|RRAT)(\,(AXP|HE|NRAD|XDINS|XINS|RRAT)){0,1})
            (\s+(?P<uncertainty>\d+)\s+){0,1}
            ((\s*|\[)(?P<ref>(([a-z]+\+{0,1}\d{2}[a-z]{0,1})(\,\s+([a-z]+\+{0,1}\d{2}[a-z]{0,1}))*)|(?<=0\s)\*)\]*)*
            """, re.VERBOSE)
    #finally:
    if psr == '':
        results = []
        for m in p.finditer(text):
            try:
                if not m.group('Number') == '0':
                    line = str(m.group('line'))
                    info = _retrieve(line, keylist, pattern)
                    if not info == None:
                        results.append(info)
            except StopIteration:
                print 'line %s: \n%s' % (m.group('Number'),line)
        return results
    else:
        m = p.search(text)
        line = str(m.group('line'))
        #print 'line: \n',line
        results = _retrieve(line, keylist, pattern)
        return results

def Qatnf(psr, Query=('RaJ', 'DecJ'), condition=None):
    if psr == 'all':psr=''
    name = psr.split()
    if len(name) == 2:
        if name[0] == 'PSR':
            psr = name[1]
    #try:
    #for i in [1]:
        #Try query the webserver
    url = 'http://www.atnf.csiro.au/research/pulsar/psrcat/proc_form.php'
    data = {}
    if isinstance(Query, (basestring)):
        Query = [Query]
    for Q in Query:
        data[Q]=Q
    url_values = urllib.urlencode(data)
    #data = {'ephemeris':'short', 'startUserDefined':'true','style':'Publication quality','sort_attr':'jname','sort_order':'asc'}
    #data = {'ephemeris':'short', 'startUserDefined':'true','style':'Long with last digit error','sort_attr':'jname','sort_order':'asc'}
    data = {'ephemeris':'short', 'startUserDefined':'true','style':'Short without erros','sort_attr':'jname','sort_order':'asc'}
    url_values += '&'+urllib.urlencode(data)
    if condition:
        data = {'pulsar_names':psr, 'condition':condition}
    else:
        data = {'pulsar_names':psr}
    url_values += '&'+urllib.urlencode(data)
    data = {'x_axis':'','x_scale':'linear','y_axis':'','y_scale':'linear', 
        'no_value':'None','coords_unit':'raj/decj','radius':'','coords_1':'',
        'coords_2':'','fsize':'3' }
    url_values += '&'+urllib.urlencode(data)
    data = {'state':'query'}
    url_values += '&'+urllib.urlencode(data)
    data = {'table_bottom.x':'100', 'table_bottom.y':'100'}
    url_values += '&'+urllib.urlencode(data)
    full_url = url + '?' + url_values
    order = []
    for key in Query:
        idx = url_values.find(key)
        order.append((idx, key))
    order.sort()
    keylist = [x[1] for x in order]
    the_page = urllib2.urlopen(full_url).read()
    #print the_page
    text = html2plaintext(the_page, encoding='UTF-8')
    '''filer the text for artifacts [??]'''
    artifacts = re.compile('(\[\d+\])', re.VERBOSE)
    text = artifacts.sub('', text)
    text = text.encode('ascii', 'ignore')
    #print text
    #print '\n'.join([x for x in text.split('\n') if not x == '' and not x.startswith(' http')][20:22])
    #print '\n'.join(the_page.split('\n')[93:95])
    #print '\n'.join([x for x in text.split('\n') if not x == '' and not x.startswith(' http')][22:-22])
    text = '\n'.join([x for x in text.split('\n') if not x == '' and not x.startswith(' http')][22:-22])+'\n'
    Nkey = len(keylist)
    #print Nkey
    #p = re.compile(r"""^(?P<Number>\d+)
            #(?P<line>(\s+
            #(?P<value>([-\+]{0,1}\d{2}\:\d{2}\:\d{2}\.\d+)|(\d+\.\d*(e-*\+*\d+)*)|NONE|\*|([JB]\d{4}[-\+]\d{2,4})|((AXP|HE|NRAD|XDINS|RRAT)(\,(AXP|HE|NRAD|XDINS|RRAT)){0,1}))
            #(\s+(?P<uncertainty>\d{1,2})\s+){0,1}
            #(?P<ref>\s*\[*[a-z]+\+{0,1}\d{2}\]*){0,1}
            #){%d,%d})\s+\n""" % (Nkey,Nkey), re.VERBOSE)
    p = re.compile(r"""(?P<Number>\d+)\s+
            (?P<line>(.*))\n""" , re.VERBOSE)
    pattern = re.compile(r"""
            (?<=\s)(?P<value>((-*\+*(\d{2}\:){1,2}){0,1}\d+(\.\d*){0,1}([eE]-*\+*\d+){0,1})|NONE|\*|([JB]\d{4}[-\+]\d{2,5}([A-Z]|-\d|[a-z]{1,2}){0,1})|(AXP|HE|NRAD|XDINS|XINS|RRAT)(\,(AXP|HE|NRAD|XDINS|XINS|RRAT)){0,1})
            ((\s+)(?P<uncertainty>\d+)(?=\s)){0,1}
            ((\s*|\[)(?P<ref>(([a-z]{2,4}\+{0,1}\d{2})(\,\s+([a-z]+\+{0,1}\d{2}))*)|(?<=\s)\*)\]*){0,1}(\s%){0,1}
            """, re.VERBOSE)
            #(?<=[\s|\[])((?P<ref>(((\w{2,4}\+{0,1})(?=\d{2}))|\*))\]*){0,1}\s%{0,1}
            #((\s+|\[)(?P<ref>(([a-z]{2,4}\+{0,1}(?=\d{2}))(\,\s+([a-z]+\+{0,1}\d{2}))*)|\*)\]*){0,1}\s%{0,1}
            #((\s*|\[)(?P<ref>(([a-z]+\+{0,1}\d{2})(\,\s+([a-z]+\+{0,1}\d{2}))*)|(?<=\s)\*)\]*)(\s%){0,1}

    #finally:
    #print keylist
    #print text
    if not psr == '':
        m = p.search(text)
        line = ' '+m.group('line')
        #print m.group('Number'),' :', line
        results = _retrieve(line, keylist, pattern)
        return results
    else:
        results = []
        i = 0
        for m in p.finditer(text):
            try:
                line = m.group('line')
                info = _retrieve(line, keylist, pattern)
                if not info == None:
                    results.append(info)
                    i+=1
            except:
                #print i
                print 'line %s: \n%s' % (m.group('Number'),line)

        return results

    #except :
        #print 'web server query failed, try local database.\n'
        #return LQatnf(psr, Query)


from Coordinate import RA, Dec, ecs

def QatnfPos(psr, in_unit_degree=False):
    info = Qatnf(psr)
    if in_unit_degree:
        ra = RA(info['RaJ']).in_unit_degree
        dec = Dec(info['DecJ']).in_unit_degree
        return ra, dec
    else:
        ra = RA(info['RaJ'])
        dec = Dec(info['DecJ'])
        return ecs(ra, dec)


def isAXP(psr):
    if not psr['Type'][0]==None and not psr['Type'][0].find('AXP') == -1:
        return True
    else:
        return False

def isINS(psr):
    if not psr['Type'][0]==None and (not psr['Type'][0].find('XDINS') == -1 or not psr['Type'][0].find('XINS') == -1):
        return True
    else:
        return False
