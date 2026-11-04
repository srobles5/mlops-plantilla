# Laboratorio 2 · Versionar el dataset con DVC

Sábado del fin de semana 1 · 35 min · por equipos · hito E1

## Objetivo
Versionar el dataset del equipo con DVC, guardarlo en un remote y poder volver a cualquier versión.

## Pasos

### 0. Rama de trabajo
```bash
git switch entrega/e1
git pull
git switch -c feat/versiona-dataset
```

### 1. Configurar un remote
Para hoy basta una carpeta fuera del repositorio:
```bash
dvc remote add -d local ../dvc-storage
git add .dvc/config
git commit -m "Configura remote de DVC"
```

### 2. Versión 1 del dataset
```bash
dvc add data/raw/dataset.csv
git add data/raw/dataset.csv.dvc data/raw/.gitignore
git commit -m "Dataset v1"
dvc push
```
Abran `data/raw/dataset.csv.dvc` y miren qué contiene.

### 3. Versión 2 del dataset
Hagan un cambio real (quitar filas o columnas). Por ejemplo, quedarse con el 90 % de las filas:
```bash
python -c "import pandas as pd; df = pd.read_csv('data/raw/dataset.csv'); df.sample(frac=0.9, random_state=1).to_csv('data/raw/dataset.csv', index=False)"
dvc add data/raw/dataset.csv
git commit -am "Dataset v2"
dvc push
```

### 4. Viajar entre versiones
```bash
# volver a la versión 1
git checkout HEAD~1 -- data/raw/dataset.csv.dvc
dvc checkout
# volver a la versión 2
git checkout HEAD -- data/raw/dataset.csv.dvc
dvc checkout
```
Comprueben el número de filas en cada paso:
```bash
python -c "import pandas as pd; print(len(pd.read_csv('data/raw/dataset.csv')))"
```

### 5. Prueba final
Borren `data/raw/dataset.csv` y recupérenlo:
```bash
dvc pull
```

### 6. Pull Request hacia entrega/e1
```bash
git push -u origin feat/versiona-dataset
```
En GitHub: **Pull requests › New pull request**, con `base: entrega/e1` ← `compare: feat/versiona-dataset`. Borren la plantilla de entrega y escriban qué cambia. Otro integrante aprueba (*Files changed › Review changes › Approve*), hace el merge y borra la rama. Después, todos: `git switch entrega/e1` y `git pull`.

## Listo cuando
- [ ] Hay dos commits con versiones distintas de `dataset.csv.dvc`.
- [ ] `dvc pull` recupera el archivo borrado.
- [ ] El PR de `feat/versiona-dataset` está aprobado y unido a `entrega/e1`.

## Opcional: compartir los datos dentro del equipo
El remote en carpeta local vive en una sola máquina. En el fin de semana 2 el remote pasa a **DagsHub** (con su plan gratuito), que también da el servidor de MLflow compartido. Si quieren adelantarlo:
1. Entrar a dagshub.com con la cuenta de GitHub y elegir **Create › New Repository › Connect a repository** con el repositorio del equipo.
2. En DagsHub, botón **Remote › Data › DVC**: ahí aparecen los comandos exactos para su repositorio.
3. Al pegar los comandos con el usuario y el token, usen siempre `--local`: así las credenciales quedan en `.dvc/config.local`, que Git no sube.
4. `dvc push` y comprobar que los datos aparecen en DagsHub.

## Errores frecuentes
- **`output 'data/raw/dataset.csv' is already tracked by SCM`**: el CSV se subió a Git por error. Solución: `git rm --cached data/raw/dataset.csv`, `git commit -m "Saca el CSV de Git"` y repetir `dvc add`.
- **`dvc push` falla con una ruta**: evitar espacios y tildes en la ruta del remote.
- **`git commit -am` no incluye el `.dvc`**: el archivo todavía no estaba en Git; usar `git add` primero.
