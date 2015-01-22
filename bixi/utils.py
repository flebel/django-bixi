import errno
import urllib2

from math import radians, cos, sin, asin, sqrt
from socket import error as SocketError


def distance(lat1, long1, lat2, long2):
    """
    Calculate the great circle distance in meters between two points on
    Earth (specified in decimal degrees.)
    Taken on May 1st 2013 from http://stackoverflow.com/a/4913653
    """
    # Convert decimal degrees to radians
    rlong1, rlat1, rlong2, rlat2 = map(radians, [long1, lat1, long2, lat2])
    # Haversine formula
    dlon = rlong2 - rlong1
    dlat = rlat2 - rlat1
    a = sin(dlat / 2) ** 2 + cos(rlat1) * cos(rlat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return 6367 * c * 1000

def forgiving_urlopen(url, attempts=5):
    data = None
    for attempt in range(attempts):
        try:
            data = urllib2.urlopen(url)
            break
        except urllib2.HTTPError:
            continue
        except SocketError as e:
            # Only ignore ECONNRESET
            if e.errno != errno.ECONNRESET:
                raise
            continue
    return data

