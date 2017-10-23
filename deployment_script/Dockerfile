FROM gitlab.devartis.com:4567/devops/image-utils:alpine_ssh
MAINTAINER lgomez@devartis.com

WORKDIR /simple_deploy/
RUN apk add --no-cache bash python3 gcc make g++ python3-dev libffi libffi-dev openssl-dev && \
    /usr/bin/easy_install-3.5 pip && \
    pip install -U pip && \
    pip3 install --no-cache-dir cffi && \
    pip3 install --no-cache-dir ansible;
COPY ./ /simple_deploy/
ENTRYPOINT ["bash", "entrypoint.sh"]
