from fastapi import FastAPI
import time
import threading

app = FastAPI()

NODES = {}
METRICS = {}

@app.post("/register")
def register(node: dict):
    node_id = node["node_id"]
    NODES[node_id] = {
        "ip": node["ip"],
        "stake": node.get("stake", 0),
        "last_seen": time.time()
    }
    return {"status": "registered", "node_id": node_id}

@app.post("/heartbeat")
def heartbeat(data: dict):
    node_id = data["node_id"]
    METRICS[node_id] = data
    if node_id in NODES:
        NODES[node_id]["last_seen"] = time.time()
    return {"ok": True}

@app.get("/cluster")
def cluster():
    return {
        "nodes": NODES,
        "metrics": METRICS
    }
