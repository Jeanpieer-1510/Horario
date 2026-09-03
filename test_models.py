from app.models.schedule import ClassSession, FLOORS
from app.services.excel_reader import read_excel

print("Modelos OK")
print(f"Pisos: {list(FLOORS.keys())}")
print(f"Salas Piso 1: {len(FLOORS['Primer Piso'])}")
print(f"Salas Piso 2: {len(FLOORS['Segundo Piso'])}")
print("Excel reader OK")
