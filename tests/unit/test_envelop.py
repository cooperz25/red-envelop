from scripts import helper, deploy
import hashlib, pytest
from brownie import exceptions, network


def test_create_envelop():
    if network.show_active() not in helper.DEV_NETWORK:
        pytest.skip()
    acc0 = helper.getAccount(0)
    acc1 = helper.getAccount(1)

    redEnvelop = deploy.deploy(acc0)

    ethToken = helper.getContract("eth_token")
    ethToken.transfer(acc1, 9 * 10 ** 26, {"from": acc0})
    ethToken.approve(redEnvelop, 2 ** 256 - 1, {"from": acc1})

    m = hashlib.sha256()
    m.update(b"passwordxx")
    digest = m.digest()
    print(f"digest : {digest}")
    txCreate = deploy.createEnvelop(redEnvelop, acc1, ethToken, digest, {"from": acc1})
    amount = txCreate.events["TransferFund"]["amount"]
    print(f"amount {amount}")
    myAmount = 10 ** 18 + ((10 ** 18 * 5) / 100) + 10
    print(f"my amount {myAmount}")
    assert amount == myAmount

    creator, amount, message, passWordHash = redEnvelop.getUsersEnvelopInfo(
        acc1, digest, {"from": acc1}
    )
    assert creator == acc1
    assert amount == 10 ** 18
    return redEnvelop, ethToken, acc1


def test_claim():
    if network.show_active() not in helper.DEV_NETWORK:
        pytest.skip()
    acc1 = helper.getAccount(2)
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
    assert amount == 10 ** 18
    print(f"amount: {amount}")
    assert token == ethToken
    assert (balanceBefore + amount) == balanceAfter

    with pytest.raises(exceptions.VirtualMachineError):
        txClaim = redEnvelop.claim(creator, "passwordxx", {"from": acc1})
