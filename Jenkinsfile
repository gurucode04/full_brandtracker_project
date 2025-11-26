pipeline {
    agent any

    environment {
        VENV_PATH = 'venv'
        APP_PORT  = '10000'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/gurucode04/full_brandtracker_project.git'
            }
        }

        stage('Setup Python Env') {
            steps {
                sh """
                    python -m venv ${VENV_PATH}
                    . ${VENV_PATH}/bin/activate
                    pip install --upgrade pip
                """
            }
        }

        stage('Build') {
            steps {
                sh """
                    . ${VENV_PATH}/bin/activate
                    chmod +x build.sh
                    ./build.sh
                """
            }
        }

        stage('Test') {
            steps {
                sh """
                    . ${VENV_PATH}/bin/activate
                    python manage.py test
                """
            }
        }

        stage('Deploy') {
            steps {
                script {
                    sh """
                        . ${VENV_PATH}/bin/activate
                        chmod +x start.sh
                        PORT=${APP_PORT} nohup ./start.sh > deploy.log 2>&1 &
                        sleep 5
                    """
                    env.DEPLOY_URL = "http://localhost:${env.APP_PORT}"
                    echo "Application deployed at ${env.DEPLOY_URL}"
                }
            }
        }
    }

    post {
        success {
            echo "Access the application at ${env.DEPLOY_URL}"
        }
    }
}