# using ubuntu LTS version
FROM ubuntu:20.04 AS build

# avoid stuck build due to user prompt
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y software-properties-common && \
          ( yes | add-apt-repository ppa:deadsnakes/ppa ) && apt-get install --no-install-recommends \
        -y python3 python3-dev python3-venv python3-pip python3-wheel build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# create and activate virtual environment
# using final folder name to avoid path issues with packages
RUN mkdir -p /home/venv
RUN mkdir -p /home/wolfinch
RUN python3 -m venv /home/venv
ENV PATH="/home/venv/bin:$PATH"

# install requirements
COPY . .
RUN pip3 install --no-cache-dir wheel
RUN pip3 install --no-cache-dir -r requirements.txt

#install exchange specific requirements.
RUN for l in `ls -d exchanges/*/`; do \ 
        if [ -f $l/requirements.txt ]; then \ 
            pip3 install -r $l/requirements.txt; \
        fi; \
    done;

# RUN sleep 36000

FROM ubuntu:20.04
RUN apt-get update && apt-get install -y software-properties-common && \
                ( yes | add-apt-repository ppa:deadsnakes/ppa ) && \
                apt-get install --no-install-recommends -y python3 python3-venv && \
                apt-get clean && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home wolfinch
COPY --from=build /home/venv /home/venv

USER wolfinch
RUN mkdir -p /home/wolfinch
WORKDIR /home/wolfinch
COPY . .

EXPOSE 8080

# make sure all messages always reach console
ENV PYTHONUNBUFFERED=1

# activate virtual environment
ENV VIRTUAL_ENV=/home/venv
ENV PATH="/home/venv/bin:$PATH"
ENV PYTHONPATH=$PYTHONPATH:/home/wolfinch

# /dev/shm is mapped to shared memory and should be used for gunicorn heartbeat
# this will improve performance and avoid random freezes

ENTRYPOINT ["bash", "-l", "-c"]
