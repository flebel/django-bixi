from collections import namedtuple

from django.test import TestCase

from .utils import distance


class UtilsTest(TestCase):
    LatLonCoordinates = namedtuple('LatLonCoordinated', ['lat', 'lon'])

    def test_distance_close(self):
        fishermans_wharf = self.LatLonCoordinates(37.80833, -122.41555)
        gg_bridge = self.LatLonCoordinates(37.80815, -122.47644)
        d = distance(fishermans_wharf.lat, fishermans_wharf.lon, gg_bridge.lat, gg_bridge.lon)
        expected = 5.3508 * 1000
        # Test accuracy within a 5 m radius
        self.assertTrue(d > expected - 5)
        self.assertTrue(d < expected + 5)

    def test_distance_distant(self):
        cn_tower = self.LatLonCoordinates(43.64256, -79.38705)
        space_needle = self.LatLonCoordinates(47.62046, -122.34911)
        d = distance(cn_tower.lat, cn_tower.lon, space_needle.lat, space_needle.lon)
        expected = 3330 * 1000 # Rounded estimation
        # Test accuracy within a 10 km radius
        self.assertTrue(d > expected - 10*1000)
        self.assertTrue(d < expected + 10*1000)

