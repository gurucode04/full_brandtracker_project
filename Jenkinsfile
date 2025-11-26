pipeline {
    agent any

    environment {
        VENV_PATH = 'venv'
        APP_PORT  = '9000'
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
                script {
                    if (isUnix()) {
                        sh """
                            python3 -m venv ${VENV_PATH}
                            . ${VENV_PATH}/bin/activate
                            python -m pip install --upgrade pip
                        """
                    } else {
                        bat """
                            python -m venv %VENV_PATH%
                            call %VENV_PATH%\\Scripts\\activate
                            python -m pip install --upgrade pip
                        """
                    }
                }
            }
        }

        stage('Build') {
            steps {
                script {
                    if (isUnix()) {
                        sh """
                            . ${VENV_PATH}/bin/activate
                            export USE_FULL_NLP=false
                            python -m pip install --no-cache-dir -r requirements-lightweight.txt
                            python manage.py collectstatic --no-input --clear || true
                            python manage.py migrate --noinput
                        """
                    } else {
                        bat """
                            call %VENV_PATH%\\Scripts\\activate
                            set USE_FULL_NLP=false
                            python -m pip install --no-cache-dir -r requirements-lightweight.txt
                            python manage.py collectstatic --no-input --clear
                            python manage.py migrate --noinput
                        """
                    }
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    if (isUnix()) {
                        sh """
                            . ${VENV_PATH}/bin/activate
                            python manage.py test
                        """
                    } else {
                        bat """
                            call %VENV_PATH%\\Scripts\\activate
                            python manage.py test
                        """
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    if (isUnix()) {
                        sh """
                            . ${VENV_PATH}/bin/activate
                            chmod +x start.sh
                            PORT=${APP_PORT} nohup ./start.sh > deploy.log 2>&1 &
                            sleep 5
                        """
                    } else {
                        bat """
                            call %VENV_PATH%\\Scripts\\activate
                            start "" /B python manage.py runserver 0.0.0.0:%APP_PORT% > deploy.log 2>&1
                            ping 127.0.0.1 -n 6 > nul
                        """
                    }
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