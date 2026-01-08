# Multi-stage Dockerfile for Angular frontend

# 1) Build stage
FROM node:20-alpine AS build
WORKDIR /usr/src/app

# Install dependencies first (leverage Docker layer cache)
# Copy only package manifests
COPY app/package*.json ./

# Install dependencies in clean, reproducible way
RUN npm ci

# Copy the rest of the frontend sources
COPY app/ ./

# Build the Angular app for production
# Using the local CLI (from devDependencies) via npx
RUN npx ng build --configuration production

# 2) Runtime stage (NGINX)
FROM nginx:1.27-alpine AS runtime

# Copy custom NGINX config to serve SPA and proxy API to backend service
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built artifacts from the build stage
# Angular application builder outputs to dist/<projectName>/browser by default
COPY --from=build /usr/src/app/dist/app/browser/ /usr/share/nginx/html/

EXPOSE 80

# Use the default nginx entrypoint/cmd
