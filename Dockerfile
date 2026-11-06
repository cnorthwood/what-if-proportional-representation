FROM node:14-alpine3.15 AS builder

RUN apk add python2 py3-requests py3-shapely build-base

WORKDIR /build/
COPY . /build/

RUN ./prepdata.py

RUN yarn install
RUN yarn build

FROM nginx:stable@sha256:42c68eab6f7e22611786a9fe1d1c019e275c50185bd54b8f75dc2b9184322703

COPY --from=builder /build/build /usr/share/nginx/html/whatifelection
