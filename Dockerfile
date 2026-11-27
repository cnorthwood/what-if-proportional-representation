FROM node:14-alpine3.15 AS builder

RUN apk add python2 py3-requests py3-shapely build-base

WORKDIR /build/
COPY . /build/

RUN ./prepdata.py

RUN yarn install
RUN yarn build

FROM nginx:stable@sha256:755983e0e0e568e4c86297cc91485d7a6f9fb73e42d8a19cdba3eac9e8b8cfc9

# k3s pod network: Traefik's pod IP changes on every restart, so trust the whole range
RUN cat >/etc/nginx/conf.d/real-ip.conf <<'EOF'
set_real_ip_from 10.42.0.0/16;
real_ip_header X-Forwarded-For;
EOF

COPY --from=builder /build/build /usr/share/nginx/html/whatifelection
