# Laboratorio 1 · DagsHub: remote de DVC y MLflow compartidos

Viernes del fin de semana 2 · 60 min · por equipos · hito E3

## Objetivo
Que los datos, el modelo y los experimentos dejen de vivir en un solo portátil. Mañana GitHub Actions va a traer el modelo desde DagsHub para desplegarlo.

## Pasos

### 0. Ramas
Si `entrega/e3` todavía no existe, una persona la crea desde `master` actualizado:
```bash
git switch master
git pull
git switch -c entrega/e3
git push -u origin entrega/e3
```
Si el PR del E2 sigue abierto, salgan de `entrega/e2` en lugar de `master`.

Después, la rama de trabajo:
```bash
git switch entrega/e3
git pull
git switch -c feat/conecta-dagshub
```

### 1. Conectar el repositorio (una persona)
1. Entren a https://dagshub.com con su cuenta de GitHub y usen el plan gratuito.
2. **Create › New Repository › Connect a repository › GitHub**, y elijan el repositorio del equipo. Déjenlo **público**: en privado, el plan gratuito solo permite 2 colaboradores y 100 experimentos. Quedan a la vista el dataset y el modelo, así que un equipo con datos propios debe avisar al docente antes de conectarlo.
3. En el repositorio de DagsHub: **Settings › Collaborators**, y agreguen a los demás con permiso de escritura.

### 2. Crear el token (cada integrante)
En DagsHub: foto de perfil **› Your Settings › Tokens**. Copien el token y no lo pongan en ningún archivo del repositorio.

### 3. Cambiar el remote de DVC
Una persona agrega el remote, con el usuario y el nombre del repositorio tal como aparecen en la URL de DagsHub:
```bash
dvc remote add -d dagshub https://dagshub.com/<usuario>/<repo>.dvc
git add .dvc/config
git commit -m "Usa DagsHub como remote de DVC"
```
Cada integrante configura sus credenciales. `--local` las guarda en `.dvc/config.local`, que Git ignora:
```bash
dvc remote modify dagshub --local auth basic
dvc remote modify dagshub --local user <usuario>
dvc remote modify dagshub --local password <token>
```
Quien tiene los datos los sube:
```bash
dvc push
```

### 4. Registrar los experimentos en DagsHub
En `src/train.py`, agreguen `import os` arriba y cambien la línea de `set_tracking_uri`:
```python
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db"))
```
Si la variable no existe, todo sigue funcionando con SQLite como antes.

Definan las variables en la terminal. Duran hasta que la cierren.

Git Bash, macOS o Linux:
```bash
export MLFLOW_TRACKING_URI=https://dagshub.com/<usuario>/<repo>.mlflow
export MLFLOW_TRACKING_USERNAME=<usuario>
export MLFLOW_TRACKING_PASSWORD=<token>
```
PowerShell:
```powershell
$env:MLFLOW_TRACKING_URI = "https://dagshub.com/<usuario>/<repo>.mlflow"
$env:MLFLOW_TRACKING_USERNAME = "<usuario>"
$env:MLFLOW_TRACKING_PASSWORD = "<token>"
$env:PYTHONUTF8 = "1"
```

Corran un experimento y súbanlo:
```bash
dvc repro
dvc push
```
Búsquenlo en DagsHub, en la pestaña **Experiments** del repositorio.

### 5. Guardar y Pull Request hacia entrega/e3
```bash
git add src/train.py dvc.lock metrics.json
git commit -m "Registra los experimentos en DagsHub"
git push -u origin feat/conecta-dagshub
```
En GitHub: **Pull requests › New pull request**, con `base: entrega/e3` ← `compare: feat/conecta-dagshub`. Borren la plantilla de entrega y escriban qué cambia. Otro integrante aprueba, hace el merge y borra la rama.

### 6. Probar desde otro portátil
Otra persona actualiza la rama, configura sus credenciales (paso 3) y trae los datos:
```bash
git switch entrega/e3
git pull
dvc pull
```

## Listo cuando
- [ ] `dvc pull` funciona en otro portátil.
- [ ] El run aparece en DagsHub.
- [ ] Ningún token quedó en un archivo que Git sigue.
- [ ] El PR de `feat/conecta-dagshub` está unido a `entrega/e3`.

## Errores frecuentes
- **`401 Unauthorized` o `Bad credentials`**: usuario o token mal escritos. Repitan los comandos con `--local`, o vuelvan a definir las variables si abrieron otra terminal.
- **`403 Forbidden`**: la persona no es colaboradora del repositorio de DagsHub con permiso de escritura.
- **`SSLCertVerificationError: self-signed certificate in certificate chain`** al hacer `dvc push` o `dvc pull`: un antivirus, proxy o VPN de la red intercepta HTTPS y DVC no confía en su certificado. Desactiven la verificación solo en su portátil (`--local`, no se sube a Git) y repitan:
  ```bash
  dvc remote modify dagshub --local ssl_verify false
  ```
  Úsenlo solo si el error aparece y en una red que conozcan. Para quitarlo después: `dvc remote modify dagshub --local --unset ssl_verify`.
- **`dvc pull` dice que faltan archivos**: alguien no hizo `dvc push` después de entrenar.
- **El run sigue apareciendo solo en local**: la terminal no tiene `MLFLOW_TRACKING_URI`. Compruébenlo con `echo $MLFLOW_TRACKING_URI` o, en PowerShell, `echo $env:MLFLOW_TRACKING_URI`.
- **`dvc repro` no crea un run nuevo**: no cambió nada. Fuercen el entrenamiento con `dvc repro --force`.
- **`API request to endpoint /api/2.0/mlflow/logged-models failed with error code 404`**: el servidor no acepta esa llamada de MLflow 3. Instalen la versión anterior con `pip install "mlflow<3" "sqlalchemy<2.0.45"`, pónganla igual en `requirements.txt` y en `src/train.py` cambien `name="model"` por `artifact_path="model"`.
- **`UnicodeEncodeError` con `charmap`** al terminar el run, en Windows: MLflow imprime un emoji que la terminal no sabe mostrar. Definan `$env:PYTHONUTF8 = "1"` y repitan.

Si no alcanzan hoy, terminen antes del sábado a las 13:00: el CD lo necesita.
