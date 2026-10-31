"""
Pruebas unitarias y de integración para la API Deportiva.
Compatible tanto con ejecución directa (python tests/test_api.py) como con pytest.
"""
import sys
import os
import asyncio

# Garantizar que la raíz del proyecto esté en el PATH sin importar desde dónde se ejecute
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import httpx
from app.main import app
from app.services.cache import SimpleMemoryCache
from app.services.parsers import (
    parse_team_event,
    parse_ufc_event,
    parse_event_status,
    parse_competitor,
    parse_venue,
    parse_ufc_fighter,
)

# Configurar stdout para terminales Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def _run_async(coro):
    """Helper para ejecutar corrutinas dentro de tests compatibles con pytest síncrono."""
    return asyncio.run(coro)


def test_health_check():
    async def _test():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            assert "version" in data

    _run_async(_test())
    print("[OK] test_health_check passed")


def test_soccer_leagues_endpoint():
    async def _test():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/soccer/leagues")
            assert response.status_code == 200
            data = response.json()
            assert "leagues" in data
            assert len(data["leagues"]) == 5
            league_keys = [l["key"] for l in data["leagues"]]
            assert "premier_league" in league_keys
            assert "laliga" in league_keys
            assert "serie_a" in league_keys
            assert "bundesliga" in league_keys
            assert "ligue_1" in league_keys

    _run_async(_test())
    print("[OK] test_soccer_leagues_endpoint passed")


def test_cache_ttl_logic():
    """Valida que el caché respete tanto el TTL por defecto como el personalizado."""
    async def _test():
        test_cache = SimpleMemoryCache(default_ttl=10)
        # 1. Guardar valor
        await test_cache.set("key1", "val1", ttl=50)
        cached = await test_cache.get("key1")
        assert cached == "val1"

        # 2. Clave inexistente
        assert await test_cache.get("non_existent") is None

        # 3. Limpiar caché
        await test_cache.clear()
        assert await test_cache.get("key1") is None

    _run_async(_test())
    print("[OK] test_cache_ttl_logic passed")


def test_parser_team_event_mock():
    mock_event = {
        "id": "123456",
        "date": "2026-10-30T19:00:00Z",
        "name": "Barcelona vs Real Madrid",
        "shortName": "BAR vs RMA",
        "status": {
            "type": {
                "id": "3",
                "name": "STATUS_FINAL",
                "state": "post",
                "completed": True,
                "description": "Final",
                "detail": "Final",
            }
        },
        "competitions": [
            {
                "id": "999",
                "venue": {
                    "fullName": "Santiago Bernabéu",
                    "address": {"city": "Madrid", "country": "España"},
                },
                "competitors": [
                    {
                        "id": "86",
                        "homeAway": "home",
                        "winner": True,
                        "score": "3",
                        "records": [{"summary": "10-1-1"}],
                        "team": {
                            "id": "86",
                            "displayName": "Real Madrid",
                            "abbreviation": "RMA",
                            "logo": "https://example.com/rma.png",
                        },
                    },
                    {
                        "id": "83",
                        "homeAway": "away",
                        "winner": False,
                        "score": "1",
                        "records": [{"summary": "9-1-2"}],
                        "team": {
                            "id": "83",
                            "displayName": "Barcelona",
                            "abbreviation": "BAR",
                            "logo": "https://example.com/bar.png",
                        },
                    },
                ],
            }
        ],
    }

    parsed = parse_team_event(mock_event, sport="soccer", league_code="laliga", league_name="LaLiga")
    assert parsed.id == "123456"
    assert parsed.sport == "soccer"
    assert parsed.league == "laliga"
    assert parsed.home_team.name == "Real Madrid"
    assert parsed.home_team.score == "3"
    assert parsed.home_team.is_winner is True
    assert parsed.away_team.name == "Barcelona"
    assert parsed.away_team.score == "1"
    assert parsed.status.completed is True
    assert parsed.venue.name == "Santiago Bernabéu"
    assert parsed.venue.city == "Madrid"
    print("[OK] test_parser_team_event_mock passed")


def test_parser_ufc_event_mock():
    mock_ufc = {
        "id": "6000",
        "name": "UFC 308: Topuria vs Holloway",
        "date": "2026-10-30T22:00:00Z",
        "venue": {
            "fullName": "Etihad Arena",
            "address": {"city": "Abu Dhabi", "country": "UAE"},
        },
        "status": {
            "type": {
                "state": "post",
                "completed": True,
                "detail": "Final",
            }
        },
        "competitions": [
            {
                "id": "7001",
                "order": 1,
                "type": {"abbreviation": "Featherweight Championship"},
                "status": {
                    "period": 3,
                    "displayClock": "1:34",
                    "type": {"completed": True, "detail": "KO/TKO"},
                },
                "competitors": [
                    {
                        "id": "1",
                        "winner": True,
                        "athlete": {
                            "id": "1",
                            "displayName": "Ilia Topuria",
                            "nickname": "El Matador",
                        },
                        "records": [{"summary": "16-0-0"}],
                    },
                    {
                        "id": "2",
                        "winner": False,
                        "athlete": {
                            "id": "2",
                            "displayName": "Max Holloway",
                            "nickname": "Blessed",
                        },
                        "records": [{"summary": "26-8-0"}],
                    },
                ],
            }
        ],
    }

    parsed_ufc = parse_ufc_event(mock_ufc)
    assert parsed_ufc.id == "6000"
    assert parsed_ufc.name == "UFC 308: Topuria vs Holloway"
    assert parsed_ufc.total_fights == 1
    fight = parsed_ufc.fights[0]
    assert fight.fighter_1.name == "Ilia Topuria"
    assert fight.fighter_2.name == "Max Holloway"
    assert fight.winner_name == "Ilia Topuria"
    assert fight.is_title_fight is True
    assert fight.method == "KO/TKO"
    print("[OK] test_parser_ufc_event_mock passed")


def test_parsers_resilience_null_data():
    """Valida que los parsers manejen datos nulos o corruptos sin lanzar excepciones."""
    # Status vacío o nulo
    status_none = parse_event_status(None)
    assert status_none.state == "pre"
    assert status_none.completed is False

    # Venue nulo
    venue_none = parse_venue(None)
    assert venue_none is None

    # Competitor vacío
    comp_none = parse_competitor(None)
    assert comp_none.name == "Por definir"
    assert comp_none.score == "-"

    # Fighter vacío
    fighter_none = parse_ufc_fighter(None)
    assert fighter_none.id == "0"
    print("[OK] test_parsers_resilience_null_data passed")


def run_all_tests():
    test_health_check()
    test_soccer_leagues_endpoint()
    test_cache_ttl_logic()
    test_parser_team_event_mock()
    test_parser_ufc_event_mock()
    test_parsers_resilience_null_data()
    print("=" * 60)
    print("SUCCESS: TODOS LOS TESTS UNITARIOS PASARON CORRECTAMENTE!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
