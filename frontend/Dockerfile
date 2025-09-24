# Use Node.js image for React + Vite
FROM node:22

WORKDIR /app

# Copy package.json first for caching
COPY package*.json ./
RUN npm install

# Copy the rest of frontend code
COPY . .

# Expose Vite port
EXPOSE 3000

# Default command: run Vite dev server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
