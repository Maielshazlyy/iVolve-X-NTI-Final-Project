FROM node:24.22.3-alpine3.24

WORKDIR /app

# Refresh the npm bundled with the Node image. The pinned CLI release includes
# patched brace-expansion and undici dependencies reported by Trivy.
RUN npm install --global npm@11.21.2

COPY package*.json ./
RUN npm install --omit=dev

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
