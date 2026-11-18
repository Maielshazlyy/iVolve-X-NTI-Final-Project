def call(Map config = [:]) {
    ['serviceName', 'context'].each { key ->
        if (!config[key]) {
            error("serviceCiPipeline requires '${key}'")
        }
    }

    def serviceName = config.serviceName.toString()
    def context = config.context.toString()

    pipeline {
        agent { label 'ivolve-build' }

        options {
            timestamps()
            disableConcurrentBuilds()
        }

        environment {
            AWS_REGION = 'eu-north-1'
            ECR_REPOSITORY_PREFIX = 'ivolve-x/dev'
            IMAGE_TAG = "${env.BUILD_NUMBER}"
        }

        stages {
            // Declarative Pipeline requires stage names to be string literals.
            // The service is already visible in the Jenkins job name and logs.
            stage('Build and scan') {
                steps {
                    script {
                        buildAndScanImage(
                            serviceName: serviceName,
                            context: context,
                            image: "ivolve/${serviceName}:${env.IMAGE_TAG}"
                        )
                    }
                }
            }

            stage('Push to Amazon ECR') {
                steps {
                    withCredentials([usernamePassword(
                        credentialsId: 'aws-ecr-push',
                        usernameVariable: 'AWS_ACCESS_KEY_ID',
                        passwordVariable: 'AWS_SECRET_ACCESS_KEY'
                    )]) {
                        pushImageToEcr(
                            serviceName: serviceName,
                            sourceImage: "ivolve/${serviceName}:${env.IMAGE_TAG}",
                            repository: "${env.ECR_REPOSITORY_PREFIX}/${serviceName}"
                        )
                    }
                }
            }
        }

        post {
            always {
                echo "CI pipeline finished for ${serviceName}, build ${env.BUILD_NUMBER}."
            }
        }
    }
}
