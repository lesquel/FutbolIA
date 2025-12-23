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
DIXIE_SYSTEM_PROMPT = """ERES 'DIXIE', UNA IA ANALISTA DEPORTIVA DE ÉLITE CON PERSONALIDAD ÚNICA.

🎯 TU PERSONALIDAD:
- Eres apasionado, carismático y experto en fútbol mundial
- Hablas como un comentarista legendario de televisión
- Usas emojis deportivos estratégicamente (⚽🔥🏆⭐💪)
- Tienes sentido del humor pero siempre profesional
- Eres honesto: si no tienes suficientes datos, lo admites

🧠 TU ESTILO DE ANÁLISIS:
- Comienzas con una frase impactante sobre el enfrentamiento
- Das contexto histórico breve si es relevante
- Destacas las batallas tácticas clave (ej: "El duelo Vinicius vs Trent será DECISIVO")
- Mencionas datos específicos de jugadores
- Terminas con un veredicto contundente

📊 TU MÉTODO DE PREDICCIÓN:
1. Evalúas la forma reciente (últimos 5 partidos)
2. Comparas la calidad individual de las estrellas
3. Analizas matchups tácticos específicos
4. Consideras el factor local (+5-10% ventaja)
5. Evalúas la profundidad de la plantilla
6. Das un porcentaje de confianza REALISTA

💬 EJEMPLOS DE TU ESTILO:
- "¡PARTIDAZO a la vista! 🔥"
- "Esto huele a goleada..."
- "La clave está en el mediocampo"
- "Si [jugador] tiene su día, esto puede ser histórico"

⚠️ REGLAS ESTRICTAS:
- Responde SIEMPRE en JSON válido
- El "confidence" debe ser entre 1-100 (sé realista, no siempre 80%)
- El "reasoning" debe tener 3-4 oraciones con tu análisis PERSONALIZADO
- Menciona jugadores específicos por nombre
- Si faltan datos de jugadores, baja la confianza a 40-60%
- Sé creativo pero basado en los datos proporcionados
"""


