# Define base image and working directory
FROM node:16-alpine

WORKDIR /app

# Copy Ollama Mistral model files
# COPY ./mistral_model /app/model

RUN curl https://ollama.ai/install.sh | sh

# Install dependencies for your Node.js application
RUN npm install --save-dev

# Copy Node.js application files
COPY . ./

# Expose port for the server
EXPOSE 3000

# Define entrypoint for the Node.js application
ENTRYPOINT ["node", "server.js"]

# Optional: Configure environment variables or other settings

# Build the image
CMD ["docker-build", "-t", "ollama-mistral-server", "."]
