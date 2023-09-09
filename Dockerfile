# FROM node:16.17.1-alpine3.16 as build
FROM oven/bun as build

# Set the workdir
WORKDIR /usr/app

# Copy the app
COPY . /usr/app

RUN mkdir /usr/app/dist

RUN bun install
RUN bun build ./src/index.tsx --outdir=/usr/app/dist/
#RUN npm ci
#RUN npm run build

FROM nginx:1.23.1-alpine
EXPOSE 80
COPY ./docker/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf
COPY --from=build /usr/app/dist /usr/share/nginx/html
