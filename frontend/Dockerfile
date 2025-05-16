FROM node:23-slim

WORKDIR /app

RUN npm install -g pnpm@8.14.1

COPY package.json pnpm-lock.yaml* ./

RUN pnpm install --frozen-lockfile

COPY . .

RUN npm run build

EXPOSE 3000

CMD ["node", "--env-file=.env", "build"]
