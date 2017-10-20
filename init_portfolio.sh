#!/bin/bash

token=$1

function asset {
    curl -d "coin_id=$1&amount=$2&weight=$3" -X POST http://localhost:80/$token/assets
}

asset bitcoin 1.0 0.5
asset monero 71.0 0.5

curl -d "name=drift&threshold=0.5" -X POST http://localhost:80/$token/notifications
curl -d "name=value_usd&threshold=10000" -X POST http://localhost:80/$token/notifications
