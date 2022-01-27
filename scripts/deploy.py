from scripts import helper
from brownie import RedEnvelop
import hashlib


def main():
    acc = helper.getAccount()

    redEnvelop = deploy(acc)

    ethToken = helper.getContract("eth_token")
    ethToken.approve(redEnvelop, 2 ** 256 - 1, {"from": acc})

    m = hashlib.sha256()
    m.update(b"passwordxx")
    digest = m.digest()
    print(f"digest : {digest}")

    createEnvelop(redEnvelop, acc, ethToken, digest)
    info = redEnvelop.getUsersEnvelopInfo(acc, digest)
    print(f"info: {info}")
    claim(redEnvelop, acc, "passwordxx")
    info = redEnvelop.getUsersEnvelopInfo(acc, digest)
    print(f"info: {info}")


def deploy(acc0):
    redEnvelop = RedEnvelop.deploy({"from": acc0})
    return redEnvelop


def createEnvelop(contract, acc, token, digest):

    tx = contract.createEnvelop(token, 10 ** 16, "helloxxx", digest, {"from": acc})
    tx.wait(1)

    hashDeploy = tx.events["CreateEnvelop"]["hash"]
    print(f"hash deplloy {hashDeploy}   ", tx.events["CreateEnvelop"]["isValid"])
    return tx


def claim(contract, acc, password):
    txClaim = contract.claim(acc, "passwordxx")
    txClaim.wait(1)
