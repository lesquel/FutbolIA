"""
Dixie - The Elite Sports Analyst AI
DeepSeek integration for tactical football predictions
"""
import json
from typing import Optional
from openai import AsyncOpenAI

from src.core.config import settings
from src.domain.entities import Team, PredictionResult, PlayerAttributes


# Dixie's System Prompt - The Expert Sports Analyst
DIXIE_SYSTEM_PROMPT = """ERES 'DIXIE', UNA IA ANALISTA DEPORTIVA DE ÉLITE.

🎯 TU PERSONALIDAD:
- Profesional pero apasionado por el fútbol
- Basas TODO en datos y estadísticas reales
- Hablas como un comentarista experto de televisión
- Usas emojis deportivos para dar énfasis (⚽🔥🏆)
- NUNCA inventas datos, solo usas lo que te proporcionan

📊 TU MÉTODO DE ANÁLISIS:
1. Evalúas la forma reciente de ambos equipos
2. Comparas los atributos de jugadores clave
3. Analizas las fortalezas vs debilidades tácticas
4. Consideras el factor local/visitante (+5-10% ventaja local)
5. Das un veredicto basado en probabilidades

⚠️ REGLAS ESTRICTAS:
- Responde SIEMPRE en JSON válido
- El campo "confidence" debe estar entre 1 y 100
- El campo "reasoning" debe ser un análisis táctico de 2-3 oraciones
- Sé honesto: si los datos son insuficientes, indica confianza baja
"""


def build_prediction_prompt(
    team_a: Team,
    team_b: Team,
    players_a: list[PlayerAttributes],
    players_b: list[PlayerAttributes],
    language: str = "es"
) -> str:
    """Build the structured prompt for match prediction"""
    
    # Format players info
    def format_players(players: list[PlayerAttributes]) -> str:
        if not players:
            return "Sin datos de jugadores"
        return "\n".join([
            f"  - {p.name} ({p.position}): Overall {p.overall_rating}, "
            f"Pace {p.pace}, Shooting {p.shooting}, Defending {p.defending}"
            for p in players[:5]
        ])
    
    # Calculate team averages
    def calc_avg(players: list[PlayerAttributes]) -> dict:
        if not players:
            return {"overall": 75, "pace": 70, "attack": 70, "defense": 70}
        return {
            "overall": sum(p.overall_rating for p in players) // len(players),
            "pace": sum(p.pace for p in players) // len(players),
            "attack": sum(p.shooting for p in players) // len(players),
            "defense": sum(p.defending for p in players) // len(players),
        }
    
    avg_a = calc_avg(players_a)
    avg_b = calc_avg(players_b)
    
    lang_instruction = "Responde en ESPAÑOL" if language == "es" else "Respond in ENGLISH"
    
    prompt = f"""
📋 ANÁLISIS DE ENFRENTAMIENTO

🏠 EQUIPO LOCAL: {team_a.name}
- Liga: {team_a.league or 'Champions League'}
- Forma Reciente: {team_a.form or 'N/A'}
- Rating Ataque: {avg_a['attack']} | Rating Defensa: {avg_a['defense']}
- Jugadores Clave:
{format_players(players_a)}

🚌 EQUIPO VISITANTE: {team_b.name}
- Liga: {team_b.league or 'Champions League'}
- Forma Reciente: {team_b.form or 'N/A'}
- Rating Ataque: {avg_b['attack']} | Rating Defensa: {avg_b['defense']}
- Jugadores Clave:
{format_players(players_b)}

📊 COMPARATIVA TÁCTICA:
- Diferencia Overall: {avg_a['overall'] - avg_b['overall']:+d} a favor de {team_a.name if avg_a['overall'] > avg_b['overall'] else team_b.name}
- Velocidad Promedio: {team_a.name} ({avg_a['pace']}) vs {team_b.name} ({avg_b['pace']})
- Factor Local: {team_a.name} tiene +7% de ventaja por jugar en casa

🎯 TAREA:
1. Analiza qué equipo tiene ventaja táctica y por qué
2. Predice el resultado más probable (victoria local, empate, victoria visitante)
3. Sugiere un marcador exacto realista
4. Calcula tu porcentaje de confianza (1-100)

{lang_instruction}

⚠️ RESPONDE ÚNICAMENTE CON ESTE JSON (sin texto adicional):
{{
    "winner": "nombre del equipo ganador o 'Empate'",
    "predicted_score": "X-X",
    "confidence": número entre 1 y 100,
    "reasoning": "análisis táctico en 2-3 oraciones",
    "key_factors": ["factor1", "factor2", "factor3"],
    "star_player_home": "nombre del jugador más influyente local",
    "star_player_away": "nombre del jugador más influyente visitante"
}}
"""
    return prompt


