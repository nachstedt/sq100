from sq100.data_types import CoordinateBounds, Point


def calc_tracks_bounds(tracks):
    track_bounds = [t.bounds() for t in tracks]
    min_latitude = min([b.min.latitude for b in track_bounds])
    min_longitude = min([b.min.longitude for b in track_bounds])
    max_latitude = max([b.max.latitude for b in track_bounds])
    max_longitude = max([b.max.longitude for b in track_bounds])
    return CoordinateBounds(
        minimum=Point(latitude=min_latitude, longitude=min_longitude),
        maximum=Point(latitude=max_latitude, longitude=max_longitude))


def parse_range(astr):
    result = set()
    for part in astr.split(','):
        x = part.split('-')
        result.update(range(int(x[0]), int(x[-1]) + 1))
    return sorted(result)
