// SPDX-License-Identifier: MIT
pragma solidity ^0.5.16;

contract userDB {

    event newUser(string _login, uint32 _score);
    event scoreUpdate(string _login, uint32 _score);

    struct user {
        string login;
        uint32 score;
    }

    mapping(string => user) public Users;

    function doUser (string memory _login, uint32 _score) public {
        if (bytes(Users[_login].login).length == 0) {
            Users[_login] = user(_login, _score); 
            emit newUser(_login, _score);
        } else {
            if (_score > Users[_login].score) {
                Users[_login].score = _score;
                emit scoreUpdate(_login, _score);
            }
        }
    }

    function getUserScore(string memory _login) public view returns (uint32) {
        return Users[_login].score;
    }
}