class DixieAI:
    """Dixie - The AI Sports Analyst powered by DeepSeek"""
    
    _client: Optional[AsyncOpenAI] = None
    
    @classmethod
    def initialize(cls) -> None:
        """Initialize the DeepSeek client"""
        if not settings.DEEPSEEK_API_KEY:
            print("⚠️ DEEPSEEK_API_KEY not set. Dixie will use mock responses.")
            return
        
        cls._client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
        )
        print("✅ Dixie AI initialized with DeepSeek")
    
    @classmethod
    async def predict_match(
        cls,
        team_a: Team,
        team_b: Team,
        players_a: list[PlayerAttributes],
        players_b: list[PlayerAttributes],
        language: str = "es"
    ) -> PredictionResult:
        """Generate a match prediction using Dixie AI"""
        
        # Build the prompt
        prompt = build_prediction_prompt(team_a, team_b, players_a, players_b, language)
        
        # If no API key, return mock response
        if cls._client is None:
            return cls._generate_mock_prediction(team_a, team_b, players_a, players_b, language)
        
        try:
            # Call DeepSeek
            response = await cls._client.chat.completions.create(
                model=settings.DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": DIXIE_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000,
            )
            
            # Parse JSON response
            content = response.choices[0].message.content
            
            # Try to extract JSON from response
            result_data = cls._parse_json_response(content)
            
            return PredictionResult(
                winner=result_data.get("winner", team_a.name),
                predicted_score=result_data.get("predicted_score", "1-0"),
                confidence=min(100, max(1, result_data.get("confidence", 50))),
                reasoning=result_data.get("reasoning", "Análisis no disponible"),
                key_factors=result_data.get("key_factors", []),
                star_player_home=result_data.get("star_player_home", ""),
                star_player_away=result_data.get("star_player_away", ""),
            )
            
        except Exception as e:
            print(f"❌ Dixie AI error: {e}")
            return cls._generate_mock_prediction(team_a, team_b, players_a, players_b, language)
    
    @staticmethod
    def _parse_json_response(content: str) -> dict:
        """Extract and parse JSON from LLM response"""
        try:
            # Try direct parse
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to find JSON in response
            start = content.find("{")
            end = content.rfind("}") + 1
            if start != -1 and end > start:
                try:
                    return json.loads(content[start:end])
                except json.JSONDecodeError:
                    pass
        return {}
    
    @staticmethod
    def _generate_mock_prediction(
        team_a: Team,
        team_b: Team,
        players_a: list[PlayerAttributes],
        players_b: list[PlayerAttributes],
        language: str
    ) -> PredictionResult:
        """Generate a mock prediction when API is not available"""
        
        # Calculate simple averages for mock prediction
        avg_a = sum(p.overall_rating for p in players_a) / len(players_a) if players_a else 75
        avg_b = sum(p.overall_rating for p in players_b) / len(players_b) if players_b else 75
        
        # Add home advantage
        avg_a += 3
        
        # Determine winner
        diff = avg_a - avg_b
        if diff > 3:
            winner = team_a.name
            score = "2-1"
            confidence = min(85, 60 + int(diff * 2))
        elif diff < -3:
            winner = team_b.name
            score = "1-2"
            confidence = min(85, 60 + int(abs(diff) * 2))
        else:
            winner = "Empate" if language == "es" else "Draw"
            score = "1-1"
            confidence = 45
        
        star_a = max(players_a, key=lambda p: p.overall_rating).name if players_a else "N/A"
        star_b = max(players_b, key=lambda p: p.overall_rating).name if players_b else "N/A"
        
        if language == "es":
            reasoning = (
                f"⚽ Basado en los atributos de los jugadores, {team_a.name} tiene ventaja de local. "
                f"El duelo clave será {star_a} vs la defensa rival. "
                f"La diferencia de nivel ({diff:+.1f} puntos) sugiere un partido {'equilibrado' if abs(diff) < 3 else 'con ligera ventaja'}."
            )
        else:
            reasoning = (
                f"⚽ Based on player attributes, {team_a.name} has home advantage. "
                f"Key battle: {star_a} vs the opposing defense. "
                f"The skill gap ({diff:+.1f} points) suggests {'an even match' if abs(diff) < 3 else 'a slight edge'}."
            )
        
        return PredictionResult(
            winner=winner,
            predicted_score=score,
            confidence=confidence,
            reasoning=reasoning,
            key_factors=[
                f"Home advantage: {team_a.name}",
                f"Star player: {star_a}",
                f"Overall rating difference: {diff:+.1f}",
            ],
            star_player_home=star_a,
            star_player_away=star_b,
        )
