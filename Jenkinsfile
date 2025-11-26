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
                            if [ -f deploy.log ]; then
                                echo "=== Deployment Log ==="
                                tail -20 deploy.log
                            fi
                            curl -f http://localhost:${APP_PORT}/ || echo "Server not responding yet"
                        """
                    } else {
                        bat """
                            call %VENV_PATH%\\Scripts\\activate
                            echo Starting server on port %APP_PORT%...
                            echo Checking if port %APP_PORT% is available...
                            netstat -an | findstr ":%APP_PORT%" || echo Port %APP_PORT% is free
                            echo.
                            echo Starting Django server...
                            start "Django Server" /B cmd /c "python manage.py runserver 0.0.0.0:%APP_PORT% --noreload > deploy.log 2>&1"
                            echo Waiting for server to start...
                            timeout /t 8 /nobreak >nul
                            echo.
                            if exist deploy.log (
                                echo === Last 30 lines of Deployment Log ===
                                powershell -Command "Get-Content deploy.log -Tail 30"
                                echo.
                            ) else (
                                echo WARNING: deploy.log not found!
                            )
                            echo.
                            echo Checking if server is running on port %APP_PORT%...
                            netstat -an | findstr ":%APP_PORT%"
                            echo.
                            echo Testing server response...
                            powershell -Command "$ErrorActionPreference='Continue'; $maxAttempts=25; $attempt=0; $success=$false; while($attempt -lt $maxAttempts -and -not $success) { try { $response = Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:%APP_PORT%/' -TimeoutSec 3 -ErrorAction Stop; if($response.StatusCode -eq 200) { Write-Host \"SUCCESS: Server is responding with status code $($response.StatusCode)!\" -ForegroundColor Green; $success=$true; exit 0 } } catch { $attempt++; Write-Host \"Attempt $attempt/$maxAttempts: Server not ready yet... ($($_.Exception.Message))\" -ForegroundColor Yellow; if($attempt -lt $maxAttempts) { Start-Sleep -Seconds 2 } } }; if(-not $success) { Write-Host \"ERROR: Server failed to start after $maxAttempts attempts\" -ForegroundColor Red; if(Test-Path deploy.log) { Write-Host \"`n=== Full Deployment Log ===\" -ForegroundColor Red; Get-Content deploy.log } else { Write-Host \"deploy.log not found!\" -ForegroundColor Red }; Write-Host \"`n=== Checking if process is running ===\" -ForegroundColor Yellow; Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like '*manage.py*'} | Format-Table -AutoSize; exit 1 }"
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