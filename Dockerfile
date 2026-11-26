FROM node:14-alpine3.15 AS builder

RUN apk add python2 py3-requests py3-shapely build-base

WORKDIR /build/
COPY . /build/

RUN ./prepdata.py

RUN yarn install
RUN yarn build

FROM nginx:stable@sha256:755983e0e0e568e4c86297cc91485d7a6f9fb73e42d8a19cdba3eac9e8b8cfc9

COPY --from=builder /build/build /usr/share/nginx/html/whatifelection
