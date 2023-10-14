
FROM node:16.14.0

WORKDIR /app

COPY package*.json ./

RUN npm install && npx playwright install chromium

COPY . ./

CMD [ "node", "server.js" ]
