import urllib2
import urllib, sys

def simbad(psr):
    """Search simbad database for a pulsar's information, especially the coordinates."""
    data = {}
    data['output.format'] = 'ASCII'
    data['Ident'] = psr
    url_values = urllib.urlencode(data)
    url = 'http://simbad.u-strasbg.fr/simbad/sim-id'
    full_url = url + '?' + url_values
    data = urllib2.urlopen(full_url)
    results = data.read()
    info = {}
    failed = False
    for lines in results.split('\n')[7:]:
        try:
            key,value = lines.split(':')
        except ValueError:
            try:
                value+=lines
            except UnboundLocalError:
                key='Search Result'
                value = lines
                failed = True
        except:
            pass
        info.update({key:value})
    for key in info.keys():
        value = info[key]
        value.replace('\n','')
        if not value.find('~ ~') == -1:value=None
        info[key] = value
    if failed:
        for key in info.keys():
            print '%s:\n%s\n' % (key, info[key])
        raise 'Failed to identify the object %s' % psr
    else:
        return info


from Coordinate import coordinate, ecs
def SimbadCoord(psr):
    info = simbad(psr)
    pos = info['Coordinates(FK5,ep=2000,eq=2000)']
    coord = coordinate(pos)
    return ecs(coord.RA, coord.Dec)
    #rastr, decstr = pos.split()
