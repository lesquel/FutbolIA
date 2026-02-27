"""
Test Internacional: Verificar predicciones con ligas de todo el mundo
Argentina, Colombia, Brasil, Europa, etc.
"""
import asyncio
import sys
sys.path.insert(0, ".")

async def test_international():
    print("=" * 70)
    print("TEST INTERNACIONAL: Ligas de Todo el Mundo")
    print("=" * 70)
    
    from src.infrastructure.llm.dixie import DixieAI
    from src.domain.entities import Team, PlayerAttributes
    
    DixieAI.initialize()
    
    def convert_players(raw):
        result = []
        if not raw:
            return result
        for p in raw[:11]:
            if isinstance(p, dict):
                result.append(PlayerAttributes(
                    name=p.get("name", "Unknown"),
                    position=p.get("position", "CM"),
                    overall_rating=p.get("overall_rating", p.get("overall", 75)),
                    pace=p.get("pace", 70),
                    shooting=p.get("shooting", 65),
                    passing=p.get("passing", 70),
                    dribbling=p.get("dribbling", 68),
                    defending=p.get("defending", 50),
                    physical=p.get("physical", 70),
                ))
        return result
    
    # ========== TEST 1: LIGA ARGENTINA ==========
    print("\n" + "=" * 70)
    print("LIGA ARGENTINA: Boca Juniors vs River Plate (Superclasico)")
    print("=" * 70)
    
    boca_raw = await DixieAI.generate_team_players("Boca Juniors Argentina")
    river_raw = await DixieAI.generate_team_players("River Plate Argentina")
    
    print(f"\nBoca Juniors: {len(boca_raw)} jugadores")
    for p in boca_raw[:5]:
        print(f"   - {p.get('name')} ({p.get('position')}) OVR:{p.get('overall_rating', p.get('overall', '?'))}")
    
    print(f"\nRiver Plate: {len(river_raw)} jugadores")
    for p in river_raw[:5]:
        print(f"   - {p.get('name')} ({p.get('position')}) OVR:{p.get('overall_rating', p.get('overall', '?'))}")
    
    boca = Team(id="ar_boca", name="Boca Juniors", short_name="BOC", country="Argentina")
    river = Team(id="ar_river", name="River Plate", short_name="RIV", country="Argentina")
    
    result = await DixieAI.predict_match(boca, river, convert_players(boca_raw), convert_players(river_raw))
    
    print(f"\n--- PREDICCION ---")
    print(f"Ganador: {result.winner}")
    print(f"Marcador: {result.predicted_score}")
    print(f"Confianza: {result.confidence}%")
    print(f"Analisis: {result.reasoning[:200]}...")
    
    # ========== TEST 2: LIGA ECUATORIANA ==========
    print("\n" + "=" * 70)
    print("LIGA ECUATORIANA: Atletico Nacional vs Millonarios")
    print("=" * 70)
    
    nacional_raw = await DixieAI.generate_team_players("Atletico Nacional Ecuador")
    millos_raw = await DixieAI.generate_team_players("Millonarios Ecuador")
    
    print(f"\nAtletico Nacional: {len(nacional_raw)} jugadores")
    for p in nacional_raw[:5]:
        print(f"   - {p.get('name')} ({p.get('position')}) OVR:{p.get('overall_rating', p.get('overall', '?'))}")
    
    print(f"\nMillonarios: {len(millos_raw)} jugadores")
    for p in millos_raw[:5]:
        print(f"   - {p.get('name')} ({p.get('position')}) OVR:{p.get('overall_rating', p.get('overall', '?'))}")
    
    nacional = Team(id="ec_nacional", name="Atletico Nacional", short_name="NAL", country="Ecuador")
    millos = Team(id="ec_millos", name="Millonarios", short_name="MIL", country="Ecuador")
    
    result2 = await DixieAI.predict_match(nacional, millos, convert_players(nacional_raw), convert_players(millos_raw))
    
    print(f"\n--- PREDICCION ---")
    print(f"Ganador: {result2.winner}")
    print(f"Marcador: {result2.predicted_score}")
    print(f"Confianza: {result2.confidence}%")
    print(f"Analisis: {result2.reasoning[:200]}...")
    
    # ========== TEST 3: LIGA BRASILEIRA ==========
    print("\n" + "=" * 70)
    print("BRASILEIRAO: Flamengo vs Palmeiras")
    print("=" * 70)
    
    flamengo_raw = await DixieAI.generate_team_players("Flamengo Brasil")
    palmeiras_raw = await DixieAI.generate_team_players("Palmeiras Brasil")
    
    print(f"\nFlamengo: {len(flamengo_raw)} jugadores")
    for p in flamengo_raw[:5]:
        print(f"   - {p.get('name')} ({p.get('position')}) OVR:{p.get('overall_rating', p.get('overall', '?'))}")
    
    print(f"\nPalmeiras: {len(palmeiras_raw)} jugadores")
    for p in palmeiras_raw[:5]:
        print(f"   - {p.get('name')} ({p.get('position')}) OVR:{p.get('overall_rating', p.get('overall', '?'))}")
    
    flamengo = Team(id="br_flamengo", name="Flamengo", short_name="FLA", country="Brasil")
    palmeiras = Team(id="br_palmeiras", name="Palmeiras", short_name="PAL", country="Brasil")
    
    result3 = await DixieAI.predict_match(flamengo, palmeiras, convert_players(flamengo_raw), convert_players(palmeiras_raw))
    
    print(f"\n--- PREDICCION ---")
    print(f"Ganador: {result3.winner}")
    print(f"Marcador: {result3.predicted_score}")
    print(f"Confianza: {result3.confidence}%")
    
    # ========== TEST 4: CHAMPIONS LEAGUE ==========
    print("\n" + "=" * 70)
    print("CHAMPIONS LEAGUE: Real Madrid vs Manchester City")
    print("=" * 70)
    
    madrid_raw = await DixieAI.generate_team_players("Real Madrid")
    city_raw = await DixieAI.generate_team_players("Manchester City")
    
    print(f"\nReal Madrid: {len(madrid_raw)} jugadores")
    for p in madrid_raw[:5]:
        print(f"   - {p.get('name')} ({p.get('position')}) OVR:{p.get('overall_rating', p.get('overall', '?'))}")
    
    print(f"\nManchester City: {len(city_raw)} jugadores")
    for p in city_raw[:5]:
        print(f"   - {p.get('name')} ({p.get('position')}) OVR:{p.get('overall_rating', p.get('overall', '?'))}")
    
    madrid = Team(id="es_madrid", name="Real Madrid", short_name="RMA", country="Spain")
    city = Team(id="en_city", name="Manchester City", short_name="MCI", country="England")
    
    result4 = await DixieAI.predict_match(madrid, city, convert_players(madrid_raw), convert_players(city_raw))
    
    print(f"\n--- PREDICCION ---")
    print(f"Ganador: {result4.winner}")
    print(f"Marcador: {result4.predicted_score}")
    print(f"Confianza: {result4.confidence}%")
    print(f"Analisis: {result4.reasoning[:200]}...")
    
    # ========== TEST 5: LIGA MX ==========
    print("\n" + "=" * 70)
    print("LIGA MX: America vs Chivas (Clasico)")
    print("=" * 70)
    
    america_raw = await DixieAI.generate_team_players("Club America Mexico")
    chivas_raw = await DixieAI.generate_team_players("Chivas Guadalajara Mexico")
    
    print(f"\nClub America: {len(america_raw)} jugadores")
    for p in america_raw[:5]:
        print(f"   - {p.get('name')} ({p.get('position')}) OVR:{p.get('overall_rating', p.get('overall', '?'))}")
    
    print(f"\nChivas: {len(chivas_raw)} jugadores")
    for p in chivas_raw[:5]:
        print(f"   - {p.get('name')} ({p.get('position')}) OVR:{p.get('overall_rating', p.get('overall', '?'))}")
    
    america = Team(id="mx_america", name="Club America", short_name="AME", country="Mexico")
    chivas = Team(id="mx_chivas", name="Chivas Guadalajara", short_name="CHI", country="Mexico")
    
    result5 = await DixieAI.predict_match(america, chivas, convert_players(america_raw), convert_players(chivas_raw))
    
    print(f"\n--- PREDICCION ---")
    print(f"Ganador: {result5.winner}")
    print(f"Marcador: {result5.predicted_score}")
    print(f"Confianza: {result5.confidence}%")
    
    # ========== RESUMEN ==========
    print("\n" + "=" * 70)
    print("RESUMEN DE PREDICCIONES")
    print("=" * 70)
    print(f"1. Argentina: Boca vs River -> {result.winner} ({result.predicted_score}) {result.confidence}%")
    print(f"2. Ecuador: Nacional vs Millos -> {result2.winner} ({result2.predicted_score}) {result2.confidence}%")
    print(f"3. Brasil: Flamengo vs Palmeiras -> {result3.winner} ({result3.predicted_score}) {result3.confidence}%")
    print(f"4. Champions: Madrid vs City -> {result4.winner} ({result4.predicted_score}) {result4.confidence}%")
    print(f"5. Mexico: America vs Chivas -> {result5.winner} ({result5.predicted_score}) {result5.confidence}%")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_international())
