# Laboratorio 1 · El panel de la API con Prometheus y Grafana

Viernes del fin de semana 3 · 40 min · por equipos · hito E5

## Objetivo
Que la API del equipo muestre sus números en `/metrics`, que Prometheus los guarde cada 20 segundos y que Grafana los dibuje en un panel con cuatro gráficos.

## Antes de clase
La primera descarga de las imágenes toma varios minutos. Con Docker Desktop abierto, corran en casa:
```bash
docker pull prom/prometheus
docker pull grafana/grafana
```

## Pasos

### 0. Rama de trabajo
```bash
git switch entrega/e5
git pull
git switch -c feat/metricas
dvc pull
```
Si `entrega/e5` no existe, créenla desde `master` como en los fines de semana anteriores ([docs/entregas.md](../../docs/entregas.md)). `dvc pull` trae `models/model.pkl`, que la imagen necesita.

### 1. Métricas en la API
Agreguen la librería al final de `requirements-api.txt` e instálenla:
```
prometheus-fastapi-instrumentator>=7.0
```
```bash
pip install -r requirements-api.txt
```

En `api/app.py` hay tres cambios. El archivo completo está en [la plantilla](https://github.com/srobles5/mlops-plantilla/blob/master/api/app.py); trae además `guardar_entrada`, que se agrega en el [laboratorio de drift](02-drift.md).

**a. Las métricas estándar.** Dos líneas: el import arriba y la otra justo después de crear `app`. Agregan la ruta `/metrics` con tráfico, errores y tiempo de respuesta.
```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

**b. El contador de predicciones por clase.** Después de la línea anterior:
```python
from prometheus_client import REGISTRY, Counter

try:
    PREDICCIONES = Counter("predicciones_total", "Predicciones por clase", ["clase"])
except ValueError:  # ya existe: pasa cuando las pruebas vuelven a cargar la API
    PREDICCIONES = REGISTRY._names_to_collectors["predicciones_total"]
```
El `try` no es opcional: las pruebas de `tests/test_api.py` cargan la API una vez por prueba, y sin él el contador se registra dos veces y el CI queda en rojo con `Duplicated timeseries`.

**c. Contar en `predict`.** Guarden la predicción en una variable y súmenle 1 al contador antes del `return`:
```python
@app.post("/predict")
def predict(cliente: Cliente):
    X = pd.get_dummies(pd.DataFrame([cliente.model_dump()]), dtype=int)
    X = X.reindex(columns=modelo.feature_names_in_, fill_value=0)
    resultado = str(modelo.predict(X)[0])
    PREDICCIONES.labels(clase=resultado).inc()
    return {"prediccion": resultado}
```

Comprueben antes de seguir:
```bash
uvicorn api.app:app --reload
pytest
```
http://localhost:8000/metrics debe mostrar texto, y `pytest` debe pasar. Detengan el servidor con `Ctrl+C`.

### 2. Levantar los tres contenedores
Creen dos archivos en la raíz del repositorio. Los dos también están en la plantilla.

`prometheus.yml` le dice a Prometheus a quién preguntar y cada cuánto:
```yaml
global:
  scrape_interval: 20s

scrape_configs:
  - job_name: api
    static_configs:
      - targets: ["api:8000"]
```

`docker-compose.yml` define los tres contenedores juntos:
```yaml
services:
  api:
    build: .
    ports: ["8000:8000"]
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports: ["9090:9090"]
  grafana:
    image: grafana/grafana
    ports: ["3000:3000"]
```
`api` es el nombre del servicio: dentro de la red de Docker, Prometheus llega a la API por ese nombre. El `docker-compose.yml` de la plantilla tiene además un volumen para `logs/`, que se agrega en el [laboratorio de drift](02-drift.md).

Con Docker Desktop abierto, en la terminal y desde la raíz del repositorio:
```bash
docker compose up --build
```
En Docker Desktop, en **Containers**, deben aparecer los tres en verde. Para detenerlos, `Ctrl+C` en la terminal o el botón de detener en **Containers**.

### 3. Generar tráfico
Sin peticiones los paneles salen vacíos. Hay dos formas; basta con una.

**Con clics.** Abran http://localhost:8000/docs, entren a **POST /predict › Try it out**, cambien los valores y pulsen **Execute**. Repítanlo unas 20 veces con valores distintos. Después, una vez más con texto donde va un número, por ejemplo `"tenure": "muchos"`: debe responder error 422. Ese error también se cuenta en el panel.

**Con el script.** En otra terminal, con los contenedores corriendo:
```bash
python src/generar_trafico.py
```
Envía 20 peticiones con valores distintos y al final un dato inválido, y muestra cada respuesta. El script está en [la plantilla](https://github.com/srobles5/mlops-plantilla/blob/master/src/generar_trafico.py) y solo usa la librería estándar de Python. Antes de correrlo, cambien `CASO` por las columnas de su `Cliente`, con valores reales del dataset. Para otra dirección u otra cantidad: `python src/generar_trafico.py http://localhost:8001 50`.

El error 422 es del cliente (`4xx`), no del servidor: el panel de errores del paso 6 cuenta los `5xx` y debe quedar en 0.

### 4. Comprobar Prometheus
1. Abran http://localhost:9090.
2. En el menú, **Status › Targets**: el objetivo `api` debe decir **UP**.
3. En **Graph**, escriban `http_requests_total` y pulsen **Execute**. Si aparece una tabla con filas, Prometheus ya tiene datos.

Si dice **DOWN**, revisen el nombre y el puerto en `prometheus.yml`: debe ser `api:8000`.

### 5. Conectar Grafana
1. Abran http://localhost:3000. Usuario y clave: `admin` y `admin`; pueden omitir el cambio de clave.
2. **Connections › Data sources › Add data source › Prometheus**.
3. En URL escriban `http://prometheus:9090`. Es `prometheus`, no `localhost`: dentro del contenedor de Grafana, `localhost` es el propio Grafana.
4. Abajo: **Save & test**.

Los nombres de los menús pueden variar un poco según la versión; el buscador de Grafana los encuentra.

### 6. El panel de la API
1. **Dashboards › New › New dashboard › Add visualization**.
2. Elijan la fuente **Prometheus** y peguen la primera consulta de la tabla. Si el editor está en modo **Builder**, cámbienlo a **Code**.
3. Pongan título al panel y pulsen **Apply**.
4. Repitan con las otras tres y guarden el panel con el nombre del equipo.

| Panel | Consulta |
|---|---|
| Tráfico | `sum(rate(http_requests_total[2m]))` |
| Errores | `sum(rate(http_requests_total{status="5xx"}[2m]))` |
| Latencia p95 | `histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[2m])) by (le))` |
| Predicciones por clase | `sum(rate(predicciones_total[2m])) by (clase)` |

`rate()` convierte un contador que solo sube en peticiones por segundo. `[2m]` es la ventana: los últimos 2 minutos, que con una lectura cada 20 segundos son 6 lecturas.

Si un panel dice **No data**, generen tráfico otra vez (paso 3) y esperen unos 30 segundos: Prometheus lee cada 20.

### 7. Guardar y Pull Request hacia entrega/e5
Tomen una captura del panel con los cuatro gráficos y agréguenla al `README.md`, con cómo levantar los contenedores. Es evidencia del E5.
```bash
git add api requirements-api.txt prometheus.yml docker-compose.yml src/generar_trafico.py README.md
git commit -m "Métricas de la API con Prometheus y Grafana"
git push -u origin feat/metricas
```
PR con `base: entrega/e5` ← `compare: feat/metricas`. Otro integrante aprueba y hace el merge.

## Listo cuando
- [ ] http://localhost:8000/metrics muestra texto y `pytest` pasa.
- [ ] Los tres contenedores corren en Docker Desktop.
- [ ] En Prometheus, el objetivo `api` dice **UP**.
- [ ] El panel de Grafana tiene cuatro gráficos con datos.
- [ ] La captura del panel está en el README.

## Errores frecuentes
- **`Duplicated timeseries in CollectorRegistry`** en `pytest` o en el CI: falta el `try` del paso 1b.
- **`ModuleNotFoundError: prometheus_fastapi_instrumentator`** al construir: falta la librería en `requirements-api.txt`.
- **Un contenedor no arranca**: abran su nombre en **Containers** y miren **Logs**. Lo más común es una sangría mal puesta en un YAML.
- **`port is already allocated`**: el puerto está ocupado. Cambien el número de la izquierda en `ports`, por ejemplo `"3001:3000"`, y abran ese puerto.
- **El objetivo `api` dice DOWN**: el target de `prometheus.yml` no es `api:8000`, o la API no arrancó.
- **Grafana no conecta con Prometheus**: escribieron `localhost:9090` en vez de `http://prometheus:9090`.
- **No data**: aún no hay tráfico o no ha pasado una lectura. Paso 3 y esperar 30 segundos.
- **Codespaces**: los puertos 3000 y 9090 se abren desde la pestaña **Ports**.
