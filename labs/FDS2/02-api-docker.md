# Laboratorio 2 · La API del equipo en Docker

Viernes del fin de semana 2 · 70 min, y 45 min más el sábado · por equipos · hito E3

## Objetivo
Que el modelo del equipo responda predicciones por HTTP desde un contenedor, en cualquier máquina.

## Pasos

### 0. Rama de trabajo
```bash
git switch entrega/e3
git pull
git switch -c feat/api-docker
dvc pull
```
Si `entrega/e3` no existe, créenla como dice el paso 0 del [laboratorio 1](01-dagshub.md). `dvc pull` trae `models/model.pkl`.

### 1. requirements-api.txt
La API necesita menos que el entrenamiento. Creen `requirements-api.txt` en la raíz con este contenido, que también está en [la plantilla](https://github.com/srobles5/mlops-plantilla/blob/master/requirements-api.txt):
```
pandas>=2.0,<3
scikit-learn==X.Y.Z
joblib>=1.3
fastapi>=0.110
uvicorn>=0.29
pytest>=8.0
httpx>=0.27
```
Cambien `X.Y.Z` por la versión con la que entrenaron, que ven con `pip show scikit-learn`. Un modelo guardado con una versión puede fallar al cargarse con otra, y sin fijarla Docker instala la más reciente. Si reentrenan con otra versión, actualicen este número.

```bash
pip install -r requirements-api.txt
```

### 2. Ver qué columnas espera el modelo
```bash
python -c "import pandas as pd; print(pd.read_csv('data/raw/dataset.csv').iloc[0].to_dict())"
```
Anoten las columnas, salvo el objetivo y las de `drop_columns`.

### 3. api/app.py
Creen `api/app.py` con este contenido, que también está en [la plantilla](https://github.com/srobles5/mlops-plantilla/blob/master/api/app.py). Este ejemplo es de churn y solo muestra unas pocas columnas. Pongan en `Cliente` todas las de su dataset, cada una con un valor por defecto real:
```python
"""API de inferencia: carga el modelo y responde predicciones."""
import os
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

modelo = joblib.load(Path(os.getenv("MODEL_DIR", "models")) / "model.pkl")
app = FastAPI(title="API del equipo")


class Cliente(BaseModel):
    tenure: int = 12
    MonthlyCharges: float = 70.0
    Contract: str = "Month-to-month"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(cliente: Cliente):
    X = pd.get_dummies(pd.DataFrame([cliente.model_dump()]), dtype=int)
    X = X.reindex(columns=modelo.feature_names_in_, fill_value=0)
    return {"prediccion": str(modelo.predict(X)[0])}
```
`reindex` deja las columnas igual que en el entrenamiento: las que falten quedan en 0. Por eso una categoría mal escrita no da error, pero sí cambia la predicción: copien los valores tal como están en el dataset.

### 4. Probarla sin Docker
```bash
uvicorn api.app:app --reload
```
Abran http://localhost:8000/docs y entren a **POST /predict › Try it out › Execute**. Detengan el servidor con `Ctrl+C`.

### 5. Dockerfile
Creen `Dockerfile` en la raíz con este contenido, que también está en [la plantilla](https://github.com/srobles5/mlops-plantilla/blob/master/Dockerfile):
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt
COPY api/ api/
COPY models/ models/
EXPOSE 8000
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 6. Construir y correr
Con Docker Desktop abierto, construyan la imagen desde la raíz del repositorio. Es el único comando que hace falta:
```bash
docker build -t mi-api .
```
Después, en Docker Desktop:
1. Entren a **Images** y, sobre `mi-api`, pulsen **Run**.
2. Abran **Optional settings** y en el puerto escriban `8000`.
3. Pulsen **Run**.
4. En **Containers** debe aparecer corriendo. Si no, abran su nombre y miren **Logs**.

En http://localhost:8000/health debe responder `{"status":"ok"}`. En http://localhost:8000/docs, prueben `/predict` con una fila real del dataset. Luego escriban texto en un campo numérico: debe responder error 422.

Para detenerlo, usen el botón de detener en **Containers**.

En Codespaces no hay Docker Desktop. Allí se corre con este comando y el puerto se abre desde la pestaña **Ports**:
```bash
docker run --rm -p 8000:8000 mi-api
```

### 7. README
Agreguen al `README.md` del repositorio una sección con cómo construir, correr y probar la API.

### 8. Guardar y Pull Request hacia entrega/e3
```bash
git add api requirements-api.txt Dockerfile README.md
git commit -m "Sirve el modelo con FastAPI en Docker"
git push -u origin feat/api-docker
```
PR con `base: entrega/e3` ← `compare: feat/api-docker`. Otro integrante aprueba y hace el merge.

### 9. Entrega del E3 (sábado)
Alguien que no escribió el Dockerfile construye y corre la imagen desde cero. Después abran el PR con `base: master` ← `compare: entrega/e3`, reemplacen el checklist de la plantilla por el del E3 en [docs/entregas.md](../../docs/entregas.md) y llamen al docente para la revisión en la mesa.

## Listo cuando
- [ ] `/health` responde desde el contenedor.
- [ ] `/predict` da una predicción con una fila real del dataset.
- [ ] Un dato inválido devuelve error 422.
- [ ] El README explica cómo construir, correr y probar.
- [ ] Hay un PR abierto de `entrega/e3` hacia `master`.

## Errores frecuentes
- **`Cannot connect to the Docker daemon`** o **`docker_engine`**: Docker Desktop no está abierto.
- **`COPY failed` con `models`** o **`No such file` con `model.pkl`**: falta el modelo. Corran `dvc pull` antes de construir.
- **La API corre pero el navegador no conecta**: no escribieron el puerto en **Optional settings**, o falta `--host 0.0.0.0` en el `CMD`.
- **`port is already allocated`**: el puerto está ocupado. Escriban `8001` en **Optional settings** y abran `localhost:8001`.
- **`InconsistentVersionWarning` o error al cargar el modelo**: la versión de `scikit-learn` de `requirements-api.txt` no es la del entrenamiento.
- **`Could not import module "api.app"`**: corran el comando desde la raíz del repositorio.
