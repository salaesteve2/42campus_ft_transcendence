const userDB = artifacts.require("userDB");

contract("userDB", (accounts) => {
    it("register a new user", async () => {
        const instance = await userDB.deployed();
        await instance.doUser("testUser", 100);
        const userScore = await instance.getUserScore("testUser");
        assert.equal(userScore, 100, "User score should be 100");
    });

});