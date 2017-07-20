FROM ubuntu

RUN export DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y
RUN apt-get install make build-essential curl wget git python-dev python-pip python-software-properties software-properties-common -y
RUN curl -sL https://deb.nodesource.com/setup | bash -
RUN apt-get update -y
RUN apt-get install nodejs npm -y
RUN npm install -g jscpd
RUN ln -s /usr/bin/nodejs /usr/bin/node
RUN echo '{ "allow_root": true }' > /root/.bowerrc
