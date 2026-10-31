"""
Router para Baloncesto (NBA).
"""
from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Query

from app.services.espn_service import espn_service
from app.models.schemas import MatchesResponse

router = APIRouter(prefix="/nba", tags=["🏀 Baloncesto (NBA)"])


@router.get(
    "",
    response_model=MatchesResponse,
    summary="Resultados y partidos de la NBA",
)
async def get_nba_scores(
    date: Optional[str] = Query(
        None,
        description="Fecha en formato YYYYMMDD (ej: 20261030). Si se omite, retorna la jornada de hoy/reciente.",
    ),
    force_refresh: bool = Query(
        False,
        description="Forzar actualización omitiendo la memoria caché",
    ),
):
    """
    Obtiene marcadores, puntos por cuartos (Q1, Q2, Q3, Q4, prórroga), estado en vivo y resultados finales de la NBA.
    """
    events = await espn_service.get_nba_matches(date=date, force_refresh=force_refresh)
    return MatchesResponse(
        sport="nba",
        league="National Basketball Association",
        total_events=len(events),
        updated_at=datetime.now(timezone.utc).isoformat(),
        events=events,
    )

