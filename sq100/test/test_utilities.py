from mock import create_autospec

from sq100.data_types import CoordinateBounds, Point, Track
import sq100.utilities as utils


def test_calc_tracks_bounds():
    tracks = [create_autospec(Track) for _ in range(3)]
    track_bounds = [
        CoordinateBounds(minimum=Point(-20, 5), maximum=Point(0, 11)),
        CoordinateBounds(minimum=Point(8, -3), maximum=Point(10, 2)),
        CoordinateBounds(minimum=Point(5, 7), maximum=Point(12, 9))]
    for i in range(3):
        tracks[i].bounds.return_value = track_bounds[i]
    bounds = utils.calc_tracks_bounds(tracks)
    expected = CoordinateBounds(minimum=Point(-20, -3), maximum=Point(12, 11))
    print(bounds)
    print(expected)
    assert bounds == expected
