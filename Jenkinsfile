pipeline {
    // Assign the label 'windows' to the Windows node that will run this job.
    agent { label 'windows' }
    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
    }
    stages {
        stage('Checkout') {
            steps {
                // Clears old results and environments in this job's workspace.
                deleteDir()
                checkout scm
            }
        }
        stage('Install dependencies') {
            steps {
                bat '"C:\Users\g.ghvaberidze\AppData\Local\Python\bin\python.exe" -m venv .venv'
                bat '.venv\\Scripts\\python.exe -m pip install -r requirements.txt'
            }
        }
        stage('Run tests') {
            steps {
                bat '.venv\\Scripts\\python.exe -m pytest tests -v --alluredir=allure-results --clean-alluredir'
            }
            post {
                always {
                    allure includeProperties: false, results: [[path: 'allure-results']]
                }
            }
        }
    }
}
