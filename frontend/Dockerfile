FROM node:23-slim

WORKDIR /app

COPY package.json ./

RUN npm install
COPY . .
RUN npm run build

EXPOSE 3000
CMD ["node", "--env-file=.env", "build"]
