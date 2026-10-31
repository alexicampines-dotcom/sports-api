"""
Router para Béisbol (Major League Baseball - MLB).
"""
from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Query

from app.services.espn_service import espn_service
from app.models.schemas import MatchesResponse

router = APIRouter(prefix="/mlb", tags=["⚾ Béisbol (MLB)"])


@router.get(
    "",
    response_model=MatchesResponse,
    summary="Resultados y partidos de MLB (Grandes Ligas)",
)
async def get_mlb_scores(
    date: Optional[str] = Query(
        None,
        description="Fecha en formato YYYYMMDD (ej: 20261030). Si se omite, retorna los juegos del día/recientes.",
    ),
    force_refresh: bool = Query(
        False,
        description="Forzar actualización omitiendo la memoria caché",
    ),
):
    """
    Obtiene marcadores, carreras, hits, errores e innings de los partidos de la MLB.
    Incluye juegos de pretemporada, temporada regular y Serie Mundial.
    """
    events = await espn_service.get_mlb_matches(date=date, force_refresh=force_refresh)
    return MatchesResponse(
        sport="mlb",
        league="Major League Baseball",
        total_events=len(events),
        updated_at=datetime.now(timezone.utc).isoformat(),
        events=events,
    )

