#!/bin/bash

# sleep 600

ganache-cli &

sleep 5

truffle compile --all

truffle migrate

truffle test

grep -o '"address": "[^"]*"' /usr/src/app/build/contracts/userDB.json | awk -F'"' '{print $4}' > /usr/src/app/block/contract_address.txt

while true; do
  sleep 60
done
