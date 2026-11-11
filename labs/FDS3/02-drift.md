# Laboratorio 2 · Informe de drift con Evidently

Viernes del fin de semana 3 · 40 min · por equipos · hito E5

## Objetivo
Guardar lo que recibe la API, simular un cambio en los datos y obtener un informe de Evidently que diga qué columnas cambiaron. Con ese informe, el equipo decide si reentrena.

## Pasos

### 0. Rama de trabajo
```bash
git switch entrega/e5
git pull
git switch -c feat/drift
```
Necesitan `data/raw/dataset.csv` en el portátil. Si no está, corran `dvc pull`.

### 1. Guardar lo que recibe la API
En `api/app.py` hay tres cambios. El archivo completo está en [la plantilla](https://github.com/srobles5/mlops-plantilla/blob/master/api/app.py).

**a.** Arriba, junto a los otros imports:
```python
import csv
```

**b.** Antes de la línea `modelo = joblib.load(...)`, la carpeta donde se guardan las entradas:
```python
LOGS = Path(os.getenv("LOGS_DIR", "logs"))
```
Y antes de `class Cliente`, la función que agrega una fila por petición:
```python
def guardar_entrada(datos):
    """Agrega una fila a logs/entradas.csv con lo que recibió la API."""
    LOGS.mkdir(exist_ok=True)
    archivo = LOGS / "entradas.csv"
    nuevo = not archivo.exists()
    with open(archivo, "a", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=list(datos))
        if nuevo:
            escritor.writeheader()
        escritor.writerow(datos)
```

**c.** La primera línea dentro de `predict`:
```python
    guardar_entrada(cliente.model_dump())
```

En `tests/test_api.py`, debajo de `monkeypatch.setenv("MODEL_DIR", ...)`, agreguen esta línea para que las pruebas no escriban en su `logs/`:
```python
    monkeypatch.setenv("LOGS_DIR", str(tmp_path / "logs"))
```

En `docker-compose.yml`, el servicio `api` necesita un volumen para que el archivo quede en el repositorio y no solo dentro del contenedor:
```yaml
  api:
    build: .
    ports: ["8000:8000"]
    volumes:
      - ./logs:/app/logs
```

Y en `.gitignore`, para no subir las entradas ni los informes:
```
logs/
reports/
```

Levanten todo de nuevo con `docker compose up --build` y generen tráfico, como en el paso 3 del [laboratorio 1](01-monitoreo.md): 30 casos desde `/docs`, o
```bash
python src/generar_trafico.py http://localhost:8000 30
```

### 2. Provocar un cambio
En clase no hay semanas de datos reales, así que se simula el cambio que dejaría una campaña nueva. Copien [src/simular_drift.py](https://github.com/srobles5/mlops-plantilla/blob/master/src/simular_drift.py) de la plantilla. Arriba tiene:
```python
CAMBIOS = {
    "tenure": 0.3,
    "Contract": "Month-to-month",
}
```
Cámbienlo por columnas de su dataset. En una columna numérica, el número la multiplica: `0.3` la deja en un 30 % y `1.5` la sube un 50 %. En una columna de texto, el valor reemplaza a esa categoría en el 60 % de las filas. Después:
```bash
python src/simular_drift.py
```
Escribe `logs/actual.csv` con 500 filas del dataset, con esas columnas cambiadas.

### 3. Correr el informe
Agreguen Evidently a `requirements.txt` con esta versión exacta e instálenlo:
```
evidently==0.7.23
```
```bash
pip install -r requirements.txt
```
Copien [src/drift.py](https://github.com/srobles5/mlops-plantilla/blob/master/src/drift.py) de la plantilla y córranlo:
```bash
python src/drift.py
```
Compara el dataset del entrenamiento con `logs/actual.csv`, escribe `reports/drift.html` y muestra un resumen:
```
Columnas con drift: 2 de 19 (11%): tenure, Contract
El conjunto no tiene drift: cambiaron menos de la mitad de las columnas.
Informe: reports/drift.html
```
Abran `reports/drift.html` en el navegador.

### 4. Leer el informe
1. ¿Se marcó drift en el conjunto? Evidently lo marca cuando cambió la mitad o más de las columnas.
2. ¿Cuáles columnas cambiaron? ¿Son las que ustedes tocaron?
3. Abran una columna en el informe y miren cómo se movió la distribución.

Tomen una captura del informe para el README.

### 5. Decidir
En el `README.md`, en una sección «Drift», escriban:
1. Qué columnas cambiaron, con la captura.
2. Si reentrenarían o seguirían con el modelo actual.
3. Por qué, en tres frases que se apoyen en el informe.

### 6. Guardar y Pull Request hacia entrega/e5
```bash
git add api tests docker-compose.yml .gitignore requirements.txt src/simular_drift.py src/drift.py README.md
git commit -m "Informe de drift con Evidently"
git push -u origin feat/drift
```
PR con `base: entrega/e5` ← `compare: feat/drift`. Otro integrante aprueba y hace el merge.

## Listo cuando
- [ ] `logs/entradas.csv` tiene una fila por cada petición a `/predict`.
- [ ] `python src/drift.py` genera `reports/drift.html`.
- [ ] El README tiene la captura del informe y la decisión escrita.
- [ ] `logs/` y `reports/` están en `.gitignore`.

## Cómo elige Evidently la prueba
Con menos de 1.000 filas de referencia usa Kolmogorov-Smirnov para números y chi cuadrado para categorías; con más, como el dataset de churn, usa distancias: Wasserstein para números y Jensen-Shannon para categorías, con umbral 0,1. El informe dice cuál usó en cada columna.

## Errores frecuentes
- **`ImportError: cannot import name 'infer_dtype_from_object'`**: hay pandas 3 instalado y Evidently 0.7 no funciona con él. `requirements.txt` debe decir `pandas>=2.0,<3`; corran `pip install -r requirements.txt` de nuevo.
- **`ModuleNotFoundError: evidently`**: falta `pip install -r requirements.txt` en el entorno activo.
- **`La columna ... no está en el dataset`**: un nombre de `CAMBIOS` no coincide con su dataset; respeten mayúsculas.
- **`logs/entradas.csv` no aparece**: falta el volumen en `docker-compose.yml`, o no reconstruyeron con `--build`.
- **Columnas marcadas que no tocaron**: con pocas filas, como las 30 de `entradas.csv`, aparecen cambios por azar. Es un buen punto para la decisión escrita.
- **`TotalCharges` u otra columna sale como texto**: el CSV tiene celdas vacías en una columna numérica. Evidently la trata como texto; no es un error del laboratorio.