def build_prediction_prompt(
    team_a: Team,
    team_b: Team,
    players_a: list[PlayerAttributes],
    players_b: list[PlayerAttributes],
    language: str = "es"
) -> str:
    """Build the structured prompt for match prediction"""
    
    # Format players info with more detail
    def format_players(players: list[PlayerAttributes], team_name: str) -> str:
        if not players:
            return f"⚠️ Sin datos de jugadores para {team_name} - Usa estimaciones generales"
        
        lines = []
        for p in players[:5]:
            # Determine player role
            if p.position in ["GK"]:
                role = "🧤 Portero"
            elif p.position in ["CB", "LB", "RB", "LWB", "RWB"]:
                role = "🛡️ Defensa"
            elif p.position in ["CDM", "CM", "CAM"]:
                role = "🎯 Mediocampo"
            else:
                role = "⚡ Ataque"
            
            # Highlight strengths
            attrs = {"Pace": p.pace, "Shot": p.shooting, "Pass": p.passing, "Def": p.defending}
            best_attr = max(attrs, key=attrs.get)
            
            lines.append(
                f"  • {p.name} ({p.position}) - OVR {p.overall_rating} | "
                f"Mejor: {best_attr} {attrs[best_attr]} | {role}"
            )
        return "\n".join(lines)
    
    # Calculate team averages and strengths
    def calc_team_profile(players: list[PlayerAttributes]) -> dict:
        if not players:
            return {
                "overall": 75, "pace": 70, "attack": 70, "defense": 70,
                "passing": 70, "physical": 70, "style": "Desconocido"
            }
        
        profile = {
            "overall": sum(p.overall_rating for p in players) // len(players),
            "pace": sum(p.pace for p in players) // len(players),
            "attack": sum(p.shooting for p in players) // len(players),
            "defense": sum(p.defending for p in players) // len(players),
            "passing": sum(p.passing for p in players) // len(players),
            "physical": sum(p.physical for p in players) // len(players),
        }
        
        # Determine playing style
        if profile["pace"] > 80:
            profile["style"] = "Contraataque rápido ⚡"
        elif profile["passing"] > 80:
            profile["style"] = "Posesión y toque 🎯"
        elif profile["defense"] > 80:
            profile["style"] = "Solidez defensiva 🛡️"
        elif profile["attack"] > 80:
            profile["style"] = "Ataque directo 🔥"
        else:
            profile["style"] = "Equilibrado ⚖️"
        
        return profile
    
    profile_a = calc_team_profile(players_a)
    profile_b = calc_team_profile(players_b)
    
    # Determine data quality
    has_good_data = len(players_a) >= 3 and len(players_b) >= 3
    data_quality = "✅ DATOS COMPLETOS" if has_good_data else "⚠️ DATOS LIMITADOS - Ajusta confianza"
    
    lang_instruction = "Responde en ESPAÑOL con tu estilo característico" if language == "es" else "Respond in ENGLISH with your characteristic style"
    
    prompt = f"""
🏟️ ANÁLISIS PRE-PARTIDO: {team_a.name} vs {team_b.name}
{data_quality}

═══════════════════════════════════════════════════
🏠 EQUIPO LOCAL: {team_a.name}
═══════════════════════════════════════════════════
📋 Liga: {team_a.league or 'Internacional'}
📈 Forma Reciente: {team_a.form or 'Sin datos'} {'🔥' if team_a.form and team_a.form.count('W') >= 3 else ''}
🎮 Estilo de juego: {profile_a['style']}

📊 PERFIL TÁCTICO:
   Ataque: {'★' * (profile_a['attack'] // 20)} ({profile_a['attack']})
   Defensa: {'★' * (profile_a['defense'] // 20)} ({profile_a['defense']})
   Velocidad: {'★' * (profile_a['pace'] // 20)} ({profile_a['pace']})
   Pases: {'★' * (profile_a['passing'] // 20)} ({profile_a['passing']})

⭐ JUGADORES CLAVE:
{format_players(players_a, team_a.name)}

═══════════════════════════════════════════════════
🚌 EQUIPO VISITANTE: {team_b.name}
═══════════════════════════════════════════════════
📋 Liga: {team_b.league or 'Internacional'}
📈 Forma Reciente: {team_b.form or 'Sin datos'} {'🔥' if team_b.form and team_b.form.count('W') >= 3 else ''}
🎮 Estilo de juego: {profile_b['style']}

📊 PERFIL TÁCTICO:
   Ataque: {'★' * (profile_b['attack'] // 20)} ({profile_b['attack']})
   Defensa: {'★' * (profile_b['defense'] // 20)} ({profile_b['defense']})
   Velocidad: {'★' * (profile_b['pace'] // 20)} ({profile_b['pace']})
   Pases: {'★' * (profile_b['passing'] // 20)} ({profile_b['passing']})

⭐ JUGADORES CLAVE:
{format_players(players_b, team_b.name)}

═══════════════════════════════════════════════════
🔍 ANÁLISIS COMPARATIVO
═══════════════════════════════════════════════════
• Diferencia Overall: {profile_a['overall'] - profile_b['overall']:+d} puntos ({'favorable a ' + team_a.name if profile_a['overall'] > profile_b['overall'] else 'favorable a ' + team_b.name if profile_b['overall'] > profile_a['overall'] else 'equilibrado'})
• Factor Local: {team_a.name} tiene +7% de ventaja por jugar en casa
• Jugadores estrella: {players_a[0].name if players_a else 'N/A'} ({players_a[0].overall_rating if players_a else 0}) vs {players_b[0].name if players_b else 'N/A'} ({players_b[0].overall_rating if players_b else 0})

═══════════════════════════════════════════════════
🎯 TU MISIÓN, DIXIE:
═══════════════════════════════════════════════════
1. Analiza el matchup táctico (¿qué estilo prevalecerá?)
2. Identifica los duelos clave (jugador vs jugador)
3. Considera el factor local y la forma reciente
4. Predice el resultado más probable
5. Da tu confianza REAL ({"40-60% si faltan datos" if not has_good_data else "basada en los datos"})

{lang_instruction}

⚠️ RESPONDE ÚNICAMENTE CON ESTE JSON (sin texto adicional):
{{
    "winner": "nombre del equipo ganador o 'Empate'",
    "predicted_score": "X-X",
    "confidence": número entre 1 y 100,
    "reasoning": "Tu análisis con estilo Dixie (3-4 oraciones, menciona jugadores, sé específico y entretenido)",
    "key_factors": ["factor clave 1", "factor clave 2", "factor clave 3", "factor clave 4"],
    "star_player_home": "nombre del jugador más influyente local",
    "star_player_away": "nombre del jugador más influyente visitante",
    "match_preview": "Una frase de apertura emocionante sobre el partido",
    "tactical_insight": "Un insight táctico específico sobre cómo se desarrollará el partido"
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
                match_preview=result_data.get("match_preview", ""),
                tactical_insight=result_data.get("tactical_insight", ""),
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
            if start == -1:
                start = content.find("[")
            
            end = content.rfind("}") + 1
            if end == 0:
                end = content.rfind("]") + 1
                
            if start != -1 and end > start:
                try:
                    return json.loads(content[start:end])
                except json.JSONDecodeError:
                    pass
        return {}

    @classmethod
    async def generate_team_players(cls, team_name: str, count: int = 11) -> list[dict]:
        """
        🤖 Use AI to get REAL players for a team when API data is missing.
        Returns a list of player dictionaries with realistic attributes.
        """
        if cls._client is None:
            return []

        prompt = f"""
        Eres un experto en bases de datos de fútbol mundial. 
        Necesito una lista de los {count} jugadores más importantes/actuales del equipo: {team_name}.
        
        Para cada jugador, proporciona:
        1. Nombre completo real.
        2. Posición (GK, CB, LB, RB, CDM, CM, CAM, LW, RW, ST).
        3. Valoración general (OVR) basada en su nivel actual (50-95).
        4. Atributos (Pace, Shooting, Passing, Dribbling, Defending, Physical) estilo FIFA.
        
        Responde ÚNICAMENTE con un JSON válido que sea una lista de objetos:
        [
          {{"name": "Nombre Real", "position": "POS", "overall_rating": 80, "pace": 75, "shooting": 70, "passing": 80, "dribbling": 78, "defending": 50, "physical": 70}},
          ...
        ]
        """
        
        try:
            response = await cls._client.chat.completions.create(
                model=settings.DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": "Eres un experto en datos de fútbol. Solo respondes en JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
            )
            
            content = response.choices[0].message.content
            players_data = cls._parse_json_response(content)
            
            if isinstance(players_data, list):
                return players_data
            return []
        except Exception as e:
            print(f"❌ Error generating real players for {team_name}: {e}")
            return []
    
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
            match_preview = f"🔥 ¡PARTIDAZO a la vista! {team_a.name} recibe a {team_b.name} en un duelo que promete emociones."
            reasoning = (
                f"⚽ Basado en los atributos de los jugadores, {team_a.name} tiene ventaja de local. "
                f"El duelo clave será {star_a} vs la defensa rival. "
                f"La diferencia de nivel ({diff:+.1f} puntos) sugiere un partido {'equilibrado' if abs(diff) < 3 else 'con ligera ventaja'}. "
                f"{'¡Espera un encuentro vibrante!' if abs(diff) < 5 else '¡El favorito debería imponerse!'}"
            )
            tactical_insight = f"La clave estará en el duelo {star_a} vs la línea defensiva visitante. Si logra generar espacios, el gol local es cuestión de tiempo."
        else:
            match_preview = f"🔥 BLOCKBUSTER incoming! {team_a.name} hosts {team_b.name} in a clash that promises fireworks."
            reasoning = (
                f"⚽ Based on player attributes, {team_a.name} has home advantage. "
                f"Key battle: {star_a} vs the opposing defense. "
                f"The skill gap ({diff:+.1f} points) suggests {'an even match' if abs(diff) < 3 else 'a slight edge'}. "
                f"{'Expect a thrilling encounter!' if abs(diff) < 5 else 'The favorite should prevail!'}"
            )
            tactical_insight = f"The key will be the {star_a} vs defensive line matchup. If they can create space, the home goal is just a matter of time."
        
        return PredictionResult(
            winner=winner,
            predicted_score=score,
            confidence=confidence,
            reasoning=reasoning,
            key_factors=[
                f"🏠 Home advantage: {team_a.name}",
                f"⭐ Star player duel: {star_a} vs {star_b}",
                f"📊 Rating difference: {diff:+.1f} points",
                f"📈 Form analysis included",
            ],
            star_player_home=star_a,
            star_player_away=star_b,
            match_preview=match_preview,
            tactical_insight=tactical_insight,
        )
