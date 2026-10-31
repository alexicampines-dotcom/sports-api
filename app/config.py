"""
Configuración general de la API Deportiva.
"""
from typing import Dict, Any

# Configuración de Servidor y Metadatos
API_TITLE = "API Deportiva Global (Top 5 Deportes)"
API_DESCRIPTION = """
API REST de alto rendimiento en FastAPI que centraliza resultados, marcadores en vivo y calendarios 
de los **5 deportes más vistos del mundo**:
- ⚽ **Fútbol**: Top 5 ligas (Premier League, LaLiga, Serie A, Bundesliga, Ligue 1)
- ⚾ **Béisbol (MLB)**: Grandes Ligas
- 🥊 **Artes Marciales Mixtas (UFC)**: Carteleras, peleas y resultados
- 🏀 **Baloncesto (NBA)**: Temporada regular, playoffs y marcadores
- 🏈 **Fútbol Americano (NFL)**: Partidos de la semana y marcadores

Todos los datos se obtienen en tiempo real con sistema de caché en memoria de alta velocidad.
"""
API_VERSION = "1.0.0"

# Tiempo de vida del caché en memoria (en segundos)
CACHE_TTL_SECONDS = 60

# Mapeo de ligas de fútbol (Top 5 del mundo)
SOCCER_LEAGUES: Dict[str, Dict[str, str]] = {
    "premier_league": {
        "code": "eng.1",
        "name": "Premier League",
        "country": "Inglaterra",
        "flag": "🇬🇧",
    },
    "laliga": {
        "code": "esp.1",
        "name": "LaLiga EA Sports",
        "country": "España",
        "flag": "🇪🇸",
    },
    "serie_a": {
        "code": "ita.1",
        "name": "Serie A",
        "country": "Italia",
        "flag": "🇮🇹",
    },
    "bundesliga": {
        "code": "ger.1",
        "name": "Bundesliga",
        "country": "Alemania",
        "flag": "🇩🇪",
    },
    "ligue_1": {
        "code": "fra.1",
        "name": "Ligue 1",
        "country": "Francia",
        "flag": "🇫🇷",
    },
}

# URLs base de la API de ESPN (pública y gratuita)
ESPN_ENDPOINTS: Dict[str, str] = {
    "soccer": "https://site.api.espn.com/apis/site/v2/sports/soccer/{league_code}/scoreboard",
    "mlb": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard",
    "ufc": "https://site.api.espn.com/apis/site/v2/sports/mma/ufc/scoreboard",
    "nba": "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard",
    "nfl": "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard",
}

# Configuración HTTP
HTTP_TIMEOUT = 8.0
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SportsDataHub/1.0"

