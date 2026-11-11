# Laboratorio 4 · Kubernetes con kind (opcional)

Sábado del fin de semana 3 · 40 min · por equipos · opcional · RA3

## Objetivo
Correr tres copias de la API del equipo en un clúster de Kubernetes dentro de Docker Desktop, llegar a ella desde el navegador y ver que Kubernetes reemplaza solo una copia que se borra.

Todo es gratis y no pide cuenta. Necesitan Docker Desktop abierto y la imagen pública que publica su CD.

## Pasos

### 1. Crear el clúster
Instalen **kind** y **kubectl**:

| Sistema | Comandos |
|---|---|
| Windows | `winget install Kubernetes.kind` y `winget install Kubernetes.kubectl`. Cierren y abran la terminal. |
| macOS | `brew install kind kubectl` |
| Linux | [kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation) y [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/) |

Docker Desktop trae su propio `kubectl`; si `kubectl version --client` responde, no hace falta instalarlo.

```bash
kind create cluster
kubectl get nodes
```
El nodo debe decir `Ready`. La primera vez tarda unos minutos.

### 2. Desplegar la API
Copien [labs/FDS3/k8s.yaml](k8s.yaml) a la raíz del repositorio como `k8s.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: api
          image: ghcr.io/<usuario>/<repo>:latest
          ports:
            - containerPort: 8000
---
apiVersion: v1
kind: Service
metadata:
  name: api
spec:
  selector:
    app: api
  ports:
    - port: 8000
      targetPort: 8000
```
Cambien `<usuario>/<repo>` por los de GitHub, **en minúsculas**: es la misma imagen del CD. El Deployment pide tres copias; el Service les da una dirección fija.

```bash
kubectl apply -f k8s.yaml
kubectl get pods
```
Deben aparecer tres pods en `Running`. Si dicen `ContainerCreating`, esperen y repitan `kubectl get pods`.

### 3. Llegar a la API
El clúster tiene su propia red. Este comando abre una puerta desde el portátil:
```bash
kubectl port-forward service/api 8000:8000
```
Dejen esa terminal abierta y abran http://localhost:8000/docs. Prueben `/predict`. Si `docker compose` sigue corriendo, deténganlo antes: también usa el puerto 8000.

### 4. Probar que se repara solo
En otra terminal:
```bash
kubectl get pods
kubectl delete pod <nombre-de-un-pod>
kubectl get pods
```
Ya hay un pod nuevo con otro nombre: se pidieron tres, y Kubernetes vuelve a crear el que falta.

Al terminar, borren el clúster para liberar memoria:
```bash
kind delete cluster
```

## Listo cuando
- [ ] `kubectl get pods` muestra tres pods en `Running`.
- [ ] `/docs` responde a través de `port-forward`.
- [ ] Al borrar un pod, aparece otro solo.

## Errores frecuentes
- **`Cannot connect to the Docker daemon`** al crear el clúster: Docker Desktop no está abierto.
- **`ImagePullBackOff` o `ErrImagePull`**: la imagen sigue privada, el nombre tiene mayúsculas o está mal escrito. Revisen el paso 5 del [laboratorio de CD](../FDS2/04-cd.md).
- **`CrashLoopBackOff`**: la API se cae al arrancar. `kubectl logs <nombre-de-un-pod>` muestra el error; casi siempre es el modelo o una librería que falta en `requirements-api.txt`.
- **`port is already allocated` o `address already in use`**: otro programa usa el puerto 8000. Usen `kubectl port-forward service/api 8001:8000` y abran `localhost:8001`.
- **`kind` o `kubectl` no se reconoce** en Windows: cierren y abran la terminal después de `winget`.
