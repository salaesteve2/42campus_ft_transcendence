// SPDX-License-Identifier: MIT
pragma solidity ^0.8.25;

contract userDB {

    event userScore(string _login, uint8 _score, uint32 _tournamentId);

    struct user {
        string login;
        uint8 score;
        uint32 tournamentId;
    }

    mapping(string => user) public Users;

    function doUser (string memory _login, uint8 _score, uint32 _tournamentId) public {
        require(bytes(_login).length > 0, "Login cannot be empty");
        require(_score <= 255 && _score >= 0, "Score should not exceed 255 or be less than 0");
        require(_tournamentId >= 0, "Tournament ID must be greater than 0");
        Users[_login] = user(_login, _score, _tournamentId);
        emit userScore(_login, _score, _tournamentId);
    }
}