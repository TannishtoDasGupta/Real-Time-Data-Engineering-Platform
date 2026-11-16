import json, os, sqlite3
from datetime import datetime,timezone
from typing import Any
from fastapi import FastAPI,Query
from pydantic import BaseModel,Field
app=FastAPI(title="Real-Time Data Engineering Platform",version="1.0.0")
DB=os.getenv("EVENT_DB_PATH","events.db")
def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def init():
    with db() as c: c.execute("CREATE TABLE IF NOT EXISTS events(event_id TEXT PRIMARY KEY,event_type TEXT NOT NULL,event_time TEXT NOT NULL,payload TEXT NOT NULL)")
init()
class Event(BaseModel):
    event_id:str=Field(min_length=1,max_length=120)
    event_type:str=Field(min_length=1,max_length=80)
    payload:dict[str,Any]=Field(default_factory=dict)
@app.get("/health")
def health(): return {"status":"ok"}
@app.post("/events",status_code=202)
def ingest(e:Event):
    ts=datetime.now(timezone.utc).isoformat()
    with db() as c:
        cur=c.execute("INSERT OR IGNORE INTO events VALUES(?,?,?,?)",(e.event_id,e.event_type,ts,json.dumps(e.payload)))
        created=cur.rowcount==1
    return {"event_id":e.event_id,"accepted":True,"duplicate":not created}
@app.get("/events")
def events(limit:int=Query(100,ge=1,le=1000)):
    with db() as c: rows=c.execute("SELECT * FROM events ORDER BY event_time DESC LIMIT ?",(limit,)).fetchall()
    return [{"event_id":r["event_id"],"event_type":r["event_type"],"event_time":r["event_time"],"payload":json.loads(r["payload"])} for r in rows]
@app.get("/metrics")
def metrics():
    with db() as c: rows=c.execute("SELECT event_type,COUNT(*) total FROM events GROUP BY event_type").fetchall()
    return {"total_events":sum(r["total"] for r in rows),"by_type":[{"event_type":r["event_type"],"count":r["total"]} for r in rows]}
