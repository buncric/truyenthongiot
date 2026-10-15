#!/usr/bin/env bash
set -euo pipefail
# Run inside this directory on Debian/WSL. Supply the actual broker LAN IP.
BROKER_IP="${1:?Usage: bash create-certificates.sh 192.168.1.100}"
mkdir -p certs
if [[ -e certs/ca.key || -e certs/server.key ]]; then echo 'Certificates already exist; keep or archive them first.' >&2; exit 1; fi
openssl req -x509 -newkey rsa:2048 -nodes -keyout certs/ca.key -out certs/ca.crt -days 365 -subj '/CN=IoT Lab CA'
openssl req -newkey rsa:2048 -nodes -keyout certs/server.key -out certs/server.csr -subj '/CN=broker.iot.local'
printf 'subjectAltName=IP:%s,DNS:broker.iot.local\nextendedKeyUsage=serverAuth\n' "$BROKER_IP" > certs/server.ext
openssl x509 -req -in certs/server.csr -CA certs/ca.crt -CAkey certs/ca.key -CAcreateserial -out certs/server.crt -days 365 -extfile certs/server.ext
# The isolated lab container must be able to read the mounted server key.
chmod 644 certs/server.key
echo 'Keep ca.key private. Do not commit certs/. Embed ca.crt, never ca.key, in the ESP ca.h.'
