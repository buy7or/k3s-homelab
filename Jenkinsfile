pipeline {
  agent {
    kubernetes {
      defaultContainer 'kubectl'
      yaml '''
apiVersion: v1
kind: Pod
spec:
  serviceAccountName: jenkins
  containers:
    - name: kubectl
      image: alpine/k8s:1.34.1
      command:
        - cat
      tty: true
'''
    }
  }

  stages {
    stage('Comprobar archivos') {
      steps {
        sh '''
          echo "Archivos del repo:"
          ls -la

          test -f app.py
          test -f web-demo.yaml
        '''
      }
    }

    stage('Actualizar ConfigMap') {
      steps {
        sh '''
          kubectl create configmap web-demo-app \
            --from-file=app.py \
            -n default \
            --dry-run=client \
            -o yaml | kubectl apply -n default -f -
        '''
      }
    }

    stage('Aplicar Kubernetes YAML') {
      steps {
        sh '''
          kubectl apply -n default -f web-demo.yaml
        '''
      }
    }

    stage('Reiniciar web-demo') {
      steps {
        sh '''
          kubectl rollout restart deployment web-demo -n default
          kubectl rollout status deployment web-demo -n default
        '''
      }
    }

    stage('Estado final') {
      steps {
        sh '''
          kubectl get pods -n default -o wide
          kubectl get svc -n default
          kubectl get ingress -n default
          kubectl get pvc -n default
        '''
      }
    }
  }
}