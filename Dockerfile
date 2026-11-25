FROM node:14-alpine3.15 AS builder

RUN apk add python2 py3-requests py3-shapely build-base

WORKDIR /build/
COPY . /build/

RUN ./prepdata.py

RUN yarn install
RUN yarn build

FROM nginx:stable@sha256:c2c7e8370da496dc7283497fcd3a0cbe648d7f18b6c62ee1d0675f474d499aeb

COPY --from=builder /build/build /usr/share/nginx/html/whatifelection
