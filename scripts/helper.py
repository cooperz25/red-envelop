from brownie import accounts, network, config, Contract, TokenERC20

DEV_NETWORK = ["development", "gananche-local"]
MAINNET_FORK = ["mainnet-fork-dev", "mainnet-fork-dev2"]


name_to_mock = {
    "eth_token": TokenERC20,
}


def getAccount(index=None, networkId=None):
    if network.show_active() in DEV_NETWORK or network.show_active() in MAINNET_FORK:
        if index:
            return accounts[index]
        if networkId:
            return accounts.load(networkId)
        return accounts[0]

    # default
    return accounts.add(config["wallets"]["key"])


def getContract(contractName):
    contractType = name_to_mock[contractName]
    if network.show_active() in DEV_NETWORK:
        # if len(contractType) <= 0:
        return deployMockContract(contractName)
    # return contractType[-1]
    else:
        contract_address = config["networks"][network.show_active()][contractName]
        contract = Contract.from_abi(
            contractType._name, contract_address, contractType.abi
        )
        return contract


def deployMockContract(contractName):
    splitted = contractName.split("_")
    name = ""
    ticker = ""

    for s in splitted:
        name += s.capitalize()
        ticker += s[0].capitalize()
    return TokenERC20.deploy(10 ** 27, name, ticker, {"from": getAccount()})


def getIsPublish(_networkName):
    if (
        _networkName in DEV_NETWORK
        or _networkName in MAINNET_FORK
        or _networkName == "kovan"
    ):
        return False
    else:
        return True
