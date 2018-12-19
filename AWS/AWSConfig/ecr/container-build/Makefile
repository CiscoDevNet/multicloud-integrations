VERSION ?= latest
NS ?= ciscomulticloud
IMAGE_NAME ?= aws-kubectl
#defaults to dockerhub
DOCKER_REGISTRY ?= 

.PHONY: all
all: build login push

.Phony: build
build:
	docker build -t $(NS)/$(IMAGE_NAME):$(VERSION) -f Dockerfile .

.Phony: login
login:
	docker login $(DOCKER_REGISTRY)

.Phony: push
push:
	docker push $(NS)/$(IMAGE_NAME):$(VERSION)