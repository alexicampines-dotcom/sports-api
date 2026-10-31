"""
Módulo de parseo y normalización de datos deportivos.
Convierte las respuestas crudas de ESPN a modelos Pydantic limpios.
"""
from typing import Dict, Any, List, Optional
from app.models.schemas import (
    MatchEvent,
    CompetitorInfo,
    EventStatus,
    VenueInfo,
    UFCEventCard,
    UFCFight,
    UFCFighter,
)


def parse_event_status(raw_status: Optional[Dict[str, Any]]) -> EventStatus:
    """Extrae y normaliza el estado de un evento."""
    if not raw_status or not isinstance(raw_status, dict):
        return EventStatus(
            state="pre",
            completed=False,
            detail="Programado",
            short_detail="Prog.",
        )
    
    type_info = raw_status.get("type", {})
    if not isinstance(type_info, dict):
        type_info = {}

    state = type_info.get("state", "pre")
    completed = type_info.get("completed", False)
    detail = type_info.get("detail") or type_info.get("description") or "Programado"
    short_detail = type_info.get("shortDetail") or detail
    clock = raw_status.get("displayClock")
    period = raw_status.get("period")

    return EventStatus(
        state=state,
        completed=completed,
        detail=detail,
        short_detail=short_detail,
        clock=str(clock) if clock is not None else None,
        period=period if isinstance(period, int) else None,
    )


def parse_venue(raw_venue: Optional[Dict[str, Any]]) -> Optional[VenueInfo]:
    """Extrae los datos de la sede / estadio."""
    if not raw_venue or not isinstance(raw_venue, dict):
        return None
    
    address = raw_venue.get("address", {})
    if not isinstance(address, dict):
        address = {}

    return VenueInfo(
        name=raw_venue.get("fullName") or raw_venue.get("name"),
        city=address.get("city"),
        country=address.get("country"),
    )


def parse_competitor(raw_comp: Optional[Dict[str, Any]], default_side: str = "neutral") -> CompetitorInfo:
    """Extrae los datos de un equipo competidor."""
    if not raw_comp or not isinstance(raw_comp, dict):
        return CompetitorInfo(
            id="0",
            name="Por definir",
            home_away=default_side,
            score="-",
        )

    team = raw_comp.get("team") or {}
    athlete = raw_comp.get("athlete") or {}
    if not isinstance(team, dict):
        team = {}
    if not isinstance(athlete, dict):
        athlete = {}
    
    # Puede ser equipo o atleta
    entity_id = str(team.get("id") or athlete.get("id") or raw_comp.get("id", "0"))
    name = team.get("displayName") or team.get("name") or athlete.get("displayName") or "Equipo"
    short_name = team.get("shortDisplayName") or athlete.get("shortName") or name
    abbrev = team.get("abbreviation")
    
    logo = team.get("logo")
    if not logo and isinstance(athlete.get("headshot"), dict):
        logo = athlete.get("headshot", {}).get("href")
    elif not logo and isinstance(athlete.get("headshot"), str):
        logo = athlete.get("headshot")
    
    raw_color = team.get("color")
    color = f"#{raw_color}" if raw_color and not str(raw_color).startswith("#") else raw_color
    
    score_val = raw_comp.get("score")
    score_str = str(score_val) if score_val is not None else "-"
    
    is_winner = raw_comp.get("winner")
    
    # Récord (ej: 10-2, 5-3-1)
    record_str = None
    records = raw_comp.get("records")
    if records and isinstance(records, list) and len(records) > 0:
        first_rec = records[0]
        if isinstance(first_rec, dict):
            record_str = first_rec.get("summary")
        elif isinstance(first_rec, str):
            record_str = first_rec

    linescores = raw_comp.get("linescores", [])
    
    return CompetitorInfo(
        id=entity_id,
        name=name,
        short_name=short_name,
        abbreviation=abbrev,
        logo=logo,
        color=color,
        home_away=raw_comp.get("homeAway", default_side),
        score=score_str,
        is_winner=is_winner,
        record=record_str,
        linescores=linescores if isinstance(linescores, list) else [],
    )


def parse_team_event(
    event: Dict[str, Any],
    sport: str,
    league_code: str,
    league_name: str,
) -> MatchEvent:
    """Convierte un evento de deportes de equipo (fútbol, béisbol, baloncesto, fútbol americano)."""
    competitions = event.get("competitions", [])
    comp = competitions[0] if competitions else {}
    competitors = comp.get("competitors", [])

    # Identificar local y visitante
    home_raw = next((c for c in competitors if c.get("homeAway") == "home"), None)
    away_raw = next((c for c in competitors if c.get("homeAway") == "away"), None)

    if not home_raw and len(competitors) > 0:
        home_raw = competitors[0]
    if not away_raw and len(competitors) > 1:
        away_raw = competitors[1]

    home_team = parse_competitor(home_raw or {}, default_side="home")
    away_team = parse_competitor(away_raw or {}, default_side="away")

    # Transmisiones
    broadcasts_list = []
    for b in comp.get("broadcasts", []):
        names = b.get("names", [])
        if names:
            broadcasts_list.extend(names)

    venue = parse_venue(comp.get("venue") or event.get("venue"))

    return MatchEvent(
        id=str(event.get("id", "")),
        sport=sport,
        league=league_code,
        league_name=league_name,
        date=event.get("date", ""),
        name=event.get("name", f"{away_team.name} vs {home_team.name}"),
        short_name=event.get("shortName"),
        status=parse_event_status(event.get("status", {})),
        home_team=home_team,
        away_team=away_team,
        venue=venue,
        broadcasts=broadcasts_list,
    )


