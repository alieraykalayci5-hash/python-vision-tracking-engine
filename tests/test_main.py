import sys
import types
import cv2
import pytest
import main
from tools.make_synthetic_demo import make_video

def test_missing_input_and_camera_index(tmp_path):
    with pytest.raises(FileNotFoundError,match='Input video not found'):
        main.validate_input_video(str(tmp_path/'missing.mp4'))
    assert main.validate_input_video('0')==0

def test_cli_validation():
    args=main.parse_args(['--input','test.mp4','--headless','--max-frames','7'])
    assert args.headless and args.max_frames==7
    with pytest.raises(SystemExit): main.parse_args(['--confidence','2'])

def test_video_io_fake_detector(monkeypatch,tmp_path):
    src=make_video(tmp_path/'synthetic.mp4',frames=12,width=320,height=240)
    target=tmp_path/'out'/'tracked.mp4'
    class FakeYOLODetector:
        def __init__(self,**kwargs): pass
        def detect(self, frame):
            return [{'bbox':(40,60,100,170),'confidence':.91,'class_id':0}]
    monkeypatch.setitem(sys.modules,'src.detection.yolo_detector',
        types.SimpleNamespace(YOLODetector=FakeYOLODetector))
    assert main.main(['--input',str(src),'--output',str(target),'--headless','--max-frames','6'])==6
    assert target.is_file() and target.stat().st_size>0
    cap=cv2.VideoCapture(str(target))
    assert cap.isOpened()
    success,frame=cap.read();cap.release()
    assert success and frame.shape[:2]==(240,320)
