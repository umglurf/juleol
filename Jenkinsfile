pipeline {
  agent any

  stages {

    stage("Build") {
      steps {
        script {
          docker.withTool('docker') {
            docker.withServer("tcp://${env.DOCKER_HOST}:2375") {
              docker.withRegistry("https://${env.DOCKER_REGISTRY}", 'docker-repo') {
                sh "docker build -t ${env.DOCKER_REGISTRY}/juleol:${env.BUILD_NUMBER} ."
                sh "docker push ${env.DOCKER_REGISTRY}/juleol:${env.BUILD_NUMBER}"
              }
            }
          }
        }
      }
    }

    stage("Deploy") {
      steps {
        script {
          docker.withTool('docker') {
            docker.withServer("tcp://${env.DOCKER_HOST}:2375") {
              sh "docker service update juleol -d --image ${env.DOCKER_REGISTRY}/juleol:${env.BUILD_NUMBER}"
            }
          }
        }
      }
    }
  }
  post {
    failure {
      emailext body: "${env.BUILD_URL}", subject: "${env.JOB_NAME} - Build # ${env.BUILD_NUMBER} - ${currentBuild.result}", to: env.MAIL_ERROR_RCPT
    }
  }
}
