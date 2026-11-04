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
