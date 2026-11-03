FROM node:14-alpine3.15 AS builder

RUN apk add python2 py3-requests py3-shapely build-base

WORKDIR /build/
COPY . /build/

RUN ./prepdata.py

RUN yarn install
RUN yarn build

FROM nginx:stable@sha256:66b50d24288dba67f3d000b31223daefc4868c58d29aaacb6a4ff9771597b5eb

COPY --from=builder /build/build /usr/share/nginx/html/whatifelection
