# ============================
# 1) FRONTEND BUILD STAGE
# ============================
FROM node:22-alpine AS build

WORKDIR /app

# Copy package files first (better caching)
COPY package*.json ./
RUN npm install

# Copy rest of the frontend
COPY . .

# Build Vite app – dist/ will be created
RUN npm run build



# ============================
# 2) NGINX SERVE STAGE
# ============================
FROM nginx:1.25-alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Add your custom config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy Vite output to nginx html directory
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 5173
CMD ["nginx", "-g", "daemon off;"]
