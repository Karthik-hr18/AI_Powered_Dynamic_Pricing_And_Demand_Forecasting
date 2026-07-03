FROM node:22-slim

WORKDIR /app

# Copy package descriptors and install packages
COPY package*.json ./
RUN npm install

# Copy application files
COPY . .

EXPOSE 5173

# Run vite dev server exposing it to all network interfaces inside the container
CMD ["npm", "run", "dev", "--", "--host"]