def parse_ufc_fighter(raw_comp: Optional[Dict[str, Any]]) -> UFCFighter:
    """Extrae información del peleador de UFC."""
    if not raw_comp or not isinstance(raw_comp, dict):
        return UFCFighter(
            id="0",
            name="Peleador Por Confirmar",
            is_winner=False,
        )

    athlete = raw_comp.get("athlete") or raw_comp.get("team") or {}
    if not isinstance(athlete, dict):
        athlete = {}

    records = raw_comp.get("records", [])
    record_summary = None
    if records and isinstance(records, list) and len(records) > 0:
        first_rec = records[0]
        if isinstance(first_rec, dict):
            record_summary = first_rec.get("summary")
        elif isinstance(first_rec, str):
            record_summary = first_rec

    headshot_raw = athlete.get("headshot")
    headshot_url = None
    if isinstance(headshot_raw, dict):
        headshot_url = headshot_raw.get("href")
    elif isinstance(headshot_raw, str):
        headshot_url = headshot_raw

    return UFCFighter(
        id=str(athlete.get("id", raw_comp.get("id", ""))),
        name=athlete.get("displayName") or athlete.get("fullName") or "Peleador Desconocido",
        nickname=athlete.get("nickname"),
        headshot=headshot_url,
        record=record_summary,
        is_winner=raw_comp.get("winner"),
    )


def parse_ufc_fight(comp: Optional[Dict[str, Any]], order: int) -> UFCFight:
    """Extrae información de una pelea individual dentro de una cartelera de UFC."""
    if not comp or not isinstance(comp, dict):
        dummy_f = UFCFighter(id="0", name="TBD")
        return UFCFight(
            id=str(order),
            order=order,
            status=EventStatus(state="pre", completed=False, detail="Programado"),
            fighter_1=dummy_f,
            fighter_2=dummy_f,
        )

    competitors = comp.get("competitors", [])
    if not isinstance(competitors, list):
        competitors = []

    c1 = competitors[0] if len(competitors) > 0 else {}
    c2 = competitors[1] if len(competitors) > 1 else {}

    fighter_1 = parse_ufc_fighter(c1)
    fighter_2 = parse_ufc_fighter(c2)

    # Determinar ganador
    winner_name = None
    if fighter_1.is_winner:
        winner_name = fighter_1.name
    elif fighter_2.is_winner:
        winner_name = fighter_2.name

    type_info = comp.get("type", {})
    if not isinstance(type_info, dict):
        type_info = {}
    weight_class = type_info.get("abbreviation") or type_info.get("text") or "Categoría Abierta"

    # Detectar si es pelea de campeonato
    notes = comp.get("notes") or []
    if not isinstance(notes, list):
        notes = []
    is_title = any("championship" in str(n).lower() or "title" in str(n).lower() for n in notes)
    if "title" in weight_class.lower() or "championship" in weight_class.lower():
        is_title = True

    # Método de victoria
    status_dict = comp.get("status") or {}
    if not isinstance(status_dict, dict):
        status_dict = {}
    status_type = status_dict.get("type") or {}
    if not isinstance(status_type, dict):
        status_type = {}
    detail = status_type.get("detail", "")
    method = None
    if status_type.get("completed"):
        method = detail

    return UFCFight(
        id=str(comp.get("id", str(order))),
        order=order,
        weight_class=weight_class,
        is_title_fight=is_title,
        status=parse_event_status(status_dict),
        fighter_1=fighter_1,
        fighter_2=fighter_2,
        winner_name=winner_name,
        method=method,
        round=status_dict.get("period") if isinstance(status_dict.get("period"), int) else None,
        time=str(status_dict.get("displayClock")) if status_dict.get("displayClock") else None,
    )


def parse_ufc_event(event: Dict[str, Any]) -> UFCEventCard:
    """Convierte el evento de UFC con su cartelera de peleas."""
    competitions = event.get("competitions", [])
    fights = []
    for idx, comp in enumerate(competitions, start=1):
        fights.append(parse_ufc_fight(comp, idx))

    return UFCEventCard(
        id=str(event.get("id", "")),
        name=event.get("name", "Evento UFC"),
        date=event.get("date", ""),
        venue=parse_venue(event.get("venue")),
        status=parse_event_status(event.get("status", {})),
        total_fights=len(fights),
        fights=fights,
    )

