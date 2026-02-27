"""
Global League Registry
Catálogo completo de +50 ligas mundiales con sus identificadores en múltiples APIs
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class LeagueTier(Enum):
    """Clasificación de ligas por prioridad de datos"""

    TIER_1 = 1  # Alta prioridad - Datos completos disponibles
    TIER_2 = 2  # Media prioridad - Datos parciales
    TIER_3 = 3  # Expansión futura - Datos limitados


class Continent(Enum):
    """Continentes para clasificación geográfica"""

    EUROPE = "europe"
    SOUTH_AMERICA = "south_america"
    NORTH_AMERICA = "north_america"
    ASIA = "asia"
    AFRICA = "africa"
    OCEANIA = "oceania"
    INTERNATIONAL = "international"


@dataclass
class LeagueInfo:
    """Información completa de una liga"""

    code: str  # Código interno único
    name: str  # Nombre oficial
    country: str  # País
    continent: Continent  # Continente
    tier: LeagueTier  # Prioridad de datos

    # IDs en diferentes APIs
    football_data_id: str | None = None  # Football-Data.org
    thesportsdb_id: str | None = None  # TheSportsDB
    api_football_id: int | None = None  # API-Football

    # Metadatos adicionales
    season_start_month: int = 8  # Mes inicio temporada (agosto por defecto)
    teams_count: int = 20  # Número típico de equipos
    logo_url: str | None = None  # URL del logo de la liga
    is_active: bool = True  # Liga activa para predicciones

    def get_current_season(self) -> str:
        """Calcula la temporada actual basado en el mes de inicio"""
        from datetime import datetime

        now = datetime.now()
        year = now.year
        if now.month < self.season_start_month:
            return f"{year - 1}-{year}"
        return f"{year}-{year + 1}"


# =============================================================================
# CATÁLOGO GLOBAL DE LIGAS (+50 LIGAS)
# =============================================================================

GLOBAL_LEAGUES: dict[str, LeagueInfo] = {
    # =========================================================================
    # EUROPA - TIER 1 (Top 5 Ligas)
    # =========================================================================
    "PL": LeagueInfo(
        code="PL",
        name="Premier League",
        country="England",
        continent=Continent.EUROPE,
        tier=LeagueTier.TIER_1,
        football_data_id="PL",
        thesportsdb_id="4328",
        api_football_id=39,
        teams_count=20,
    ),
    "PD": LeagueInfo(
        code="PD",
        name="La Liga",
        country="Spain",
        continent=Continent.EUROPE,
        tier=LeagueTier.TIER_1,
        football_data_id="PD",
        thesportsdb_id="4335",
        api_football_id=140,
        teams_count=20,
    ),
    "SA": LeagueInfo(
        code="SA",
        name="Serie A",
        country="Italy",
        continent=Continent.EUROPE,
        tier=LeagueTier.TIER_1,
        football_data_id="SA",
        thesportsdb_id="4332",
        api_football_id=135,
        teams_count=20,
    ),
    "BL1": LeagueInfo(
        code="BL1",
        name="Bundesliga",
        country="Germany",
        continent=Continent.EUROPE,
        tier=LeagueTier.TIER_1,
        football_data_id="BL1",
        thesportsdb_id="4331",
        api_football_id=78,
        teams_count=18,
    ),
    "FL1": LeagueInfo(
        code="FL1",
        name="Ligue 1",
        country="France",
        continent=Continent.EUROPE,
        tier=LeagueTier.TIER_1,
        football_data_id="FL1",
        thesportsdb_id="4334",
        api_football_id=61,
        teams_count=18,
    ),
    # =========================================================================
    # EUROPA - TIER 1 (Otras Ligas Importantes)
    # =========================================================================
    "PPL": LeagueInfo(
        code="PPL",
        name="Primeira Liga",
        country="Portugal",
        continent=Continent.EUROPE,
        tier=LeagueTier.TIER_1,
        football_data_id="PPL",
        thesportsdb_id="4344",
        api_football_id=94,
        teams_count=18,
    ),
    "DED": LeagueInfo(
        code="DED",
        name="Eredivisie",
        country="Netherlands",
        continent=Continent.EUROPE,
        tier=LeagueTier.TIER_1,
        football_data_id="DED",
        thesportsdb_id="4337",
        api_football_id=88,
        teams_count=18,
    ),
    "BSA": LeagueInfo(
        code="BSA",
        name="Campeonato Brasileiro Série A",
        country="Brazil",
        continent=Continent.SOUTH_AMERICA,
        tier=LeagueTier.TIER_1,
        football_data_id="BSA",
        thesportsdb_id="4351",
        api_football_id=71,
        teams_count=20,
        season_start_month=4,  # Abril (calendario sudamericano)
    ),
    # =========================================================================
    # COMPETICIONES INTERNACIONALES - TIER 1
    # =========================================================================
    "CL": LeagueInfo(
        code="CL",
        name="UEFA Champions League",
        country="Europe",
        continent=Continent.INTERNATIONAL,
        tier=LeagueTier.TIER_1,
        football_data_id="CL",
        thesportsdb_id="4480",
        api_football_id=2,
        teams_count=32,
    ),
    "EL": LeagueInfo(
        code="EL",
        name="UEFA Europa League",
        country="Europe",
        continent=Continent.INTERNATIONAL,
        tier=LeagueTier.TIER_1,
        thesportsdb_id="4481",
        api_football_id=3,
        teams_count=32,
    ),
    "WC": LeagueInfo(
        code="WC",
        name="FIFA World Cup",
        country="International",
        continent=Continent.INTERNATIONAL,
        tier=LeagueTier.TIER_1,
        football_data_id="WC",
        thesportsdb_id="4429",
        api_football_id=1,
        teams_count=32,
    ),
    "EC": LeagueInfo(
        code="EC",
        name="UEFA European Championship",
        country="Europe",
        continent=Continent.INTERNATIONAL,
        tier=LeagueTier.TIER_1,
        football_data_id="EC",
        thesportsdb_id="4424",
        api_football_id=4,
        teams_count=24,
    ),
    "CA": LeagueInfo(
        code="CA",
        name="Copa América",
        country="South America",
        continent=Continent.INTERNATIONAL,
        tier=LeagueTier.TIER_1,
        thesportsdb_id="4477",
        api_football_id=9,
        teams_count=16,
    ),
    "COPA": LeagueInfo(
        code="COPA",
        name="Copa Libertadores",
        country="South America",
        continent=Continent.INTERNATIONAL,
        tier=LeagueTier.TIER_1,
        thesportsdb_id="4478",
        api_football_id=13,
        teams_count=32,
    ),
    # =========================================================================
    # SUDAMÉRICA - TIER 1
    # =========================================================================
    "ARG": LeagueInfo(
        code="ARG",
        name="Liga Profesional Argentina",
        country="Argentina",
        continent=Continent.SOUTH_AMERICA,
        tier=LeagueTier.TIER_1,
        thesportsdb_id="4406",
        api_football_id=128,
        teams_count=28,
        season_start_month=2,
    ),
    "ECU": LeagueInfo(
        code="ECU",
        name="Liga Pro Ecuador",
        country="Ecuador",
        continent=Continent.SOUTH_AMERICA,
        tier=LeagueTier.TIER_1,
        thesportsdb_id="4407",
        api_football_id=242,
        teams_count=16,
        season_start_month=2,
    ),
    "COL": LeagueInfo(
        code="COL",
        name="Liga BetPlay Dimayor",
        country="Colombia",
        continent=Continent.SOUTH_AMERICA,
        tier=LeagueTier.TIER_1,
        thesportsdb_id="4410",
        api_football_id=239,
        teams_count=20,
        season_start_month=1,
    ),
    "PER": LeagueInfo(
        code="PER",
        name="Liga 1 Perú",
        country="Peru",
        continent=Continent.SOUTH_AMERICA,
        tier=LeagueTier.TIER_1,
        thesportsdb_id="4411",
        api_football_id=281,
        teams_count=18,
        season_start_month=2,
    ),
    "CHI": LeagueInfo(
        code="CHI",
        name="Primera División Chile",
        country="Chile",
        continent=Continent.SOUTH_AMERICA,
        tier=LeagueTier.TIER_1,
        thesportsdb_id="4409",
        api_football_id=265,
        teams_count=16,
        season_start_month=2,
    ),
    "URU": LeagueInfo(
        code="URU",
        name="Primera División Uruguay",
        country="Uruguay",
        continent=Continent.SOUTH_AMERICA,
        tier=LeagueTier.TIER_1,
        thesportsdb_id="4412",
        api_football_id=268,
        teams_count=16,
        season_start_month=2,
    ),
    "PAR": LeagueInfo(
        code="PAR",
        name="Primera División Paraguay",
        country="Paraguay",
        continent=Continent.SOUTH_AMERICA,
        tier=LeagueTier.TIER_2,
        thesportsdb_id="4413",
        api_football_id=279,
        teams_count=12,
        season_start_month=2,
    ),
    "BOL": LeagueInfo(
        code="BOL",
        name="División Profesional Bolivia",
        country="Bolivia",
        continent=Continent.SOUTH_AMERICA,
        tier=LeagueTier.TIER_2,
        api_football_id=270,
        teams_count=16,
        season_start_month=2,
    ),
    "VEN": LeagueInfo(
        code="VEN",
        name="Liga FUTVE Venezuela",
        country="Venezuela",
        continent=Continent.SOUTH_AMERICA,
        tier=LeagueTier.TIER_2,
        api_football_id=299,
        teams_count=18,
        season_start_month=1,
    ),
    # =========================================================================
    # NORTEAMÉRICA - TIER 1
    # =========================================================================
    "MLS": LeagueInfo(
        code="MLS",
        name="Major League Soccer",
        country="USA",
        continent=Continent.NORTH_AMERICA,
        tier=LeagueTier.TIER_1,
        thesportsdb_id="4346",
        api_football_id=253,
        teams_count=29,
        season_start_month=2,
    ),
    "MX": LeagueInfo(
        code="MX",
        name="Liga MX",
        country="Mexico",
        continent=Continent.NORTH_AMERICA,
        tier=LeagueTier.TIER_1,
        thesportsdb_id="4350",
        api_football_id=262,
        teams_count=18,
        season_start_month=7,
    ),
    "MXC": LeagueInfo(
        code="MXC",
        name="Liga de Expansión MX",
        country="Mexico",
        continent=Continent.NORTH_AMERICA,
        tier=LeagueTier.TIER_2,
        api_football_id=263,
        teams_count=18,
    ),
    # =========================================================================
    # EUROPA - TIER 2 (Ligas Secundarias)
    # =========================================================================
    "ELC": LeagueInfo(
        code="ELC",
        name="EFL Championship",
        country="England",
        continent=Continent.EUROPE,
        tier=LeagueTier.TIER_2,
        football_data_id="ELC",
        thesportsdb_id="4329",
        api_football_id=40,
        teams_count=24,
    ),
    "BEL": LeagueInfo(
        code="BEL",
        name="Jupiler Pro League",
        country="Belgium",
        continent=Continent.EUROPE,
        tier=LeagueTier.TIER_2,
        thesportsdb_id="4355",
        api_football_id=144,
        teams_count=18,
    ),
    "TUR": LeagueInfo(
        code="TUR",
        name="Süper Lig",
        country="Turkey",
        continent=Continent.EUROPE,
        tier=LeagueTier.TIER_2,
        thesportsdb_id="4339",
        api_football_id=203,
        teams_count=20,
    ),
    "SCO": LeagueInfo(
        code="SCO",
        name="Scottish Premiership",
        country="Scotland",
        continent=Continent.EUROPE,
        tier=LeagueTier.TIER_2,
        thesportsdb_id="4330",
        api_football_id=179,
        teams_count=12,
    ),
    "RUS": LeagueInfo(
        code="RUS",
        name="Russian Premier League",
        country="Russia",
        continent=Continent.EUROPE,
        tier=LeagueTier.TIER_2,
        thesportsdb_id="4344",
        api_football_id=235,
        teams_count=16,
    ),
    "UKR": LeagueInfo(
        code="UKR",
        name="Ukrainian Premier League",
        country="Ukraine",
        continent=Continent.EUROPE,
        tier=LeagueTier.TIER_2,
        api_football_id=333,
        teams_count=16,
    ),
    "GRE": LeagueInfo(
        code="GRE",
        name="Super League Greece",
        country="Greece",
        continent=Continent.EUROPE,
        tier=LeagueTier.TIER_2,
        thesportsdb_id="4356",
        api_football_id=197,
        teams_count=14,
    ),
    "AUT": LeagueInfo(
        code="AUT",
        name="Austrian Bundesliga",
        country="Austria",
        continent=Continent.EUROPE,
        tier=LeagueTier.TIER_2,
        thesportsdb_id="4357",
        api_football_id=218,
        teams_count=12,
    ),
    "SUI": LeagueInfo(
        code="SUI",
        name="Swiss Super League",
        country="Switzerland",
        continent=Continent.EUROPE,
        tier=LeagueTier.TIER_2,
        thesportsdb_id="4354",
        api_football_id=207,
        teams_count=12,
    ),
    "CZE": LeagueInfo(
        code="CZE",
        name="Czech First League",
        country="Czech Republic",
        continent=Continent.EUROPE,
        tier=LeagueTier.TIER_2,
        api_football_id=345,
        teams_count=16,
    ),
    "POL": LeagueInfo(
        code="POL",
        name="Ekstraklasa",
        country="Poland",
        continent=Continent.EUROPE,
        tier=LeagueTier.TIER_2,
        thesportsdb_id="4360",
        api_football_id=106,
        teams_count=18,
    ),
    "DEN": LeagueInfo(
        code="DEN",
        name="Danish Superliga",
        country="Denmark",
        continent=Continent.EUROPE,
        tier=LeagueTier.TIER_2,
        thesportsdb_id="4352",
        api_football_id=119,
        teams_count=12,
    ),
    "NOR": LeagueInfo(
        code="NOR",
        name="Eliteserien",
        country="Norway",
        continent=Continent.EUROPE,
        tier=LeagueTier.TIER_2,
        thesportsdb_id="4358",
        api_football_id=103,
        teams_count=16,
    ),
    "SWE": LeagueInfo(
        code="SWE",
        name="Allsvenskan",
        country="Sweden",
        continent=Continent.EUROPE,
        tier=LeagueTier.TIER_2,
        thesportsdb_id="4359",
        api_football_id=113,
        teams_count=16,
    ),
    # =========================================================================
    # ASIA - TIER 2
    # =========================================================================
    "JPN": LeagueInfo(
        code="JPN",
        name="J1 League",
        country="Japan",
        continent=Continent.ASIA,
        tier=LeagueTier.TIER_2,
        thesportsdb_id="4350",
        api_football_id=98,
        teams_count=18,
        season_start_month=2,
    ),
    "KOR": LeagueInfo(
        code="KOR",
        name="K League 1",
        country="South Korea",
        continent=Continent.ASIA,
        tier=LeagueTier.TIER_2,
        thesportsdb_id="4378",
        api_football_id=292,
        teams_count=12,
        season_start_month=2,
    ),
    "CHN": LeagueInfo(
        code="CHN",
        name="Chinese Super League",
        country="China",
        continent=Continent.ASIA,
        tier=LeagueTier.TIER_2,
        thesportsdb_id="4379",
        api_football_id=169,
        teams_count=18,
        season_start_month=3,
    ),
    "SAU": LeagueInfo(
        code="SAU",
        name="Saudi Pro League",
        country="Saudi Arabia",
        continent=Continent.ASIA,
        tier=LeagueTier.TIER_2,
        thesportsdb_id="4380",
        api_football_id=307,
        teams_count=18,
    ),
    "UAE": LeagueInfo(
        code="UAE",
        name="UAE Pro League",
        country="United Arab Emirates",
        continent=Continent.ASIA,
        tier=LeagueTier.TIER_2,
        api_football_id=305,
        teams_count=14,
    ),
    "IND": LeagueInfo(
        code="IND",
        name="Indian Super League",
        country="India",
        continent=Continent.ASIA,
        tier=LeagueTier.TIER_2,
        api_football_id=323,
        teams_count=12,
        season_start_month=10,
    ),
    "AUS": LeagueInfo(
        code="AUS",
        name="A-League",
        country="Australia",
        continent=Continent.OCEANIA,
        tier=LeagueTier.TIER_2,
        thesportsdb_id="4396",
        api_football_id=188,
        teams_count=12,
        season_start_month=10,
    ),
    # =========================================================================
    # ÁFRICA - TIER 3
    # =========================================================================
    "RSA": LeagueInfo(
        code="RSA",
        name="Premier Soccer League",
        country="South Africa",
        continent=Continent.AFRICA,
        tier=LeagueTier.TIER_3,
        api_football_id=288,
        teams_count=16,
    ),
    "EGY": LeagueInfo(
        code="EGY",
        name="Egyptian Premier League",
        country="Egypt",
        continent=Continent.AFRICA,
        tier=LeagueTier.TIER_3,
        api_football_id=233,
        teams_count=18,
    ),
    "MAR": LeagueInfo(
        code="MAR",
        name="Botola Pro",
        country="Morocco",
        continent=Continent.AFRICA,
        tier=LeagueTier.TIER_3,
        api_football_id=200,
        teams_count=16,
    ),
    "NGA": LeagueInfo(
        code="NGA",
        name="Nigeria Professional League",
        country="Nigeria",
        continent=Continent.AFRICA,
        tier=LeagueTier.TIER_3,
        api_football_id=254,
        teams_count=20,
    ),
    "AFR": LeagueInfo(
        code="AFR",
        name="CAF Champions League",
        country="Africa",
        continent=Continent.INTERNATIONAL,
        tier=LeagueTier.TIER_3,
        api_football_id=12,
        teams_count=16,
    ),
}


class LeagueRegistry:
    """
    Registro centralizado de ligas con métodos de búsqueda y filtrado
    """

    @staticmethod
    def get_league(code: str) -> LeagueInfo | None:
        """Obtener información de una liga por su código"""
        return GLOBAL_LEAGUES.get(code.upper())

    @staticmethod
    def get_all_leagues() -> dict[str, LeagueInfo]:
        """Obtener todas las ligas registradas"""
        return GLOBAL_LEAGUES

    @staticmethod
    def get_leagues_by_continent(continent: Continent) -> list[LeagueInfo]:
        """Filtrar ligas por continente"""
        return [league for league in GLOBAL_LEAGUES.values() if league.continent == continent]

    @staticmethod
    def get_leagues_by_tier(tier: LeagueTier) -> list[LeagueInfo]:
        """Filtrar ligas por tier de prioridad"""
        return [league for league in GLOBAL_LEAGUES.values() if league.tier == tier]

    @staticmethod
    def get_active_leagues() -> list[LeagueInfo]:
        """Obtener solo ligas activas para predicciones"""
        return [league for league in GLOBAL_LEAGUES.values() if league.is_active]

    @staticmethod
    def get_leagues_with_api(api_name: str) -> list[LeagueInfo]:
        """
        Filtrar ligas que tienen ID en una API específica

        Args:
            api_name: 'football_data', 'thesportsdb', 'api_football'
        """
        result = []
        for league in GLOBAL_LEAGUES.values():
            if (
                api_name == "football_data"
                and league.football_data_id
                or api_name == "thesportsdb"
                and league.thesportsdb_id
                or api_name == "api_football"
                and league.api_football_id
            ):
                result.append(league)
        return result

    @staticmethod
    def search_league_by_name(name: str) -> list[LeagueInfo]:
        """Buscar ligas por nombre (fuzzy search)"""
        name_lower = name.lower()
        return [
            league
            for league in GLOBAL_LEAGUES.values()
            if name_lower in league.name.lower() or name_lower in league.country.lower()
        ]

    @staticmethod
    def get_league_codes_for_predictions() -> dict[str, str]:
        """
        Generar diccionario de mapeo nombre->código para predicciones
        Compatible con el formato actual de LEAGUE_MAPPING_PREDICTIONS
        """
        mapping = {}
        for code, league in GLOBAL_LEAGUES.items():
            if league.is_active:
                mapping[league.name] = code
                # Agregar variantes comunes del nombre
                if league.country not in league.name:
                    mapping[f"{league.name} ({league.country})"] = code
        return mapping

    @staticmethod
    def get_statistics() -> dict[str, Any]:
        """Obtener estadísticas del registro de ligas"""
        leagues = list(GLOBAL_LEAGUES.values())

        return {
            "total_leagues": len(leagues),
            "by_continent": {
                c.value: len([lg for lg in leagues if lg.continent == c]) for c in Continent
            },
            "by_tier": {
                f"tier_{t.value}": len([lg for lg in leagues if lg.tier == t]) for t in LeagueTier
            },
            "with_football_data": len([lg for lg in leagues if lg.football_data_id]),
            "with_thesportsdb": len([lg for lg in leagues if lg.thesportsdb_id]),
            "with_api_football": len([lg for lg in leagues if lg.api_football_id]),
            "active_for_predictions": len([lg for lg in leagues if lg.is_active]),
        }
