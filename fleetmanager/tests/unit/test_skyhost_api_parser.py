import pandas as pd

from fleetmanager.extractors.skyhost.parsers import Trackers, DrivingBook
from fleetmanager.tests.fixtures.skyhost_response import tracker_response, mileage_response


def test_tracker_parser():
    trackers = Trackers()
    trackers.parse(tracker_response)
    tracker_ids = ["15789", "15794", "15812", "15873"]
    assert type(trackers.frame) == pd.DataFrame
    assert all(map(lambda tracker: tracker in trackers.frame.ID.values, tracker_ids))
    assert "Description" in trackers.frame.columns


def test_driving_book_parser():
    driving_book = DrivingBook()
    driving_book.parse(mileage_response)
    assert type(driving_book.frame) == pd.DataFrame
    assert len(driving_book.frame) == 6
    assert all(map(lambda key: key in driving_book.frame.columns, ["StopPos_sLat", "StartPos_sLon", "ID"]))
