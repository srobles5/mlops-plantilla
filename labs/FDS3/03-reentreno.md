# Laboratorio 3 · Reentrenar con GitHub Actions

Sábado del fin de semana 3 · 45 min · por equipos · hito E5

## Objetivo
Un workflow que, con un botón o cada lunes, trae los datos, reentrena con `dvc repro`, compara la métrica nueva con la del modelo en uso y, solo si es igual o mejor, abre un Pull Request. Al unir ese PR, el CD del fin de semana 2 publica la imagen nueva.

## Antes de empezar
- Los secretos `DAGSHUB_USER` y `DAGSHUB_TOKEN` ya están en GitHub desde el [laboratorio de CD](../FDS2/04-cd.md).
- En el repositorio del equipo: **Settings › Actions › General › Workflow permissions**. Marquen **Allow GitHub Actions to create and approve pull requests** y pulsen **Save**. Sin esto, el último paso del workflow falla.

## Pasos

### 1. Agregar el workflow
Todo se hace en la página de GitHub, sin terminal.
1. Creen la rama `feat/reentreno` desde `entrega/e5`, con el menú de ramas.
2. **Add file › Create new file**. Nombre: `.github/workflows/reentreno.yml`.
3. Peguen el contenido de [labs/FDS3/workflows/reentreno.yml](workflows/reentreno.yml), que está abajo.
4. Cambien `<usuario>/<repo>` en `MLFLOW_TRACKING_URI` por los de su repositorio en DagsHub, igual que en el [laboratorio de DagsHub](../FDS2/01-dagshub.md).
5. **Commit changes...** a la rama `feat/reentreno`.

```yaml
name: Reentreno
on:
  schedule:
    - cron: "0 6 * * 1"   # cada lunes a las 06:00 UTC
  workflow_dispatch:       # y también con un botón
permissions:
  contents: write
  pull-requests: write
jobs:
  reentrenar:
    runs-on: ubuntu-latest
    env:
      # Cambien <usuario>/<repo> por los del repositorio en DagsHub.
      MLFLOW_TRACKING_URI: https://dagshub.com/<usuario>/<repo>.mlflow
      MLFLOW_TRACKING_USERNAME: ${{ secrets.DAGSHUB_USER }}
      MLFLOW_TRACKING_PASSWORD: ${{ secrets.DAGSHUB_TOKEN }}
      METRICA: f1_macro    # la métrica de metrics.json que decide
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - name: Traer datos y modelo
        run: |
          dvc remote modify dagshub --local auth basic
          dvc remote modify dagshub --local user ${{ secrets.DAGSHUB_USER }}
          dvc remote modify dagshub --local password ${{ secrets.DAGSHUB_TOKEN }}
          dvc pull
      - name: Reentrenar
        run: |
          cp metrics.json metrics_antes.json
          dvc repro
      - name: Comparar con el modelo en uso
        id: comparar
        run: |
          python - <<'FIN' >> "$GITHUB_OUTPUT"
          import json, os, sys
          m = os.environ["METRICA"]
          antes = json.load(open("metrics_antes.json"))[m]
          ahora = json.load(open("metrics.json"))[m]
          print(f"{m}: antes {antes}, ahora {ahora}", file=sys.stderr)
          print("mejora=" + ("true" if ahora >= antes else "false"))
          FIN
      - name: Subir el modelo nuevo a DagsHub
        if: steps.comparar.outputs.mejora == 'true'
        run: dvc push
      - name: Abrir el Pull Request
        if: steps.comparar.outputs.mejora == 'true'
        uses: peter-evans/create-pull-request@v7
        with:
          branch: reentreno/automatico
          base: master
          add-paths: |
            dvc.lock
            metrics.json
          commit-message: Reentrena el modelo con los datos actuales
          title: "Reentreno: modelo nuevo igual o mejor que el actual"
          body: |
            El workflow Reentreno entrenó un modelo nuevo y su métrica es igual o mejor que la del modelo en uso.
            Revisen metrics.json y el run en MLflow antes de aprobar. Al unir este PR, el CD publica la imagen.
```

