#!groovy
//Merging private/working branch and private/published branch and push private/pubslihed to public/pubished branch.
pipeline{
    agent any

    stages {
        stage ('Setup SCM') {
            steps {
                sh'''
                    git checkout published
                    git checkout working
                '''
            }
        }
/*        stage('Check if the branches have any difference') {
            steps{
                sh'''
                git diff --exit-code published working
                EXIT_CODE=$?
                '''
                script {
                    echo "$EXIT_CODE"
                    if ($EXIT_CODE == 0) {
                        currentBuild.result = 'SUCCESS'
                        echo 'No diffs in the branches skipping rest of the pipeline'
                        return
                    } else {
                        echo 'Continuing next stages'
                    }
                }
            }
        }*/
        stage('Merge working and published branch') {
            steps{
                sh'''
                    git branch
                    git merge published
                    git checkout published
                    git commit -m "auto-merging from working branch with build id ${BUILD_NUMBER}"
                    git push origin published
                '''
            }
        }
    }
}