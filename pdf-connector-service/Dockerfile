
FROM node:16.14.0
FROM mcr.microsoft.com/playwright:focal


WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . ./

CMD [ "node", "server.js" ]
