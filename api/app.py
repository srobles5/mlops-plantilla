"""API de inferencia: carga el modelo y responde si un cliente de Telco abandonará el servicio (Churn)."""
import os
from pathlib import Path
from typing import Literal

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field

modelo = joblib.load(Path(os.getenv("MODEL_DIR", "models")) / "model.pkl")
app = FastAPI(title="API de predicción de Churn (Telco)")

SiNo = Literal["No", "Yes"]
SiNoSinInternet = Literal["No", "Yes", "No internet service"]


class Cliente(BaseModel):
    """Columnas del dataset (sin customerID ni Churn). Todo tiene un valor por defecto."""

    gender: Literal["Female", "Male"] = "Female"
    SeniorCitizen: Literal[0, 1] = 0
    Partner: SiNo = "No"
    Dependents: SiNo = "No"
    tenure: int = Field(12, ge=0, le=100, description="Meses como cliente")
    PhoneService: SiNo = "Yes"
    MultipleLines: Literal["No", "Yes", "No phone service"] = "No"
    InternetService: Literal["DSL", "Fiber optic", "No"] = "DSL"
    OnlineSecurity: SiNoSinInternet = "No"
    OnlineBackup: SiNoSinInternet = "No"
    DeviceProtection: SiNoSinInternet = "No"
    TechSupport: SiNoSinInternet = "No"
    StreamingTV: SiNoSinInternet = "No"
    StreamingMovies: SiNoSinInternet = "No"
    Contract: Literal["Month-to-month", "One year", "Two year"] = "Month-to-month"
    PaperlessBilling: SiNo = "Yes"
    PaymentMethod: Literal[
        "Bank transfer (automatic)",
        "Credit card (automatic)",
        "Electronic check",
        "Mailed check",
    ] = "Electronic check"
    MonthlyCharges: float = Field(70.0, ge=0)
    TotalCharges: float = Field(840.0, ge=0)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(cliente: Cliente):
    # Mismo one-hot que en src/prepare.py; reindex descarta las categorías de referencia
    # (drop_first) y rellena con 0 las columnas que el cliente no activa.
    X = pd.get_dummies(pd.DataFrame([cliente.model_dump()]), dtype=int)
    X = X.reindex(columns=modelo.feature_names_in_, fill_value=0)
    return {"prediccion": str(modelo.predict(X)[0])}
