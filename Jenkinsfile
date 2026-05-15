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
      volumeMounts:
        - name: workspace-volume
          mountPath: /home/jenkins/agent

    - name: kaniko
      image: gcr.io/kaniko-project/executor:debug
      command:
        - /busybox/cat
      tty: true
      volumeMounts:
        - name: workspace-volume
          mountPath: /home/jenkins/agent
        - name: docker-config
          mountPath: /kaniko/.docker

  volumes:
    - name: workspace-volume
      emptyDir: {}
    - name: docker-config
      secret:
        secretName: ghcr-secret
        items:
          - key: .dockerconfigjson
            path: config.json
'''
    }
  }

  environment {
    IMAGE_NAME = 'ghcr.io/buy7or/k3s-homelab/web-demo'
    IMAGE_TAG = 'latest'
  }

  stages {
    stage('Comprobar archivos') {
      steps {
        sh '''
          echo "Archivos del repo:"
          ls -la

          test -f app.py
          test -f requirements.txt
          test -f Dockerfile
          test -f web-demo.yaml
        '''
      }
    }

    stage('Build y push imagen Docker') {
      steps {
        container('kaniko') {
          sh '''
            /kaniko/executor \
              --context . \
              --dockerfile Dockerfile \
              --destination ${IMAGE_NAME}:${IMAGE_TAG}
          '''
        }
      }
    }

    stage('Aplicar Kubernetes YAML') {
      steps {
        container('kubectl') {
          sh '''
            kubectl apply -n default -f web-demo.yaml
          '''
        }
      }
    }

    stage('Reiniciar web-demo') {
      steps {
        container('kubectl') {
          sh '''
            kubectl rollout restart deployment web-demo -n default
            kubectl rollout status deployment web-demo -n default
          '''
        }
      }
    }

    stage('Estado final') {
      steps {
        container('kubectl') {
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
}