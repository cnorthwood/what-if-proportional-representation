FROM node:14-alpine3.15 AS builder

RUN apk add python2 py3-requests py3-shapely build-base

WORKDIR /build/
COPY . /build/

RUN ./prepdata.py

RUN yarn install
RUN yarn build

FROM nginx:stable@sha256:7fad6c0dff97965adbddf28027d934b111fc0221a554315dc274712f3fba24d3

COPY --from=builder /build/build /usr/share/nginx/html/whatifelection
