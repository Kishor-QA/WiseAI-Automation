pipeline {
    agent { label 'mirage-agent' }

    environment {
        QA_REPO_DIR = '/home/mirage/wiseai/wiseai-automation'
        BRANCH = 'dev'
        REPORT_HOST_DIR = '/home/mirage/wiseai/qa-report-host'
        REPORT_DATA_DIR = '/home/mirage/wiseai/qa-report-host/data'
    }

    stages {

        stage('Checkout QA Automation Repo') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'govind-yadav',
                    usernameVariable: 'GITHUB_USER',
                    passwordVariable: 'GITHUB_PAT'
                )]) {
                    sh '''
                        set -e
                        if [ ! -d "${QA_REPO_DIR}/.git" ]; then
                            mkdir -p "$(dirname ${QA_REPO_DIR})"
                            git clone -b ${BRANCH} https://${GITHUB_USER}:${GITHUB_PAT}@github.com/Kishor-QA/WiseAI-Automation.git ${QA_REPO_DIR}
                        else
                            cd ${QA_REPO_DIR}
                            git remote set-url origin https://${GITHUB_USER}:${GITHUB_PAT}@github.com/Kishor-QA/WiseAI-Automation.git
                            git fetch origin
                            git checkout ${BRANCH}
                            git pull origin ${BRANCH}
                        fi
                    '''
                }
            }
        }

        stage('Clean Previous Reports') {
            steps {
                sh '''
                    rm -rf "${QA_REPO_DIR}/reports"/report*
                    mkdir -p "${QA_REPO_DIR}/reports"
                '''
            }
        }

        stage('Run QA Automation Tests') {
            steps {
                sh '''
                    cd ${QA_REPO_DIR}
                    docker compose build
                    docker compose run --rm automation 
                '''
            }
        }
    }

    post {
        always {
            sh '''
                cd ${QA_REPO_DIR} || exit 0
                docker compose down || true

                rm -rf "${WORKSPACE}/reports"
                mkdir -p "${WORKSPACE}/reports"

                if [ -d reports ]; then
                    cp -f reports/*.html "${WORKSPACE}/reports/" 2>/dev/null || true
                fi
            '''
            archiveArtifacts artifacts: 'reports/*.html', allowEmptyArchive: true, onlyIfSuccessful: false

            script {
                def latest = sh(
                    script: "ls -t ${WORKSPACE}/reports/*.html 2>/dev/null | head -n1 || true",
                    returnStdout: true
                ).trim()

                if (latest) {
                    sh """
                        set -e
                        mkdir -p "${REPORT_DATA_DIR}"

                        cp -f "${latest}" "${REPORT_DATA_DIR}/"

                        cp -f "${latest}" "${REPORT_DATA_DIR}/index.html"

                        cd "${REPORT_HOST_DIR}"
                        docker compose up -d
                    """
                    echo "Latest report republished — reachable at http://<some-custom-dns>:8081/"
                } else {
                    echo 'No HTML report found to publish.'
                }
            }
        }

        success {
            echo 'QA automation passed'
        }

        failure {
            echo 'QA automation FAILED'
        }
    }
}