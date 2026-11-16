import os,tempfile
from fastapi.testclient import TestClient
from app import main
def test_idempotent_ingestion_and_metrics(monkeypatch):
    fd,path=tempfile.mkstemp(); os.close(fd); monkeypatch.setattr(main,"DB",path); main.init()
    c=TestClient(main.app); p={"event_id":"evt-1","event_type":"order.created","payload":{"order":7}}
    assert c.post("/events",json=p).status_code==202
    assert c.post("/events",json=p).json()["duplicate"]
    assert c.get("/metrics").json()["total_events"]==1
    os.unlink(path)
def test_validation():
    assert TestClient(main.app).post("/events",json={"event_type":"x"}).status_code==422
