FROM node:18-alpine
WORKDIR /app

# Install dependencies first (uses package-lock or package.json)
COPY package*.json ./
# Use `npm ci` when package-lock.json exists for reproducible installs.
# If no lockfile, fall back to `npm install --legacy-peer-deps` and don't silence
# output so build logs include any errors for easier debugging.
RUN sh -lc 'if [ -f package-lock.json ]; then npm ci; else npm install --legacy-peer-deps; fi'

# Copy source
COPY . .

# Allow CRA dev server to bind to all interfaces
ENV HOST=0.0.0.0

EXPOSE 3000

CMD ["npm", "start"]
