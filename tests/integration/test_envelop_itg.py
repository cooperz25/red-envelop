from scripts import helper, deploy
import hashlib, pytest
from brownie import Contract, exceptions, network


def test_create_envelop():
    if network.show_active() in helper.DEV_NETWORK:
        pytest.skip()

    acc = helper.getAccount()

    redEnvelop = deploy.deploy(acc)

    ethToken = helper.getContract("eth_token")
    ethToken.approve(redEnvelop, 10 ** 18, {"from": acc})
    print(f"allowance {ethToken.allowance(acc, redEnvelop)}")
    m = hashlib.sha256()
    m.update(b"passwordxx")
    digest = m.digest()
    print(f"digest : {digest}")
    txCreate = deploy.createEnvelop(redEnvelop, acc, ethToken, digest)
    txCreate.wait(1)
    print("sol allowance ", txCreate.events["Allowance"]["amount"])
    amount = txCreate.events["TransferFund"]["amount"]
    print(f"amount {amount}")
    myAmount = 10 ** 16 + ((10 ** 16 * 5) / 100)
    print(f"my amount {myAmount}")
    assert amount == myAmount

    creator, amount, message, passWordHash = redEnvelop.getUsersEnvelopInfo(
        acc, digest, {"from": acc}
    )
    assert creator == acc
    assert amount == 10 ** 16
    return redEnvelop, ethToken, acc


def test_claim():
    if network.show_active() in helper.DEV_NETWORK:
        pytest.skip()
    acc1 = helper.getAccount()
    print(f"acc {acc1}")
    redEnvelop, ethToken, creator = test_create_envelop()

    balanceBefore = ethToken.balanceOf(acc1)
    print(f"balance before: {balanceBefore}")
    txClaim = redEnvelop.claim(creator, "passwordxx", {"from": acc1})
    txClaim.wait(1)

    balanceAfter = ethToken.balanceOf(acc1)
    print(f"balance  afrer: {balanceAfter}")

    creatorx = txClaim.events["Claim"]["creator"]
    hashPass = txClaim.events["Claim"]["passWordHash"]
    token = txClaim.events["Claim"]["token"]
    amount = txClaim.events["Claim"]["amount"]

    fromx = txClaim.events["Transfer"]["from"]
    print(f"to : {fromx}")

    to = txClaim.events["Transfer"]["to"]
    print(f"to : {to}")

    value = txClaim.events["Transfer"]["value"]
    print(f"value : {value}")

    assert creatorx == creator
    assert amount == 10 ** 16
    print(f"amount: {amount}")
    assert token == ethToken
    assert (balanceBefore + amount) == balanceAfter
