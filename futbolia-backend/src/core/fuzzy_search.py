"""
FutbolIA - Fuzzy Search for Teams
Suggests similar team names when exact match not found
"""
from typing import List, Tuple, Optional
from difflib import SequenceMatcher
import re


# Common team name variations and aliases
TEAM_ALIASES = {
    # Spanish teams
    "real madrid": ["real", "madrid", "rm", "rmcf", "merengues", "blancos"],
    "barcelona": ["barca", "barça", "fcb", "blaugrana", "cules"],
    "atletico madrid": ["atleti", "atm", "colchoneros", "atletico"],
    
    # English teams
    "manchester city": ["city", "mcfc", "citizens", "man city"],
    "manchester united": ["united", "mufc", "red devils", "man utd", "man united"],
    "liverpool": ["lfc", "reds", "pool"],
    "chelsea": ["cfc", "blues"],
    "arsenal": ["afc", "gunners", "ars"],
    "tottenham": ["spurs", "thfc", "tottenham hotspur"],
    
    # Italian teams
    "juventus": ["juve", "vecchia signora", "bianconeri"],
    "inter milan": ["inter", "internazionale", "nerazzurri"],
    "ac milan": ["milan", "rossoneri", "diavolo"],
    "napoli": ["partenopei"],
    
    # German teams
    "bayern munich": ["bayern", "fcb", "bavarians", "bayern munchen"],
    "borussia dortmund": ["dortmund", "bvb"],
    
    # French teams
    "paris saint-germain": ["psg", "paris", "parisiens"],
    
    # South American teams
    "boca juniors": ["boca", "xeneizes"],
    "river plate": ["river", "millonarios", "gallinas"],
    "flamengo": ["mengao", "urubu"],
    "palmeiras": ["verdao", "porco"],
    "santos": ["peixe"],
    "corinthians": ["timao", "corintians"],
    "sao paulo": ["tricolor", "spfc"],
    
    # Ecuadorian teams
    "barcelona sc": ["barcelona guayaquil", "idolo", "bsc"],
    "emelec": ["bombon", "azules", "electricos"],
    "liga de quito": ["liga", "ldu", "albos", "universitarios"],
    "deportivo quito": ["deportivo", "aucas"],
    "el nacional": ["nacional", "criollos", "militares"],
    "independiente del valle": ["idv", "independiente", "rayados"],
    
    # Colombian teams
    "atletico nacional": ["nacional medellin", "verdolaga"],
    "millonarios": ["millos", "embajador"],
    "america de cali": ["america", "diablos rojos"],
    "deportivo cali": ["cali", "azucareros"],
    "junior": ["junior barranquilla", "tiburones"],
    
    # Argentine teams
    "racing club": ["racing", "academia"],
    "independiente": ["rojo", "diablos"],
    "san lorenzo": ["ciclón", "cuervos"],
    
    # National teams
    "ecuador": ["tricolor", "la tri"],
    "colombia": ["cafeteros", "los cafeteros"],
    "argentina": ["albiceleste", "la scaloneta"],
    "brazil": ["brasil", "canarinha", "seleção"],
    "uruguay": ["celeste", "charrúas"],
    "peru": ["blanquirroja", "incas"],
    "chile": ["la roja"],
    "mexico": ["el tri", "aztecas"],
}

# Country mapping for teams
TEAM_COUNTRIES = {
    # European
    "real madrid": "España", "barcelona": "España", "atletico madrid": "España",
    "manchester city": "Inglaterra", "manchester united": "Inglaterra", 
    "liverpool": "Inglaterra", "chelsea": "Inglaterra", "arsenal": "Inglaterra",
    "juventus": "Italia", "inter milan": "Italia", "ac milan": "Italia", "napoli": "Italia",
    "bayern munich": "Alemania", "borussia dortmund": "Alemania",
    "paris saint-germain": "Francia",
    
    # South American
    "boca juniors": "Argentina", "river plate": "Argentina", "racing club": "Argentina",
    "flamengo": "Brasil", "palmeiras": "Brasil", "santos": "Brasil",
    "barcelona sc": "Ecuador", "emelec": "Ecuador", "liga de quito": "Ecuador",
    "atletico nacional": "Ecuador", "millonarios": "Ecuador",  # Cambiado de Colombia a Ecuador
    
    # National teams
    "ecuador": "Ecuador", "colombia": "Colombia", "argentina": "Argentina",
    "brazil": "Brasil", "uruguay": "Uruguay", "peru": "Perú",
}

# League mapping
TEAM_LEAGUES = {
    "real madrid": "La Liga", "barcelona": "La Liga", "atletico madrid": "La Liga",
    "manchester city": "Premier League", "liverpool": "Premier League", 
    "chelsea": "Premier League", "arsenal": "Premier League",
    "juventus": "Serie A", "inter milan": "Serie A", "ac milan": "Serie A",
    "bayern munich": "Bundesliga", "borussia dortmund": "Bundesliga",
    "paris saint-germain": "Ligue 1",
    "boca juniors": "Liga Argentina", "river plate": "Liga Argentina",
    "barcelona sc": "Liga Pro Ecuador", "emelec": "Liga Pro Ecuador",
    "atletico nacional": "Liga BetPlay", "millonarios": "Liga BetPlay",
}


