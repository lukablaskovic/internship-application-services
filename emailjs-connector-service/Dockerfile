
FROM node:16.14.0
FROM mcr.microsoft.com/playwright:focal

WORKDIR /app

COPY package*.json ./

RUN npm install
RUN ln -snf /usr/share/zoneinfo/Europe/Berlin /etc/localtime && echo Europe/Berlin > /etc/timezone

COPY . ./

CMD [ "node", "server.js" ]
