#!/bin/bash
openssl req \
    -new \
    -newkey rsa:4096 \
    -days 365 \
    -subj "/CN=docker.dev.rugion.ru" \
    -nodes \
    -x509 \
    -keyout conf/registry-web/auth.key \
    -out conf/registry/auth.cert
