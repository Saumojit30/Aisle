import pytest
import json
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import init_db
from app.db.seed import seed_data


@pytest.fixture(autouse=True)
def setup_db():
    import asyncio
    asyncio.run(init_db())
    asyncio.run(seed_data())


@pytest.mark.asyncio
async def test_sse_stream_calculates_node_latency():
    client = TestClient(app)
    response = client.get("/chat/stream?message=hello")
    assert response.status_code == 200
    
    content = response.text
    lines = content.split("\n")
    
    node_end_events = []
    current_event = None
    
    for line in lines:
        if line.startswith("event: "):
            current_event = line.replace("event: ", "").strip()
        elif line.startswith("data: ") and current_event == "node_end":
            data_json = line.replace("data: ", "").strip()
            try:
                data = json.loads(data_json)
                node_end_events.append(data)
            except Exception:
                pass
            current_event = None

    # Verify that at least one node_end event was emitted with elapsed_ms
    assert len(node_end_events) > 0
    for evt in node_end_events:
        assert "node" in evt
        assert "elapsed_ms" in evt
        assert isinstance(evt["elapsed_ms"], int)
        assert evt["elapsed_ms"] >= 0
