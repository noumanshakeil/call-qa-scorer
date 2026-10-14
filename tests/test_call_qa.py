import pytest

@pytest.mark.asyncio
async def test_call_scoring(client):
    c = await client.post(
        "/api/calls",
        json={
            "title": "Refund call",
            "transcript": "Sorry for the trouble. I understand. Issue fixed. We will follow up.",
        },
    )
    rid = c.json()["id"]
    await client.post(f"/api/calls/{rid}/score")
    sc = await client.get(f"/api/calls/{rid}/scores")
    assert len(sc.json()["scores"]) >= 3
    tips = await client.get(f"/api/calls/{rid}/tips")
    assert tips.json()["tips"]
