#!groovy
//Merging private/working branch and private/published branch and push private/pubslihed to public/pubished branch.
pipeline{
    agent any

    stages {
        stage ('Setup SCM') {
            steps {
                sshagent(['github-engit-ci-ciscolabs-gen-key']) {
                    sh'''
                        git checkout working
                        git checkout published    
                    '''
                }
                
            }
        }
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