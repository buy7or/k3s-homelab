# k3s-homelab

Estoy montando un homelab DevOps con 3 mini PCs Lenovo como servidores.

Infraestructura actual:
- 3 nodos Ubuntu Server con IP fija:
  - server1: 192.168.1.101
  - server2: 192.168.1.102
  - server3: 192.168.1.103
- Los 3 tienen SSH.
- Los 3 tienen Tailscale.
- Tengo un cluster k3s en HA:
  - server1 = control-plane + worker
  - server2 = control-plane + worker
  - server3 = control-plane + worker
- Lo gestiono desde mi PC con kubectl y Headlamp.
- Uso Traefik como Ingress Controller, el que viene por defecto con k3s.
- Uso /etc/hosts para dominios internos tipo:
  - web-demo.casa
  - jenkins.casa

App de prueba actual:
- Tengo una app llamada web-demo.
- Es una app Flask en Python.
- Tiene un botón que suma clicks.
- El contador se guarda en Redis.
- Redis está desplegado en Kubernetes.
- Redis tiene PVC llamado redis-data con StorageClass local-path.
- La web se conecta a Redis usando el Service interno:
  - redis:6379
- La web escucha en el contenedor en el puerto 5000.
- El Service web-demo-service expone internamente el puerto 80 y redirige al targetPort 5000.
- El acceso externo va por Ingress:
  - http://web-demo.casa
- Antes usaba app.py como ConfigMap, pero ya lo cambié a imagen Docker propia.

Imagen Docker:
- Repo GitHub: https://github.com/buy7or/k3s-homelab
- Archivos principales:
  - app.py
  - requirements.txt
  - Dockerfile
  - web-demo.yaml
  - Jenkinsfile
- La imagen se publica en GitHub Container Registry:
  - ghcr.io/buy7or/k3s-homelab/web-demo:latest
- Como la imagen es privada, creé un imagePullSecret:
  - ghcr-secret
- El Deployment web-demo usa:
  - imagePullSecrets:
      - name: ghcr-secret
  - image: ghcr.io/buy7or/k3s-homelab/web-demo:latest
  - imagePullPolicy: Always

Jenkins:
- Jenkins está instalado en Kubernetes con Helm, en namespace jenkins.
- URL por Ingress:
  - http://jenkins.casa
- Jenkins está desplegado como StatefulSet:
  - jenkins-0
- Tiene PVC propio:
  - namespace: jenkins
  - PVC: jenkins
  - StorageClass: local-path
- Jenkins usa agentes temporales en Kubernetes para ejecutar pipelines.
- El Jenkinsfile usa un pod agente con:
  - contenedor kubectl
  - contenedor kaniko
- Kaniko construye la imagen Docker dentro de Kubernetes y la sube a GHCR.
- Creé también ghcr-secret en namespace jenkins para que Kaniko pueda subir a GHCR.
- Jenkins tiene RBAC para desplegar en namespace default:
  - Role jenkins-deployer
  - RoleBinding al ServiceAccount jenkins del namespace jenkins
- Jenkins hace polling del repo GitHub cada X minutos.
- Flujo actual:
  1. Hago git push a GitHub.
  2. Jenkins detecta cambios.
  3. Jenkins clona el repo.
  4. Kaniko construye la imagen Docker.
  5. Kaniko sube la imagen a GHCR.
  6. Jenkins aplica web-demo.yaml.
  7. Jenkins reinicia el Deployment web-demo.
  8. Kubernetes descarga la nueva imagen y actualiza la web.

Cosas importantes aprendidas:
- NodePort abre un puerto en todos los nodos.
- Ingress con Traefik permite usar dominios bonitos.
- Service ClusterIP da nombres internos como redis:6379.
- Deployment sirve para apps stateless o reemplazables.
- StatefulSet sirve para apps con identidad/estado como Jenkins.
- PVC con local-path NO es almacenamiento HA real; vive en un nodo concreto.
- Si se apaga server1 y Jenkins vive en server1, Jenkins puede quedar en Error. Borrar el pod jenkins-0 lo recrea sin perder datos porque los datos están en el PVC.
- Control-plane HA no significa almacenamiento HA.
- Argo CD todavía no lo he instalado. De momento Jenkins despliega directamente con kubectl apply. Más adelante podría usar Argo CD para GitOps, pero ahora estoy haciendo pruebas manuales y no quiero que Argo me revierta cambios.