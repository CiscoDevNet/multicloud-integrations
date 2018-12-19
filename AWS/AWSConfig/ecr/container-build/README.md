# Docker Image Creation 

A Dockerfile and Makefile are hosted here to assist users who may wish to build and host their own Docker image for use with the ECR Cron solution outlined [here](../ecr-cron.md)

# Usage
By default, the Makefile will:

* Build a Docker image based on the contents of the enclosed [Dockerfile](Dockerfile);
* Login to dockerhub.com or an alternative repo if the value of 'DOCKER_REGISTRY' is set/changed;
* Perform a push to the target registry;



dockerhub.com is the default target registry. To change this and other fields such as Namespace 'NS', either update the appropriate value in the Makefile and run:
```
make
```

or override via a CLI flag such as: 

```
make -e NS=my-namespace -e VERSION=0.1
```

Similarly, if you wish to simply create a Docker image for local use/testing without pushing to a target registry, then execute the following:

```
make build
```