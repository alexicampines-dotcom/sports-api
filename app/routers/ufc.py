"""
Router para Artes Marciales Mixtas (UFC / MMA).
"""
from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Query

from app.services.espn_service import espn_service
from app.models.schemas import UFCResponse

router = APIRouter(prefix="/ufc", tags=["🥊 UFC (MMA)"])


@router.get(
    "",
    response_model=UFCResponse,
    summary="Eventos, carteleras y resultados de UFC",
)
async def get_ufc_scores(
    date: Optional[str] = Query(
        None,
        description="Fecha en formato YYYYMMDD. Si se omite, retorna el evento UFC más reciente o próximo.",
    ),
    force_refresh: bool = Query(
        False,
        description="Forzar actualización omitiendo la memoria caché",
    ),
):
    """
    Obtiene la cartelera completa de UFC:
    - Evento principal (UFC Numerado o Fight Night)
    - Peleas estelares (Main Card) y preliminares
    - Peleadores, apodos, fotos y récords (victorias-derrotas-empates)
    - Ganadores, método de victoria (KO/TKO, Sumisión, Decisión) y asalto
    """
    events = await espn_service.get_ufc_events(date=date, force_refresh=force_refresh)
    return UFCResponse(
        sport="ufc",
        total_events=len(events),
        updated_at=datetime.now(timezone.utc).isoformat(),
        events=events,
    )

