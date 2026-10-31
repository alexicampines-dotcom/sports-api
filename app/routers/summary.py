"""
Router de Resumen Global (Dashboard de los 5 Deportes).
Ideal para la portada de la web deportiva.
"""
import asyncio
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Query

from app.services.espn_service import espn_service
from app.models.schemas import SummaryResponse

router = APIRouter(prefix="/summary", tags=["🌐 Resumen General"])


@router.get(
    "",
    response_model=SummaryResponse,
    summary="Resumen integral de los 5 deportes más vistos",
)
async def get_sports_summary(
    date: Optional[str] = Query(
        None,
        description="Fecha opcional en formato YYYYMMDD para consultar un día específico",
    ),
    force_refresh: bool = Query(
        False,
        description="Forzar actualización omitiendo la memoria caché",
    ),
):
    """
    Retorna en **una sola llamada ultrarrápida** los resultados y partidos destacados
    de los 5 deportes más seguidos del mundo:
    - ⚽ **Fútbol**: Top 5 Ligas (Premier, LaLiga, Serie A, Bundesliga, Ligue 1)
    - ⚾ **Béisbol**: Major League Baseball (MLB)
    - 🥊 **UFC**: Evento y combates actuales
    - 🏀 **Baloncesto**: NBA
    - 🏈 **Fútbol Americano**: NFL

    Diseñado específicamente para construir el Home / Portada de portales deportivos.
    """
    # Consulta concurrente de los 5 deportes usando asyncio.gather
    soccer_task = espn_service.get_all_top5_soccer(date=date, force_refresh=force_refresh)
    mlb_task = espn_service.get_mlb_matches(date=date, force_refresh=force_refresh)
    ufc_task = espn_service.get_ufc_events(date=date, force_refresh=force_refresh)
    nba_task = espn_service.get_nba_matches(date=date, force_refresh=force_refresh)
    nfl_task = espn_service.get_nfl_matches(date=date, force_refresh=force_refresh)

    soccer_dict, mlb_events, ufc_events, nba_events, nfl_events = await asyncio.gather(
        soccer_task, mlb_task, ufc_task, nba_task, nfl_task
    )

    # Consolidar todos los partidos de fútbol
    all_soccer_events = []
    for league_events in soccer_dict.values():
        all_soccer_events.extend(league_events)

    counts = {
        "soccer": len(all_soccer_events),
        "mlb": len(mlb_events),
        "ufc": len(ufc_events),
        "nba": len(nba_events),
        "nfl": len(nfl_events),
        "total": len(all_soccer_events) + len(mlb_events) + len(ufc_events) + len(nba_events) + len(nfl_events),
    }

    return SummaryResponse(
        updated_at=datetime.now(timezone.utc).isoformat(),
        sports_covered=["soccer", "mlb", "ufc", "nba", "nfl"],
        counts=counts,
        soccer=all_soccer_events,
        mlb=mlb_events,
        ufc=ufc_events,
        nba=nba_events,
        nfl=nfl_events,
    )

