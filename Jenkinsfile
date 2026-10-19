// Декларативный pipeline для Multibranch Pipeline job.
// CI (любая ветка): checkout -> установка зависимостей -> автотесты.
// CD (только main): развёртывание приложения и smoke-тест.
pipeline {
    agent any

    triggers {
        // Резерв на случай, если webhook от GitHub недоступен (локальный Jenkins без публичного адреса)
        pollSCM('H/2 * * * *')
    }

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    environment {
        PYTHON     = 'python'
        DEPLOY_DIR = 'D:\\course4\\devops\\deploy\\library-app'
        APP_PORT   = '5000'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                bat 'git log -1 --oneline'
            }
        }

        stage('Install dependencies') {
            steps {
                bat '''
                    %PYTHON% -m venv .venv
                    .venv\\Scripts\\python -m pip install --upgrade pip -q
                    .venv\\Scripts\\pip install -r requirements.txt -q
                '''
            }
        }

        stage('Test') {
            steps {
                bat '.venv\\Scripts\\python -m pytest -v --junitxml=reports\\junit.xml'
            }
            post {
                always {
                    junit 'reports/junit.xml'
                }
            }
        }

        stage('Deploy') {
            when { branch 'main' }
            steps {
                powershell '.\\deploy.ps1 -DeployDir $env:DEPLOY_DIR -Port $env:APP_PORT -Python $env:PYTHON'
            }
        }
    }

    post {
        success { echo "Сборка ${env.BRANCH_NAME} #${env.BUILD_NUMBER} прошла успешно" }
        failure { echo "Сборка ${env.BRANCH_NAME} #${env.BUILD_NUMBER} упала" }
    }
}
