FROM node:16

RUN npm install -g truffle ganache-cli

WORKDIR /usr/src/app

COPY . .

RUN chmod +x /usr/src/app/start.sh
# RUN chmod +x /usr/src/app/ganache.sh

# EXPOSE 8545 8546

# CMD ["ganache-cli", "--host", "0.0.0.0"]
# CMD ["ganache-cli", "--host", "solidity-dev"]