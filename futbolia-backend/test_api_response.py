"""
Test API Response: Verificar que la API retorna datos de jugadores
"""

import asyncio
import sys

sys.path.insert(0, ".")


async def test_api_response():
    print("=" * 70)
    print("TEST: Verificar respuesta API con datos de jugadores")
    print("=" * 70)

    # Initialize services
    from src.infrastructure.db.mongodb import MongoDB
    from src.infrastructure.llm.dixie import DixieAI

    try:
        await MongoDB.connect()
        print("✅ MongoDB conectado")
    except Exception as e:
        print(f"⚠️ MongoDB no disponible (usando mock): {e}")

    DixieAI.initialize()

    from src.use_cases.prediction import PredictionUseCase

    # Test 1: Superclasico Argentina
    print("\n1. SUPERCLASICO: Boca Juniors vs River Plate")
    result1 = await PredictionUseCase.predict_match(
        home_team_name="Boca Juniors",
        away_team_name="River Plate",
        user_id="test_user",
        language="es",
    )

    if result1["success"]:
        pred = result1["data"]["prediction"]
        ctx = result1["data"]["context"]
        print(f"   Ganador: {pred['result']['winner']}")
        print(f"   Marcador: {pred['result']['predicted_score']}")
        print(f"   Confianza: {pred['result']['confidence']}%")
        print(f"   Home Players: {len(ctx['home_players'])}")
        print(f"   Away Players: {len(ctx['away_players'])}")
        if ctx["home_players"]:
            p = ctx["home_players"][0]
            print(f"   Ejemplo: {p['name']} ({p['position']}) OVR:{p['overall_rating']}")
    else:
        print(f"   Error: {result1.get('error')}")

    # Test 2: Champions League
    print("\n2. CHAMPIONS: Real Madrid vs Bayern Munich")
    result2 = await PredictionUseCase.predict_match(
        home_team_name="Real Madrid",
        away_team_name="Bayern Munich",
        user_id="test_user",
        language="es",
    )

    if result2["success"]:
        pred = result2["data"]["prediction"]
        ctx = result2["data"]["context"]
        print(f"   Ganador: {pred['result']['winner']}")
        print(f"   Marcador: {pred['result']['predicted_score']}")
        print(f"   Home Players: {len(ctx['home_players'])}")
        print(f"   Away Players: {len(ctx['away_players'])}")

    # Test 3: Liga Colombiana
    print("\n3. COLOMBIA: Atletico Nacional vs Santa Fe")
    result3 = await PredictionUseCase.predict_match(
        home_team_name="Atletico Nacional",
        away_team_name="Independiente Santa Fe",
        user_id="test_user",
        language="es",
    )

    if result3["success"]:
        pred = result3["data"]["prediction"]
        ctx = result3["data"]["context"]
        print(f"   Ganador: {pred['result']['winner']}")
        print(f"   Home Players: {len(ctx['home_players'])}")
        print(f"   Away Players: {len(ctx['away_players'])}")

    # Test 4: Premier League
    print("\n4. PREMIER LEAGUE: Liverpool vs Chelsea")
    result4 = await PredictionUseCase.predict_match(
        home_team_name="Liverpool", away_team_name="Chelsea", user_id="test_user", language="es"
    )

    if result4["success"]:
        pred = result4["data"]["prediction"]
        ctx = result4["data"]["context"]
        print(f"   Ganador: {pred['result']['winner']}")
        print(f"   Marcador: {pred['result']['predicted_score']}")
        print(f"   Home Players: {len(ctx['home_players'])}")
        print(f"   Away Players: {len(ctx['away_players'])}")

    print("\n" + "=" * 70)
    print("TESTS COMPLETADOS")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_api_response())
