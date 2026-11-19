def call(Map config = [:]) {
    ['serviceName', 'sourceImage', 'repository'].each { key ->
        if (!config[key]) {
            error("pushImageToEcr requires '${key}'")
        }
    }

    def accountId = sh(
        script: 'aws sts get-caller-identity --query Account --output text',
        returnStdout: true
    ).trim()
    def registry = "${accountId}.dkr.ecr.${env.AWS_REGION}.amazonaws.com"
    def buildImage = "${registry}/${config.repository}:${env.IMAGE_TAG}"
    def latestImage = "${registry}/${config.repository}:latest"

    sh """#!/bin/sh
set -eu
aws ecr get-login-password --region '${env.AWS_REGION}' | docker login --username AWS --password-stdin '${registry}'
docker tag '${config.sourceImage}' '${buildImage}'
docker push '${buildImage}'
docker tag '${config.sourceImage}' '${latestImage}'
docker push '${latestImage}'
"""

    return buildImage
}