def normalize_text(text: str) -> str:
    """Normalize text for comparison"""
    # Convert to lowercase
    text = text.lower().strip()
    # Remove special characters except spaces
    text = re.sub(r'[^\w\s]', '', text)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    return text


def similarity_ratio(s1: str, s2: str) -> float:
    """Calculate similarity ratio between two strings"""
    return SequenceMatcher(None, normalize_text(s1), normalize_text(s2)).ratio()


def find_by_alias(query: str) -> Optional[str]:
    """Find team name by alias"""
    query_normalized = normalize_text(query)
    
    for team_name, aliases in TEAM_ALIASES.items():
        # Check exact alias match
        if query_normalized in [normalize_text(a) for a in aliases]:
            return team_name.title()
        
        # Check if query is part of team name
        if query_normalized in normalize_text(team_name):
            return team_name.title()
    
    return None


def fuzzy_search_teams(
    query: str,
    known_teams: List[str],
    threshold: float = 0.6,
    max_results: int = 5
) -> List[Tuple[str, float]]:
    """
    Find similar team names using fuzzy matching
    
    Args:
        query: Search query
        known_teams: List of known team names
        threshold: Minimum similarity score (0-1)
        max_results: Maximum number of results
        
    Returns:
        List of (team_name, similarity_score) tuples
    """
    query_normalized = normalize_text(query)
    results = []
    
    # First check aliases
    alias_match = find_by_alias(query)
    if alias_match:
        results.append((alias_match, 1.0))
    
    # Then check all known teams
    for team in known_teams:
        team_normalized = normalize_text(team)
        
        # Skip if already found via alias
        if alias_match and normalize_text(alias_match) == team_normalized:
            continue
        
        # Calculate similarity
        score = similarity_ratio(query_normalized, team_normalized)
        
        # Also check if query is substring
        if query_normalized in team_normalized or team_normalized in query_normalized:
            score = max(score, 0.8)
        
        # Check aliases for this team
        if team_normalized in TEAM_ALIASES:
            for alias in TEAM_ALIASES[team_normalized]:
                alias_score = similarity_ratio(query_normalized, normalize_text(alias))
                score = max(score, alias_score)
        
        if score >= threshold:
            results.append((team, score))
    
    # Sort by score descending
    results.sort(key=lambda x: x[1], reverse=True)
    
    return results[:max_results]


def suggest_corrections(query: str, known_teams: List[str]) -> dict:
    """
    Suggest team name corrections
    
    Returns:
        {
            "original": "brcelona",
            "suggestions": [
                {"name": "Barcelona", "score": 0.91, "country": "España"},
                {"name": "Barcelona SC", "score": 0.85, "country": "Ecuador"}
            ],
            "best_match": "Barcelona"
        }
    """
    # Add common teams to known teams if not present
    all_teams = set(known_teams)
    all_teams.update([name.title() for name in TEAM_ALIASES.keys()])
    
    matches = fuzzy_search_teams(query, list(all_teams), threshold=0.5)
    
    suggestions = []
    for name, score in matches:
        suggestion = {
            "name": name,
            "score": round(score, 2),
        }
        
        # Add country and league if known
        name_lower = name.lower()
        if name_lower in TEAM_COUNTRIES:
            suggestion["country"] = TEAM_COUNTRIES[name_lower]
        if name_lower in TEAM_LEAGUES:
            suggestion["league"] = TEAM_LEAGUES[name_lower]
        
        suggestions.append(suggestion)
    
    return {
        "original": query,
        "suggestions": suggestions,
        "best_match": suggestions[0]["name"] if suggestions else None
    }


def get_team_info(team_name: str) -> dict:
    """Get additional info about a team"""
    name_lower = team_name.lower()
    
    return {
        "name": team_name,
        "country": TEAM_COUNTRIES.get(name_lower, ""),
        "league": TEAM_LEAGUES.get(name_lower, ""),
        "aliases": TEAM_ALIASES.get(name_lower, [])
    }


def auto_complete(prefix: str, known_teams: List[str], limit: int = 10) -> List[str]:
    """
    Autocomplete team names based on prefix
    """
    prefix_normalized = normalize_text(prefix)
    
    matches = []
    
    # Add teams from aliases
    all_teams = set(known_teams)
    all_teams.update([name.title() for name in TEAM_ALIASES.keys()])
    
    for team in all_teams:
        team_normalized = normalize_text(team)
        
        # Check if team starts with prefix
        if team_normalized.startswith(prefix_normalized):
            matches.append((team, 1.0))
        # Check if any word starts with prefix
        elif any(word.startswith(prefix_normalized) for word in team_normalized.split()):
            matches.append((team, 0.9))
        # Check aliases
        elif team_normalized in TEAM_ALIASES:
            for alias in TEAM_ALIASES[team_normalized]:
                if normalize_text(alias).startswith(prefix_normalized):
                    matches.append((team, 0.8))
                    break
    
    # Sort and return unique
    matches.sort(key=lambda x: (-x[1], x[0]))
    seen = set()
    result = []
    for team, _ in matches:
        if team not in seen:
            seen.add(team)
            result.append(team)
            if len(result) >= limit:
                break
    
    return result
