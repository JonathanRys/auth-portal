# Build web app
FROM oven/bun as build

# Set the workdir
WORKDIR /usr/app

# Copy the app
COPY ./ /usr/app/

# Install dependencies
RUN bun install

# Build the app
# RUN bunx run build
RUN bun build ./src/index.tsx --outdir=/usr/app/build/

# Configure web server
FROM nginx:1.23.1-alpine
EXPOSE 80

# Copy files
COPY ./docker/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf
COPY --from=build /usr/app/build/. /usr/share/nginx/html/
