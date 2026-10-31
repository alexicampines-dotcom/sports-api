"""
Router para Fútbol: Top 5 Ligas del Mundo.
(Premier League, LaLiga EA Sports, Serie A, Bundesliga, Ligue 1)
"""
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime, timezone
from fastapi import APIRouter, Query, HTTPException

from app.config import SOCCER_LEAGUES
from app.services.espn_service import espn_service
from app.models.schemas import MatchesResponse, MatchEvent

router = APIRouter(prefix="/soccer", tags=["⚽ Fútbol (Top 5 Ligas)"])


class SoccerLeagueEnum(str, Enum):
    all = "all"
    premier_league = "premier_league"
    laliga = "laliga"
    serie_a = "serie_a"
    bundesliga = "bundesliga"
    ligue_1 = "ligue_1"


@router.get("/leagues", summary="Obtener información de las Top 5 ligas disponibles")
async def get_supported_leagues():
    """Retorna los metadatos de las 5 ligas de fútbol soportadas."""
    return {
        "description": "Las 5 ligas más vistas e importantes del fútbol mundial",
        "leagues": [
            {
                "key": key,
                "name": data["name"],
                "country": data["country"],
                "flag": data["flag"],
                "code": data["code"],
            }
            for key, data in SOCCER_LEAGUES.items()
        ],
    }


@router.get(
    "",
    response_model=MatchesResponse,
    summary="Resultados y marcadores de Fútbol (Top 5 Ligas)",
)
async def get_soccer_scores(
    league: SoccerLeagueEnum = Query(
        SoccerLeagueEnum.all,
        description="Seleccionar una liga específica o 'all' para las 5 ligas simultáneamente",
    ),
    date: Optional[str] = Query(
        None,
        description="Fecha en formato YYYYMMDD (ej: 20261030). Si se omite, devuelve la jornada actual/reciente.",
    ),
    force_refresh: bool = Query(
        False,
        description="Forzar actualización omitiendo la caché en memoria",
    ),
):
    """
    Obtiene resultados, partidos en vivo y calendario de las mejores ligas:
    - **premier_league**: Premier League inglesa
    - **laliga**: LaLiga de España
    - **serie_a**: Serie A de Italia
    - **bundesliga**: Bundesliga de Alemania
    - **ligue_1**: Ligue 1 de Francia
    - **all**: Todas las ligas consolidadas
    """
    all_events: List[MatchEvent] = []

    if league == SoccerLeagueEnum.all:
        results_by_league = await espn_service.get_all_top5_soccer(date=date, force_refresh=force_refresh)
        for league_key, events in results_by_league.items():
            all_events.extend(events)
        league_label = "Top 5 Ligas Europeas"
    else:
        events = await espn_service.get_soccer_league_matches(
            league_key=league.value,
            date=date,
            force_refresh=force_refresh,
        )
        all_events = events
        league_label = SOCCER_LEAGUES[league.value]["name"]

    return MatchesResponse(
        sport="soccer",
        league=league_label,
        total_events=len(all_events),
        updated_at=datetime.now(timezone.utc).isoformat(),
        events=all_events,
    )


@router.get("/premier-league", response_model=MatchesResponse, summary="Premier League (Inglaterra)")
async def get_premier_league(date: Optional[str] = None, force_refresh: bool = False):
    """Acceso directo a los partidos y marcadores de la Premier League inglesa."""
    events = await espn_service.get_soccer_league_matches("premier_league", date=date, force_refresh=force_refresh)
    return MatchesResponse(
        sport="soccer",
        league="Premier League",
        total_events=len(events),
        updated_at=datetime.now(timezone.utc).isoformat(),
        events=events,
    )


@router.get("/laliga", response_model=MatchesResponse, summary="LaLiga EA Sports (España)")
async def get_laliga(date: Optional[str] = None, force_refresh: bool = False):
    """Acceso directo a los partidos y marcadores de LaLiga de España."""
    events = await espn_service.get_soccer_league_matches("laliga", date=date, force_refresh=force_refresh)
    return MatchesResponse(
        sport="soccer",
        league="LaLiga EA Sports",
        total_events=len(events),
        updated_at=datetime.now(timezone.utc).isoformat(),
        events=events,
    )


@router.get("/serie-a", response_model=MatchesResponse, summary="Serie A (Italia)")
async def get_serie_a(date: Optional[str] = None, force_refresh: bool = False):
    """Acceso directo a los partidos y marcadores de la Serie A de Italia."""
    events = await espn_service.get_soccer_league_matches("serie_a", date=date, force_refresh=force_refresh)
    return MatchesResponse(
        sport="soccer",
        league="Serie A",
        total_events=len(events),
        updated_at=datetime.now(timezone.utc).isoformat(),
        events=events,
    )


@router.get("/bundesliga", response_model=MatchesResponse, summary="Bundesliga (Alemania)")
async def get_bundesliga(date: Optional[str] = None, force_refresh: bool = False):
    """Acceso directo a los partidos y marcadores de la Bundesliga de Alemania."""
    events = await espn_service.get_soccer_league_matches("bundesliga", date=date, force_refresh=force_refresh)
    return MatchesResponse(
        sport="soccer",
        league="Bundesliga",
        total_events=len(events),
        updated_at=datetime.now(timezone.utc).isoformat(),
        events=events,
    )


@router.get("/ligue-1", response_model=MatchesResponse, summary="Ligue 1 (Francia)")
async def get_ligue_1(date: Optional[str] = None, force_refresh: bool = False):
    """Acceso directo a los partidos y marcadores de la Ligue 1 de Francia."""
    events = await espn_service.get_soccer_league_matches("ligue_1", date=date, force_refresh=force_refresh)
    return MatchesResponse(
        sport="soccer",
        league="Ligue 1",
        total_events=len(events),
        updated_at=datetime.now(timezone.utc).isoformat(),
        events=events,
    )

