uv run uvicorn src.main:app --host 0.0.0.0 --port 8000
# Si no sirve el de arriba para correr el backend prueba el de abajo aq
uv run uvicorn src.main:app --reload

eas build -p android --profile preview
