# Proyecto integrador · [nombre del equipo]

Curso Despliegue y monitoreo de Machine Learning.

| | |
|---|---|
| Dataset | [nombre y enlace] |
| Pregunta de negocio | [¿qué se quiere predecir y para qué?] |
| Métrica de éxito | [por ejemplo, F1 de al menos __] |
| Integrantes y roles | [ML engineer · Platform engineer · Calidad y documentación] |

## Cómo reproducir
```bash
pip install -r requirements.txt
dvc pull
dvc repro
```

## Estructura
```
data/raw/        dataset original (versionado con DVC)
data/prepared/   salida de la etapa prepare
models/          modelo entrenado
src/             scripts de cada etapa
api/             API de inferencia (fin de semana 2)
tests/           pruebas de la API (fin de semana 2)
space/           encabezado del Space de Hugging Face (fin de semana 2)
Dockerfile       imagen de la API (fin de semana 2)
requirements-api.txt  librerías de la API; cambiar X.Y.Z por la versión de scikit-learn del entrenamiento
labs/            guías de los laboratorios, una carpeta por fin de semana (FDS1, FDS2, FDS3)
params.yaml      parámetros del pipeline
dvc.yaml         definición del pipeline (se crea en el laboratorio 3)
```

## Entregas
Cada hito se entrega con una rama `entrega/eN` y un Pull Request hacia `master`. Nadie hace commit directo en `master` ni en `entrega/*`: todo entra por ramas de trabajo (`feat/`, `fix/`, `exp/`, `docs/`) y PR aprobados. Convención de ramas y paso a paso: [docs/entregas.md](docs/entregas.md).

## Laboratorios del fin de semana 1
1. [Entorno de trabajo](labs/FDS1/01-entorno.md)
2. [Versionar el dataset con DVC](labs/FDS1/02-dvc.md)
3. [Pipeline reproducible](labs/FDS1/03-pipeline.md)
4. [MLflow en el pipeline](labs/FDS1/04-mlflow.md)
