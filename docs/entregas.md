# Cómo se entregan los hitos

Cada hito (E1, E2…) se entrega con una **rama de entrega** y un **Pull Request** hacia `master`. El docente lo revisa en la mesa del equipo, comenta en el PR y lo aprueba y une cuando el hito está logrado.

## Reglas

- `master` solo tiene lo que el docente ya aprobó.
- **Nadie hace commit directo en `master` ni en una rama `entrega/`.** Todo el trabajo va en ramas de trabajo que entran por Pull Request.
- `master` y `entrega/*` están protegidas en GitHub (se configura en el [laboratorio 1](../labs/FDS1/01-entorno.md)): cualquier push directo se rechaza y cada PR necesita la aprobación de otra persona.
- Los PR de trabajo los aprueba **otro integrante del equipo**. Los PR de entrega hacia `master` los aprueba y une **solo el docente**.

## Convención de nombres de ramas

Formato: `<tipo>/<descripcion>`

- Todo en minúsculas, palabras separadas por guiones.
- Sin espacios, tildes ni ñ.
- Máximo 40 caracteres.
- La descripción dice qué hace la rama, no quién la hizo.

| Tipo | Para qué | Sale de | Vuelve a | Ejemplo |
|---|---|---|---|---|
| `entrega/` | Una por hito; es la que revisa el docente | `master` | `master` (aprueba y une el docente) | `entrega/e1` |
| `feat/` | Algo nuevo: una etapa, un script, una función | la rama de entrega | la rama de entrega | `feat/pipeline-tres-etapas` |
| `fix/` | Corregir algo que falla | la rama de entrega | la rama de entrega | `fix/target-params` |
| `exp/` | Probar un experimento | la rama de entrega | la rama de entrega | `exp/max-depth-10` |
| `docs/` | README u otra documentación | la rama de entrega | la rama de entrega | `docs/readme-reproducir` |

Nombres que **no** siguen la convención: `Entrega1`, `rama-juan`, `prueba`, `feat/Nueva Etapa`, `fix/corrección`, `main`.

Ramas de trabajo del E1 (una por laboratorio):

| Laboratorio | Rama |
|---|---|
| 1 · Entorno | `feat/inicializa-dvc` |
| 2 · DVC | `feat/versiona-dataset` |
| 3 · Pipeline | `feat/pipeline-tres-etapas` |
| 4 · MLflow | `feat/registro-mlflow` |

## Ciclo de una rama de trabajo

```bash
git switch entrega/e1
git pull
git switch -c feat/<descripcion>
# ... cambios y commits ...
git push -u origin feat/<descripcion>
```
En GitHub: **Pull requests › New pull request**, con `base: entrega/e1` ← `compare: feat/<descripcion>`. Borren la plantilla de entrega y escriban en una o dos líneas qué cambia. Otro integrante aprueba (*Files changed › Review changes › Approve*), hace el merge y borra la rama. Después, todos: `git switch entrega/e1` y `git pull`.

## Paso a paso de una entrega

1. La rama `entrega/eN` se crea desde `master` actualizado. En el E1 se crea en el laboratorio 1; para las siguientes:
   ```bash
   git switch master
   git pull
   git switch -c entrega/e2
   git push -u origin entrega/e2
   ```
2. Todo el trabajo entra a la rama de entrega por ramas de trabajo y PR aprobados.
3. Cuando el checklist esté completo, en GitHub: **Pull requests › New pull request**, con `base: master` ← `compare: entrega/eN`.
4. Título: `Entrega EN · <nombre del equipo>`. Dejen la plantilla: marquen el checklist y **arrastren las capturas** al cuadro de texto.
5. **Create pull request.** Nadie del equipo lo aprueba ni lo une.

## Después de la revisión

- **Logrado:** el docente aprueba y hace el merge. La siguiente entrega sale de `master` actualizado.
- **Falta algo:** el PR queda abierto con los pendientes en un comentario. Los completan con nuevas ramas de trabajo hacia la misma rama de entrega: el PR hacia `master` se actualiza solo. Cuando terminen, avisen con un comentario en el PR. Cuenta la mejor versión, sin perder puntos.
- Si el E1 queda pendiente, se completa antes de crear `entrega/e2`.

## Checklists mínimos

### E1 · Entornos y herramientas base
- [ ] Cada integrante clona el repositorio y lo ejecuta
- [ ] Dataset versionado con DVC y remote configurado
- [ ] `dvc repro` ejecuta las 3 etapas
- [ ] Al menos 3 runs en MLflow y un modelo registrado
- [ ] `master` y `entrega/*` protegidas; cada laboratorio entró por su rama `feat/` con PR aprobado por otro integrante

### E2 · Pipeline con MLflow y DVC
- [ ] `dvc.yaml` con las etapas prepare, train y evaluate
- [ ] Parámetros en `params.yaml` y métricas registradas en MLflow
- [ ] Dos versiones del dataset y forma de volver a la anterior
- [ ] README que explica cómo reproducir todo en 3 comandos
- [ ] Ramas de trabajo con la convención, unidas a `entrega/e2` por PR aprobados
- [ ] Demo de 5 minutos al grupo

### E3 · Modelo en contenedor
- [ ] `api/app.py` con `/health` y `/predict`, y la entrada validada con Pydantic
- [ ] `Dockerfile` y `requirements-api.txt`
- [ ] El contenedor levanta la API y `/predict` responde con una fila real del dataset
- [ ] README que explica cómo construir, correr y probar
- [ ] Ramas de trabajo con la convención, unidas a `entrega/e3` por PR aprobados

### E4 · Pipeline CI/CD
- [ ] Pruebas en `tests/` y workflow de CI que corre en cada PR
- [ ] Las reglas de `master` y `entrega/*` exigen que el CI pase
- [ ] El entrenamiento registra el modelo en el MLflow de DagsHub
- [ ] Un merge publica la imagen en GitHub, sin pasos manuales, y otro integrante la corre en Docker Desktop
- [ ] Los tokens están en GitHub Secrets y en ningún archivo del repositorio
- [ ] Ramas de trabajo con la convención, unidas a `entrega/e4` por PR aprobados
