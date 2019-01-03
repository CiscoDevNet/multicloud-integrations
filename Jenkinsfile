#!groovy
//Merging private/working branch and private/published branch and push private/pubslihed to public/pubished branch.
pipeline{
    agent any

    stages {
        stage ('Setup SCM') {
            steps {
                sh'''
                    git fetch --all
                    git checkout published
                    git checkout working
                '''
            }
        }
        stage('Check if the branches have any difference') {
            steps{
                sh'''
                EXIT_CODE=$(git diff --exit-code published working)
                '''
                if($EXIT_CODE == 0){
                    currentBuild.result = 'SUCCESS'
                    return
                }
            }
        }
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