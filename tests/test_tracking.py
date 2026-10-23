import pytest
from src.tracking.kalman_filter import KalmanFilter
from src.tracking.track import Track
from src.tracking.tracker import MultiObjectTracker

def detection(x,y,w=50,h=80):
    return {'bbox':(x-w/2,y-h/2,x+w/2,y+h/2),'confidence':0.9,'class_id':0}

def test_kalman_movement():
    kf=KalmanFilter(); kf.predict(); kf.update((40,25))
    x,y=kf.get_position(); assert 0<x<40 and 0<y<25

def test_track_confirmation_bbox_and_lifecycle():
    tracker=MultiObjectTracker(80,2)
    for i in range(3):
        tracker.update([detection(50,50,40,90)])
        assert len(tracker.get_tracks()) == (1 if i==2 else 0)
    t=tracker.get_tracks()[0]
    x1,y1,x2,y2=t.get_bbox()
    assert (t.id,x2-x1,y2-y1)==(1,40,90)
    tracker.update([]);assert tracker.tracks[0].missed==1
    tracker.update([]);assert tracker.tracks[0].missed==2
    tracker.update([]);assert tracker.tracks==[]

def test_two_objects_have_distinct_ids():
    tracker=MultiObjectTracker(max_match_distance=25)
    for _ in range(3): tracker.update([detection(20,20),detection(200,20)])
    assert {t.id for t in tracker.get_tracks()}=={1,2}

def test_invalid_tracker_parameters():
    with pytest.raises(ValueError): MultiObjectTracker(max_match_distance=-1)
    with pytest.raises(ValueError): MultiObjectTracker(max_missed_frames=-1)
    with pytest.raises(ValueError): Track(1,(0,0),n_init=0)
