FROM alpine:latest
LABEL maintainer="xavier@classheroes.com"
RUN apk add --no-cache bash python3 git build-base py3-yaml
WORKDIR /srv
ADD . /srv
RUN python3 setup.py develop
RUN python3 -m swag.merger --help
RUN python3 -m swag.flattener --help
RUN python3 -m swag.rspec --help
WORKDIR /build
