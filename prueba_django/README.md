# block_transcendance
Store transcendance users scores in the blockchain

We will store scores of the Pong Tournament in a mutable DB in a Ethereum testnet.

* Set a local testnet to store the scores

* Create a Solidity smart contract

* Integrate it with Django back end of the tournament website

Data structure:

Map = userLogin (string) -> score (uint32)

Optimization:

Only create users that have a score to save
