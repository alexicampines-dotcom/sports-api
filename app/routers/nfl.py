"""
Router para Fútbol Americano (NFL).
"""
from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Query

from app.services.espn_service import espn_service
from app.models.schemas import MatchesResponse

router = APIRouter(prefix="/nfl", tags=["🏈 Fútbol Americano (NFL)"])


@router.get(
    "",
    response_model=MatchesResponse,
    summary="Resultados y partidos de la NFL",
)
async def get_nfl_scores(
    date: Optional[str] = Query(
        None,
        description="Fecha en formato YYYYMMDD (ej: 20261030). Si se omite, retorna los partidos de la semana en curso.",
    ),
    force_refresh: bool = Query(
        False,
        description="Forzar actualización omitiendo la memoria caché",
    ),
):
    """
    Obtiene marcadores, cuartos, touchdowns, goles de campo y estado en vivo de los partidos de la NFL.
    """
    events = await espn_service.get_nfl_matches(date=date, force_refresh=force_refresh)
    return MatchesResponse(
        sport="nfl",
        league="National Football League",
        total_events=len(events),
        updated_at=datetime.now(timezone.utc).isoformat(),
        events=events,
    )

