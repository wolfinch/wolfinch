# build wolfinch docker image

VERSION:=1.2.1
IMAGE?=wolfinch:$(VERSION)

.PHONY: all
all: wolfinch

# build wolfinch docker image
.PHONY: wolfinch
wolfinch: wolfinch
ifneq (,$(wildcard Dockerfile))
	DOCKER_BUILDKIT=false docker build . $(NO_CACHE) $(BUILD_ARGS)  -t $(IMAGE) 
else
	echo "Docker file is not present"
endif

#EOF