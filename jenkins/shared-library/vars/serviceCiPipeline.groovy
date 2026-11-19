def call(Map config = [:]) {
    ['serviceName', 'context', 'manifestPath'].each { key ->
        if (!config[key]) {
            error("serviceCiPipeline requires '${key}'")
        }
    }

    def serviceName = config.serviceName.toString()
    def context = config.context.toString()
    def manifestPath = config.manifestPath.toString()

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
                        script {
                            env.PUBLISHED_IMAGE = pushImageToEcr(
                                serviceName: serviceName,
                                sourceImage: "ivolve/${serviceName}:${env.IMAGE_TAG}",
                                repository: "${env.ECR_REPOSITORY_PREFIX}/${serviceName}"
                            )
                        }
                    }
                }
            }

            stage('Update Kubernetes manifest and push') {
                steps {
                    script {
                        updateKubernetesManifest(
                            serviceName: serviceName,
                            manifestPath: manifestPath,
                            image: env.PUBLISHED_IMAGE
                        )
                    }
                }
            }
        }

        post {
            always {
                script {
                    def publishedImage = env.PUBLISHED_IMAGE ?: ''
                    def latestImage = publishedImage ? publishedImage.replaceFirst(/:[^:]+$/, ':latest') : ''
                    sh(
                        returnStatus: true,
                        script: "docker image rm -f 'ivolve/${serviceName}:${env.IMAGE_TAG}' '${publishedImage}' '${latestImage}' >/dev/null 2>&1"
                    )
                }
                echo "CI pipeline finished for ${serviceName}, build ${env.BUILD_NUMBER}."
            }
        }
    }
}
