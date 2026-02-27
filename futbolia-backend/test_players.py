"""
Test script for player generation and predictions
"""
import asyncio
import json
from openai import AsyncOpenAI
from src.core.config import settings
from src.infrastructure.llm.dixie import DixieAI
from src.infrastructure.chromadb.player_store import PlayerVectorStore


async def test_deepseek_direct():
    """Test DeepSeek API directly"""
    print("=" * 60)
    print("TEST 1: DeepSeek API directo - Jugadores Emelec")
    print("=" * 60)
    
    client = AsyncOpenAI(
        api_key=settings.DEEPSEEK_API_KEY,
        base_url=settings.DEEPSEEK_BASE_URL,
    )
    
    prompt = """Dame una lista JSON de 11 jugadores actuales del Club Sport Emelec de Ecuador (2024-2025).
    
    Responde SOLO con JSON valido, sin texto adicional:
    [
      {"name": "Nombre Completo", "position": "POS", "overall_rating": 75, "pace": 70, "shooting": 65, "passing": 70, "dribbling": 68, "defending": 60, "physical": 72}
    ]
    
    Posiciones validas: GK, CB, LB, RB, CDM, CM, CAM, LW, RW, ST
    """
    
    try:
        response = await client.chat.completions.create(
            model=settings.DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": "Eres experto en futbol sudamericano. Solo respondes JSON valido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        
        content = response.choices[0].message.content
        print(f"Raw response:\n{content[:1000]}")
        
        # Parse
        try:
            start = content.find("[")
            end = content.rfind("]") + 1
            if start != -1 and end > start:
                players = json.loads(content[start:end])
                print(f"\n✅ Parsed {len(players)} players:")
                for p in players[:5]:
                    print(f"  - {p.get('name')} ({p.get('position')}) OVR:{p.get('overall_rating')}")
                return players
        except Exception as e:
            print(f"Parse error: {e}")
    except Exception as e:
        print(f"API Error: {e}")
    
    return []


async def test_dixie_generation():
    """Test Dixie player generation"""
    print("\n" + "=" * 60)
    print("TEST 2: Dixie AI - Generacion de jugadores")
    print("=" * 60)
    
    DixieAI.initialize()
    
    teams = ["Emelec", "Barcelona SC", "Liga de Quito"]
    
    for team in teams:
        print(f"\n{team}:")
        players = await DixieAI.generate_team_players(team, count=11)
        if players:
            print(f"  ✅ {len(players)} jugadores")
            for p in players[:3]:
                print(f"    - {p.get('name')} ({p.get('position')}) OVR:{p.get('overall_rating')}")
        else:
            print(f"  ❌ Sin jugadores")


async def test_prediction():
    """Test prediction with Ecuadorian teams"""
    print("\n" + "=" * 60)
    print("TEST 3: Prediccion Emelec vs Barcelona SC")
    print("=" * 60)
    
    from src.domain.entities import Team
    
    DixieAI.initialize()
    PlayerVectorStore.initialize()
    
    # Create teams
    emelec = Team(id="emelec", name="Emelec", short_name="EME", country="Ecuador", league="LigaPro")
    barcelona = Team(id="barcelona_sc", name="Barcelona SC", short_name="BSC", country="Ecuador", league="LigaPro")
    
    # Get players
    emelec_players = PlayerVectorStore.search_by_team("Emelec", limit=11)
    barcelona_players = PlayerVectorStore.search_by_team("Barcelona SC", limit=11)
    
    print(f"Emelec players in DB: {len(emelec_players)}")
    print(f"Barcelona SC players in DB: {len(barcelona_players)}")
    
    # Generate prediction
    result = await DixieAI.predict_match(
        team_a=emelec,
        team_b=barcelona,
        players_a=emelec_players,
        players_b=barcelona_players,
        language="es"
    )
    
    print(f"\nResultado prediccion:")
    print(f"  Ganador: {result.winner}")
    print(f"  Score: {result.predicted_score}")
    print(f"  Confianza: {result.confidence}%")
    print(f"  Razon: {result.reasoning[:200]}...")


async def main():
    """Run all tests"""
    # Test 1: Direct API
    players = await test_deepseek_direct()
    
    # Test 2: Dixie generation
    await test_dixie_generation()
    
    # Test 3: Prediction
    await test_prediction()
    
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print("Si los tests muestran jugadores genericos o errores,")
    print("necesitamos integrar una API de datos de futbol mejor.")


if __name__ == "__main__":
    asyncio.run(main())
