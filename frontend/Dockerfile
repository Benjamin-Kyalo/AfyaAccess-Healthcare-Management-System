FROM node:18-alpine

WORKDIR /app

# copy package.json first for caching
COPY package.json package-lock.json* /app/

RUN npm install

# copy project files
COPY . /app

EXPOSE 5173

CMD ["npm", "run", "dev"]
