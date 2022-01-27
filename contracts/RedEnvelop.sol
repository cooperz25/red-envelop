// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract RedEnvelop {
    // struct EnvelopPack {
    //     address givingToken;
    //     address creator;
    //     uint256 numberOfEnvelop;
    //     uint256 amountInsideEachEnvelop;
    //     uint256 totalAmount;
    //     string message;
    //     bytes32[] passWordHashs;
    // }

    struct Envelop {
        address givingToken;
        address creator;
        uint256 amount;
        string message;
        bytes32 passWordHash;
        address claimer;
    }

    // mapping(address => EnvelopPack[]) user2EnvelopPacks;
    mapping(address => mapping(bytes32 => Envelop)) user2Envelop;
    uint256 constant FEE_PERCENTAGE = 5;
    event CreateEnvelop(bytes32 hash, bool isValid);
    event TransferFund(address sender, address receiver, uint256 amount);
    event Claim(
        address creator,
        bytes32 passWordHash,
        address token,
        uint256 amount
    );
    event Allowance(uint256 amount);

    // function createRedEnvelopPack(
    //     address _givingToken,
    //     uint256 _numberOfEnvelop,
    //     uint256 _amountInsideEachEnvelop,
    //     string memory _messageForEachEnvelop,
    //     bytes32[] memory _passWordHashs
    // ) public {
    //     //require
    //     require(
    //         _numberOfEnvelop >= 1,
    //         "Number of Red Envelop must be greater than 1"
    //     );
    //     require(
    //         _amountInsideEachEnvelop > 0,
    //         "Amount of asset must be greater than zero"
    //     );
    //     require(
    //         _passWordHashs.length == _numberOfEnvelop,
    //         "Error: Pass word hashs is insufficient!"
    //     );
    //     //
    //     uint256 totalAmount = _numberOfEnvelop * _amountInsideEachEnvelop;
    //     IERC20 token = IERC20(_givingToken);
    //     token.transferFrom(msg.sender, address(this), totalAmount);

    //     //do
    //     EnvelopPack memory envelopPack = EnvelopPack(
    //         _givingToken,
    //         msg.sender,
    //         _numberOfEnvelop,
    //         _amountInsideEachEnvelop,
    //         _numberOfEnvelop * _amountInsideEachEnvelop,
    //         _messageForEachEnvelop,
    //         _passWordHashs
    //     );
    //     user2EnvelopPacks[msg.sender].push(envelopPack);
    // }

    function createEnvelop(
        address _givingToken,
        uint256 _amount,
        string memory _message,
        bytes32 _passWordHash
    ) public {
        require(_givingToken != address(0), "Token invalid!");
        require(_amount > 0, "Amount of asset must be greater than zero");
        //require passWordHash has not existed yet!
        require(
            user2Envelop[msg.sender][_passWordHash].creator == address(0),
            "This envelop has been created before, try another code!"
        );

        IERC20 token = IERC20(_givingToken);
        uint256 allowance = token.allowance(msg.sender, address(this));
        emit Allowance(allowance);
        uint256 amountAndFee = _amount + (_amount * FEE_PERCENTAGE) / 100;
        require(
            allowance >= amountAndFee,
            "Your allowance is not enought, please approve more!"
        );

        token.transferFrom(msg.sender, address(this), amountAndFee);
        emit TransferFund(msg.sender, address(this), amountAndFee);

        Envelop memory envelop = Envelop(
            _givingToken,
            msg.sender,
            _amount,
            _message,
            _passWordHash,
            address(0) //by default, there is no claimer yet
        );
        user2Envelop[msg.sender][_passWordHash] = envelop;
        emit CreateEnvelop(_passWordHash, false);
    }

    function claim(address _creator, string memory _passWord) public {
        require(_creator != address(0));
        (bool isValid, bytes32 passWordHash) = isPasswordValid(
            _creator,
            _passWord
        );

        require(isValid, "Wrong password!");
        if (isValid) {
            Envelop memory envelop = user2Envelop[_creator][passWordHash];
            emit Claim(
                _creator,
                passWordHash,
                envelop.givingToken,
                envelop.amount
            );
            sendLuckMoney(
                _creator,
                passWordHash,
                msg.sender,
                envelop.givingToken,
                envelop.amount
            );
        }
    }

    function sendLuckMoney(
        address _creator,
        bytes32 _hashPass,
        address _luckyPerson,
        address _givingToken,
        uint256 _amount
    ) public {
        //send
        IERC20(_givingToken).transfer(_luckyPerson, _amount);
        //delete the just sent envelop
        delete (user2Envelop[_creator][_hashPass]);
    }

    function isPasswordValid(address _creator, string memory _passWord)
        public
        returns (bool, bytes32)
    {
        bytes32 passWordHash = sha256(abi.encodePacked(_passWord)); //convert bytes32 to bytes and then hash
        Envelop memory envelop = user2Envelop[_creator][passWordHash];
        require(
            envelop.creator != address(0),
            "This red envelop doesn't exist!"
        );
        return (passWordHash == envelop.passWordHash, passWordHash);
    }

    function getUsersEnvelopInfo(address _user, bytes32 _hash)
        public
        view
        returns (
            address,
            uint256,
            string memory,
            bytes32
        )
    {
        return (
            user2Envelop[_user][_hash].creator,
            user2Envelop[_user][_hash].amount,
            user2Envelop[_user][_hash].message,
            user2Envelop[_user][_hash].passWordHash
        );
    }
}
