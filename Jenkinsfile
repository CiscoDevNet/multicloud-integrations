#!groovy
//Merging private/working branch and private/published branch and push private/pubslihed to public/pubished branch.
pipeline{
    agent any

    stages {
        stage ('Setup SCM') {
            steps {
                sshagent(['github-engit-ci-ciscolabs-gen-key']) {
                    sh'''
                        git clone git@wwwin-github.cisco.com:CPSG/mci-docs.git
                        git checkout published
                        git checkout working
                    '''
                }
                
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
                sshagent(['github-engit-ci-ciscolabs-gen-key']) {
                    sh'''
                        git checkout published
                        git branch
                        git merge working
                        git status
                        git push origin published
                    '''
                }
                
            }
        }
    }
}