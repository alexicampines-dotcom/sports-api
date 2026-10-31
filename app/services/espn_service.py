"""
Servicio cliente para consultar la API de ESPN y gestionar el almacenamiento en caché.
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import httpx

from app.config import (
    ESPN_ENDPOINTS,
    SOCCER_LEAGUES,
    HTTP_TIMEOUT,
    USER_AGENT,
    CACHE_TTL_SECONDS,
)
from app.services.cache import cache
from app.services.parsers import parse_team_event, parse_ufc_event
from app.models.schemas import MatchEvent, UFCEventCard

logger = logging.getLogger("sports_api")


class ESPNService:
    def __init__(self):
        self.headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        }
        self._client: Optional[httpx.AsyncClient] = None

    async def get_client(self) -> httpx.AsyncClient:
        """Obtiene o crea una instancia compartida de httpx.AsyncClient con pool de conexiones."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=HTTP_TIMEOUT, headers=self.headers)
        return self._client

    async def close(self):
        """Cierra el cliente HTTP al apagar el servidor."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def _fetch_json(self, url: str, params: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """Realiza una petición HTTP asíncrona a ESPN reutilizando la conexión."""
        try:
            client = await self.get_client()
            response = await client.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            logger.warning(f"Error HTTP {response.status_code} al consultar {url}")
            return None
        except Exception as e:
            logger.error(f"Excepción al consultar {url}: {e}")
            return None

    async def get_soccer_league_matches(
        self,
        league_key: str,
        date: Optional[str] = None,
        force_refresh: bool = False,
    ) -> List[MatchEvent]:
        """Obtiene partidos de una de las top 5 ligas de fútbol."""
        if league_key not in SOCCER_LEAGUES:
            return []

        league_info = SOCCER_LEAGUES[league_key]
        cache_key = f"soccer_{league_key}_{date or 'current'}"

        if not force_refresh:
            cached_data = await cache.get(cache_key)
            if cached_data is not None:
                return cached_data

        url = ESPN_ENDPOINTS["soccer"].format(league_code=league_info["code"])
        params = {"dates": date} if date else None

        raw_data = await self._fetch_json(url, params=params)
        events: List[MatchEvent] = []

        if raw_data and "events" in raw_data:
            for raw_event in raw_data["events"]:
                try:
                    event = parse_team_event(
                        event=raw_event,
                        sport="soccer",
                        league_code=league_key,
                        league_name=league_info["name"],
                    )
                    events.append(event)
                except Exception as ex:
                    logger.warning(f"Error parseando partido de fútbol {raw_event.get('id')}: {ex}")

        await cache.set(cache_key, events, ttl=CACHE_TTL_SECONDS)
        return events

    async def get_all_top5_soccer(
        self,
        date: Optional[str] = None,
        force_refresh: bool = False,
    ) -> Dict[str, List[MatchEvent]]:
        """Obtiene en paralelo concurrente los partidos de las Top 5 ligas del mundo."""
        league_keys = list(SOCCER_LEAGUES.keys())
        tasks = [
            self.get_soccer_league_matches(
                league_key=k,
                date=date,
                force_refresh=force_refresh,
            )
            for k in league_keys
        ]
        results_list = await asyncio.gather(*tasks)
        return dict(zip(league_keys, results_list))

    async def get_mlb_matches(
        self,
        date: Optional[str] = None,
        force_refresh: bool = False,
    ) -> List[MatchEvent]:
        """Obtiene partidos de Béisbol (MLB)."""
        cache_key = f"mlb_{date or 'current'}"

        if not force_refresh:
            cached_data = await cache.get(cache_key)
            if cached_data is not None:
                return cached_data

        url = ESPN_ENDPOINTS["mlb"]
        params = {"dates": date} if date else None
        raw_data = await self._fetch_json(url, params=params)
        events: List[MatchEvent] = []

        if raw_data and "events" in raw_data:
            for raw_event in raw_data["events"]:
                try:
                    event = parse_team_event(
                        event=raw_event,
                        sport="mlb",
                        league_code="mlb",
                        league_name="Major League Baseball",
                    )
                    events.append(event)
                except Exception as ex:
                    logger.warning(f"Error parseando juego de MLB {raw_event.get('id')}: {ex}")

        await cache.set(cache_key, events, ttl=CACHE_TTL_SECONDS)
        return events

    async def get_ufc_events(
        self,
        date: Optional[str] = None,
        force_refresh: bool = False,
    ) -> List[UFCEventCard]:
        """Obtiene eventos y carteleras de UFC / MMA."""
        cache_key = f"ufc_{date or 'current'}"

        if not force_refresh:
            cached_data = await cache.get(cache_key)
            if cached_data is not None:
                return cached_data

        url = ESPN_ENDPOINTS["ufc"]
        params = {"dates": date} if date else None
        raw_data = await self._fetch_json(url, params=params)
        events: List[UFCEventCard] = []

        if raw_data and "events" in raw_data:
            for raw_event in raw_data["events"]:
                try:
                    event_card = parse_ufc_event(raw_event)
                    events.append(event_card)
                except Exception as ex:
                    logger.warning(f"Error parseando evento UFC {raw_event.get('id')}: {ex}")

        await cache.set(cache_key, events, ttl=CACHE_TTL_SECONDS)
        return events

    async def get_nba_matches(
        self,
        date: Optional[str] = None,
        force_refresh: bool = False,
    ) -> List[MatchEvent]:
        """Obtiene partidos de Baloncesto (NBA)."""
        cache_key = f"nba_{date or 'current'}"

        if not force_refresh:
            cached_data = await cache.get(cache_key)
            if cached_data is not None:
                return cached_data

        url = ESPN_ENDPOINTS["nba"]
        params = {"dates": date} if date else None
        raw_data = await self._fetch_json(url, params=params)
        events: List[MatchEvent] = []

        if raw_data and "events" in raw_data:
            for raw_event in raw_data["events"]:
                try:
                    event = parse_team_event(
                        event=raw_event,
                        sport="nba",
                        league_code="nba",
                        league_name="National Basketball Association",
                    )
                    events.append(event)
                except Exception as ex:
                    logger.warning(f"Error parseando juego de NBA {raw_event.get('id')}: {ex}")

        await cache.set(cache_key, events, ttl=CACHE_TTL_SECONDS)
        return events

    async def get_nfl_matches(
        self,
        date: Optional[str] = None,
        force_refresh: bool = False,
    ) -> List[MatchEvent]:
        """Obtiene partidos de Fútbol Americano (NFL)."""
        cache_key = f"nfl_{date or 'current'}"

        if not force_refresh:
            cached_data = await cache.get(cache_key)
            if cached_data is not None:
                return cached_data

        url = ESPN_ENDPOINTS["nfl"]
        params = {"dates": date} if date else None
        raw_data = await self._fetch_json(url, params=params)
        events: List[MatchEvent] = []

        if raw_data and "events" in raw_data:
            for raw_event in raw_data["events"]:
                try:
                    event = parse_team_event(
                        event=raw_event,
                        sport="nfl",
                        league_code="nfl",
                        league_name="National Football League",
                    )
                    events.append(event)
                except Exception as ex:
                    logger.warning(f"Error parseando juego de NFL {raw_event.get('id')}: {ex}")

        await cache.set(cache_key, events, ttl=CACHE_TTL_SECONDS)
        return events


# Instancia única del servicio
espn_service = ESPNService()

