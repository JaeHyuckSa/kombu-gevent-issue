#!/bin/bash
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"

# CA
openssl genrsa -out "$DIR/ca-key.pem" 2048
openssl req -new -x509 -key "$DIR/ca-key.pem" -out "$DIR/ca-cert.pem" -days 365 \
  -subj "/CN=RabbitMQ-CA"

# Server
openssl genrsa -out "$DIR/server-key.pem" 2048
openssl req -new -key "$DIR/server-key.pem" -out "$DIR/server.csr" \
  -subj "/CN=rabbitmq"
openssl x509 -req -in "$DIR/server.csr" -CA "$DIR/ca-cert.pem" -CAkey "$DIR/ca-key.pem" \
  -CAcreateserial -out "$DIR/server-cert.pem" -days 365

rm -f "$DIR/server.csr" "$DIR/ca-cert.srl"

echo "Generated TLS certificates in $DIR"
