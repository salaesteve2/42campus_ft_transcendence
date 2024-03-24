const userDB = artifacts.require("userDB");

module.exports = function (deployer) {
    deployer.deploy(userDB);
};