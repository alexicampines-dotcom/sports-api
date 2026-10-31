"""
Esquemas Pydantic para la API Deportiva.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class VenueInfo(BaseModel):
    name: Optional[str] = Field(None, description="Nombre del estadio o arena")
    city: Optional[str] = Field(None, description="Ciudad")
    country: Optional[str] = Field(None, description="País")


class CompetitorInfo(BaseModel):
    id: str = Field(..., description="ID del equipo")
    name: str = Field(..., description="Nombre completo del equipo")
    short_name: Optional[str] = Field(None, description="Nombre corto")
    abbreviation: Optional[str] = Field(None, description="Abreviatura (ej: RMA, LAL, NYY)")
    logo: Optional[str] = Field(None, description="URL del escudo / logo")
    color: Optional[str] = Field(None, description="Color hexadecimal del equipo")
    home_away: str = Field("neutral", description="'home', 'away' o 'neutral'")
    score: Optional[str] = Field("-", description="Puntuación o goles")
    is_winner: Optional[bool] = Field(None, description="¿Resultó ganador?")
    record: Optional[str] = Field(None, description="Récord de victorias-derrotas (ej: 12-4, 5-1-2)")
    linescores: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Puntuaciones por período/cuarto/inning")


class EventStatus(BaseModel):
    state: str = Field(..., description="'pre' (programado), 'in' (en vivo), 'post' (finalizado)")
    completed: bool = Field(False, description="¿El evento ha finalizado?")
    detail: str = Field(..., description="Detalle del estado (ej: 'Final', '2nd Half - 75'', 'Hoy 19:00')")
    short_detail: Optional[str] = Field(None, description="Detalle resumido")
    clock: Optional[str] = Field(None, description="Tiempo de juego / reloj")
    period: Optional[int] = Field(None, description="Período / cuarto / tiempo actual")


class MatchEvent(BaseModel):
    id: str = Field(..., description="ID único del evento")
    sport: str = Field(..., description="Deporte (soccer, mlb, nba, nfl)")
    league: str = Field(..., description="Código de liga (ej: premier_league, mlb)")
    league_name: str = Field(..., description="Nombre legible de la liga")
    date: str = Field(..., description="Fecha y hora en formato ISO 8601")
    name: str = Field(..., description="Nombre del partido (ej: Real Madrid vs Barcelona)")
    short_name: Optional[str] = Field(None, description="Nombre abreviado")
    status: EventStatus = Field(..., description="Estado del partido")
    home_team: CompetitorInfo = Field(..., description="Equipo local")
    away_team: CompetitorInfo = Field(..., description="Equipo visitante")
    venue: Optional[VenueInfo] = Field(None, description="Estadio o sede")
    broadcasts: Optional[List[str]] = Field(default_factory=list, description="Canales de transmisión (TV/Streaming)")


# Esquemas específicos para UFC / MMA
class UFCFighter(BaseModel):
    id: str = Field(..., description="ID del peleador")
    name: str = Field(..., description="Nombre del peleador")
    nickname: Optional[str] = Field(None, description="Apodo del peleador")
    headshot: Optional[str] = Field(None, description="URL de foto del peleador")
    record: Optional[str] = Field(None, description="Récord profesional (ej: 29-0-0)")
    is_winner: Optional[bool] = Field(None, description="¿Ganó la pelea?")


class UFCFight(BaseModel):
    id: str = Field(..., description="ID de la pelea")
    order: int = Field(..., description="Orden en la cartelera")
    weight_class: Optional[str] = Field(None, description="Categoría de peso (ej: Peso Ligero, Welterweight)")
    is_title_fight: bool = Field(False, description="¿Pelea por el campeonato?")
    status: EventStatus = Field(..., description="Estado de la pelea")
    fighter_1: UFCFighter = Field(..., description="Primer peleador")
    fighter_2: UFCFighter = Field(..., description="Segundo peleador")
    winner_name: Optional[str] = Field(None, description="Nombre del peleador ganador")
    method: Optional[str] = Field(None, description="Método de victoria (KO/TKO, Sumisión, Decisión Unánime)")
    round: Optional[int] = Field(None, description="Ronda en que terminó")
    time: Optional[str] = Field(None, description="Tiempo de la ronda")


class UFCEventCard(BaseModel):
    id: str = Field(..., description="ID del evento UFC")
    name: str = Field(..., description="Nombre del evento (ej: UFC 308: Topuria vs. Holloway)")
    date: str = Field(..., description="Fecha y hora del evento")
    venue: Optional[VenueInfo] = Field(None, description="Sede o arena")
    status: EventStatus = Field(..., description="Estado global del evento")
    total_fights: int = Field(0, description="Total de peleas registradas")
    fights: List[UFCFight] = Field(default_factory=list, description="Lista de peleas de la cartelera")


# Respuestas de lista para la API
class MatchesResponse(BaseModel):
    sport: str = Field(..., description="Nombre del deporte")
    league: Optional[str] = Field(None, description="Liga consultada")
    total_events: int = Field(..., description="Número total de eventos")
    updated_at: str = Field(..., description="Marca de tiempo de actualización")
    events: List[MatchEvent] = Field(default_factory=list, description="Lista de partidos")


class UFCResponse(BaseModel):
    sport: str = Field("ufc", description="Deporte")
    total_events: int = Field(..., description="Número de eventos UFC")
    updated_at: str = Field(..., description="Marca de tiempo de actualización")
    events: List[UFCEventCard] = Field(default_factory=list, description="Eventos y carteleras de UFC")


class SummaryResponse(BaseModel):
    updated_at: str = Field(..., description="Hora de última actualización")
    sports_covered: List[str] = Field(..., description="Lista de los 5 deportes cubiertos")
    counts: Dict[str, int] = Field(..., description="Cantidad de eventos disponibles por deporte")
    soccer: List[MatchEvent] = Field(default_factory=list, description="Partidos destacados de las Top 5 ligas")
    mlb: List[MatchEvent] = Field(default_factory=list, description="Partidos destacados de MLB")
    ufc: List[UFCEventCard] = Field(default_factory=list, description="Eventos de UFC")
    nba: List[MatchEvent] = Field(default_factory=list, description="Partidos destacados de NBA")
    nfl: List[MatchEvent] = Field(default_factory=list, description="Partidos destacados de NFL")


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    message: str = "API Deportiva funcionando correctamente"