Qué hace cada parte:
- **`on`**: `schedule` lo corre solo cada lunes; `workflow_dispatch` agrega el botón **Run workflow**.
- **Traer datos y modelo**: lo mismo que el CD, pero trae todo con `dvc pull`.
- **Reentrenar**: guarda la métrica actual y corre el pipeline. Si nada cambió, `dvc repro` no hace nada.
- **Comparar**: lee `METRICA` en los dos `metrics.json`. Si su `evaluate.py` usa otro nombre, cámbienlo arriba.
- **Subir y abrir el PR**: solo si la métrica es igual o mejor. Sube el modelo a DagsHub para que el CD lo encuentre y abre un PR hacia `master` con `dvc.lock` y `metrics.json`.

### 2. Pull Request hacia entrega/e5
1. **Compare & pull request** con `base: entrega/e5` ← `compare: feat/reentreno`.
2. Otro integrante aprueba.
3. **Merge pull request**.

Ojo: GitHub solo muestra el botón **Run workflow** cuando el archivo está en la rama por defecto, `master`. Para verlo hoy, abran también el PR de `entrega/e5` hacia `master` y únanlo con la aprobación del docente.

### 3. Correrlo con el botón
1. En el repositorio: **Actions**.
2. A la izquierda, el workflow **Reentreno**.
3. **Run workflow** › **Run workflow**.
4. Esperen el verde y abran el detalle de cada paso. En **Comparar con el modelo en uso** aparece la métrica de antes y la de ahora.

### 4. Leer el resultado
1. ¿Se abrió un PR desde `reentreno/automatico`? Está en **Pull requests**.
2. Si no se abrió, miren el paso **Comparar**: o la métrica bajó, o `dvc repro` no cambió nada.
3. En MLflow (DagsHub), comparen el run nuevo con el anterior.

Con los mismos datos y los mismos parámetros, `dvc repro` no cambia nada y no hay PR. Para ver el ciclo completo, cambien un valor de `train` en `params.yaml`, por ejemplo `n_estimators: 200`, súbanlo a `master` con un PR y corran el workflow otra vez.

### 5. Ciclo completo
1. Si hay PR, revísenlo y únanlo.
2. En **Actions**, esperen a que el CD publique la imagen.
3. Descarguen y corran la imagen nueva en Docker Desktop, como en el [laboratorio de CD](../FDS2/04-cd.md), y comprueben el panel de Grafana.

## Listo cuando
- [ ] El workflow **Reentreno** aparece en **Actions** y termina en verde.
- [ ] Si la métrica es igual o mejor y hubo cambios, se abre un PR solo.
- [ ] Al unir ese PR, el CD publica una imagen nueva.

## Errores frecuentes
- **No aparece el botón Run workflow**: el archivo no está en `master`. Vean el paso 2.
- **`GitHub Actions is not permitted to create or approve pull requests`**: falta marcar la opción de **Antes de empezar**.
- **Falla `dvc pull` o `dvc push`**: los secretos están mal, o falta `dvc push` de quien entrenó por última vez.
- **`KeyError: 'f1_macro'`**: `metrics.json` usa otro nombre. Cámbienlo en `METRICA`.
- **`cp: cannot stat 'metrics.json'`**: `metrics.json` no está en Git. Debe subirse junto con `dvc.lock`, como en el fin de semana 1.
- **El PR automático no corre el CI**: GitHub no dispara workflows con PR abiertos por otro workflow. Ciérrenlo y vuelvan a abrirlo con **Close pull request** y **Reopen pull request**: así el CI corre.
- **El run no aparece en MLflow**: `MLFLOW_TRACKING_URI` sigue con `<usuario>/<repo>`.
