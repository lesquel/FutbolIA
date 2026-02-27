"""
Test completo del sistema de predicciones con equipos ecuatorianos
Verifica: API, generación de jugadores, y predicciones
"""

import asyncio
import sys

sys.path.insert(0, ".")


async def test_full_system():
    print("=" * 70)
    print("🧪 TEST COMPLETO: Sistema de Predicciones FutbolIA")
    print("=" * 70)

    # ===================== TEST 1: Parser JSON Corregido =====================
    print("\n📋 TEST 1: Verificar parser JSON corregido (arrays)")
    print("-" * 50)

    from src.infrastructure.llm.dixie import DixieAI

    # Test con array JSON
    test_array = '[{"name": "Pedro", "position": "GK", "overall": 75}]'
    result = DixieAI._parse_json_response(test_array)
    print(f"Input: {test_array}")
    print(f"Output: {result}")
    print(f"Is list: {isinstance(result, list)}")

    # Test con texto envolviendo JSON
    test_wrapped = 'Aquí están los jugadores:\n[{"name": "Juan", "position": "FW", "overall": 80}]\nEspero que ayude!'
    result2 = DixieAI._parse_json_response(test_wrapped)
    print(f"\nInput con texto: {test_wrapped[:40]}...")
    print(f"Output: {result2}")
    print(f"Is list: {isinstance(result2, list)}")

    if isinstance(result, list) and isinstance(result2, list):
        print("✅ Parser JSON corregido funciona!")
    else:
        print("❌ Parser JSON aún tiene problemas")

    # ===================== TEST 2: Generar jugadores con DixieAI =====================
    print("\n📋 TEST 2: Generar jugadores REALES con DixieAI")
    print("-" * 50)

    test_teams = ["Emelec", "Barcelona SC", "LDU Quito"]

    for team in test_teams:
        print(f"\n🔄 Generando plantilla de {team}...")
        players = await DixieAI.generate_team_players(team)

        if players:
            print(f"✅ {team}: {len(players)} jugadores")
            for p in players[:5]:  # Mostrar primeros 5
                name = p.get("name", "?")
                pos = p.get("position", "?")
                ovr = p.get("overall", "?")
                print(f"   - {name} ({pos}) OVR:{ovr}")
            if len(players) > 5:
                print(f"   ... y {len(players) - 5} más")
        else:
            print(f"❌ {team}: Sin jugadores generados")

    # ===================== TEST 3: API-Football (si hay API key) =====================
    print("\n📋 TEST 3: API-Football (datos reales de plantillas)")
    print("-" * 50)

    try:
        from src.infrastructure.external_api.api_football import ECUADORIAN_TEAMS, APIFootballClient

        print(f"Equipos ecuatorianos registrados: {len(ECUADORIAN_TEAMS)}")
        for _name, info in list(ECUADORIAN_TEAMS.items())[:5]:
            print(f"   - {info['name']} (ID: {info['id']}, {info['city']})")

        # Intentar buscar un equipo
        print("\n🔍 Buscando 'Emelec' en API-Football...")
        team_data = await APIFootballClient.search_team("Emelec")

        if team_data:
            print(f"✅ Encontrado: {team_data['team']['name']}")
            print(f"   ID: {team_data['team']['id']}")
            print(f"   País: {team_data['team'].get('country', 'N/A')}")

            # Intentar obtener plantilla
            print("\n🔍 Obteniendo plantilla...")
            squad = await APIFootballClient.get_team_squad(team_data["team"]["id"])
            if squad:
                print(f"✅ Plantilla: {len(squad)} jugadores")
                for p in squad[:5]:
                    print(
                        f"   - {p['name']} ({p.get('position', 'N/A')}) #{p.get('number', 'N/A')}"
                    )
            else:
                print("⚠️ No se pudo obtener plantilla (puede requerir API key)")
        else:
            print("⚠️ No se encontró equipo (puede requerir API key válida)")

    except Exception as e:
        print(f"⚠️ API-Football no disponible: {e}")

    # ===================== TEST 4: Predicción completa =====================
    print("\n📋 TEST 4: Predicción de partido Ecuador")
    print("-" * 50)

    print("🔮 Prediciendo: Emelec vs Barcelona SC (Clásico del Astillero)")

    from src.domain.entities import PlayerAttributes, Team

    emelec = Team(id="ec_emelec", name="Emelec", short_name="EME", country="Ecuador")
    barcelona = Team(id="ec_barcelona", name="Barcelona SC", short_name="BSC", country="Ecuador")

    # Generar jugadores para la predicción
    print("   Generando jugadores de Emelec...")
    emelec_players_raw = await DixieAI.generate_team_players("Emelec")
    print("   Generando jugadores de Barcelona SC...")
    barcelona_players_raw = await DixieAI.generate_team_players("Barcelona SC")

    # Convertir a PlayerAttributes
    def to_player_attrs(players_raw):
        result = []
        if not players_raw:
            return result
        for p in players_raw[:11]:
            if isinstance(p, dict):
                result.append(
                    PlayerAttributes(
                        name=p.get("name", "Unknown"),
                        position=p.get("position", "CM"),
                        overall_rating=p.get("overall_rating", p.get("overall", 75)),
                        pace=p.get("pace", 70),
                        shooting=p.get("shooting", 65),
                        passing=p.get("passing", 70),
                        dribbling=p.get("dribbling", 68),
                        defending=p.get("defending", 50),
                        physical=p.get("physical", 70),
                    )
                )
        return result

    emelec_players = to_player_attrs(emelec_players_raw)
    barcelona_players = to_player_attrs(barcelona_players_raw)

    print(f"   Emelec: {len(emelec_players)} jugadores")
    print(f"   Barcelona SC: {len(barcelona_players)} jugadores")

    # Hacer predicción
    prediction = await DixieAI.predict_match(emelec, barcelona, emelec_players, barcelona_players)

    print("\n📊 RESULTADO DE PREDICCIÓN:")
    print(f"   🏟️ {emelec.name} vs {barcelona.name}")
    print(f"   ⚽ Marcador: {prediction.predicted_score}")
    print(f"   📈 Confianza: {prediction.confidence}%")
    print(f"   🏆 Ganador: {prediction.winner}")
    print(f"   💬 Análisis Dixie: {prediction.reasoning[:200]}...")

    if prediction.key_factors:
        print("\n   📋 Factores clave:")
        for factor in prediction.key_factors[:5]:
            print(f"      • {factor}")

    # ===================== TEST 5: Otro partido =====================
    print("\n📋 TEST 5: LDU Quito vs Independiente del Valle")
    print("-" * 50)

    ldu = Team(id="ec_ldu", name="LDU Quito", short_name="LDU", country="Ecuador")
    idv = Team(id="ec_idv", name="Independiente del Valle", short_name="IDV", country="Ecuador")

    # Generar jugadores
    ldu_players = to_player_attrs(await DixieAI.generate_team_players("LDU Quito"))
    idv_players = to_player_attrs(await DixieAI.generate_team_players("Independiente del Valle"))

    print(f"   LDU: {len(ldu_players)} jugadores")
    print(f"   IDV: {len(idv_players)} jugadores")

    prediction2 = await DixieAI.predict_match(ldu, idv, ldu_players, idv_players)

    print(f"   ⚽ Marcador: {prediction2.predicted_score}")
    print(f"   📈 Confianza: {prediction2.confidence}%")
    print(f"   🏆 Ganador: {prediction2.winner}")
    print(f"   💬 Análisis: {prediction2.reasoning[:150]}...")

    print("\n" + "=" * 70)
    print("🏁 TESTS COMPLETADOS")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_full_system())
