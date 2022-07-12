from decimal import Decimal

import pytest
from fastapi import status
from httpx import AsyncClient

from app.containers import AppContainer
from app.features.stats.models import TransactionAction


@pytest.fixture
def test_wallets_data():
    return [
        {
            "id": f"0x7bA4FDFaC208b82feFc8e371d397E4C79e{num:3g}8aE",
            "is_ignored": False,
            "received_from_id": None,
        }
        for num in range(300)
    ]


@pytest.mark.asyncio
async def test_create_wallet_with_received(
    client: AsyncClient, test_wallets_data
):
    for wallet in test_wallets_data:
        response = await client.post("/wallet", json=wallet)
        assert (
            response.status_code == status.HTTP_201_CREATED
        ), response.content
        assert response.json() == wallet

    response = await client.post(
        "/wallet",
        json={
            "id": "0x5bA4FDFaC208b82feFc8e371d397E4C79e2568aa",
            "received_from_id": "0x7bA4FDFaC208b82feFc8e371d397E4C79e2568aE",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED, response.content

    response = await client.get("/wallet")
    # assert "0x5bA4FDFaC208b82feFc8e371d397E4C79e2568aa" not in {
    #     w["id"] for w in response.json()
    # }


@pytest.mark.asyncio
async def test_create_transaction_many(client: AsyncClient, app: AppContainer):
    wallet = "0x7bA4FDFaC208b82feFc8e371d397E4C79e2568aE"

    # TODO: fix migration and db state per test
    # response = await client.post("/wallet/", json={"id": wallet})
    # assert response.status_code == status.HTTP_201_CREATED

    # "21.1 + 22.2 + 23.3 + 24.4 + 25.5"
    for i in range(1, 500):
        tx = {
            "id": f"0x6a4cd8db312486a{i:3g}fa7b8ea6d6"
            "0d4a4e5bba2b69fae7a72c9117ea4051de5d",
            "avax": f"2{i}.{i}",
            "price": f"114.{i}",
            "lvt": f"123{i}04.{i}",
            "executed_at": "2021-12-12T03:34:16Z",
            "action": TransactionAction.buy.value,
            "wallet": wallet.replace("A", "B"),
        }
        response = await client.post(
            "/wallet/transaction",
            json=tx,
        )
        assert (
            response.status_code == status.HTTP_404_NOT_FOUND
        ), response.json()

        tx["wallet"] = wallet
        tx["avax"] = "3"
        response = await client.post(
            "/wallet/transaction",
            json=tx,
        )
        # print("add tx", tx["wallet"], tx["avax"])
        assert response.status_code == status.HTTP_201_CREATED, response.json()

    # for i in range(1, 5):
    #     tx = {
    #         "id": f"0x6a4cd8db312486b{i}74fa7b8ea6d6"
    #         "0d4a4e5bba2b69fae7a72c9117ea4051de5d",
    #         "avax": f"0",
    #         "price": f"114.{i}",
    #         "lvt": f"123{i}04.{i}",
    #         "executed_at": f"2021-12-1{i}T03:34:16Z",
    #         "action": TransactionAction.sell.value,
    #         "wallet": wallet,
    #     }
    #     response = await client.post(
    #         "/wallet/transaction",
    #         json=tx,
    #     )
    #  assert response.status_code == status.HTTP_201_CREATED, response.json()

    related_wallet = "0x5bA4FDFaC208b82feFc8e371d397E4C79e2568aa"
    for i in range(1, 5):
        tx = {
            "id": f"0x6a4cd8db3124d6b{i}74fa7b8ea6d6"
            "0d4a4e5bba2b69fae7a72c9117ea4051de5d",
            "avax": "1",
            "price": f"114.{i}",
            "lvt": f"123{i}04.{i}",
            "executed_at": f"2021-12-1{i}T03:34:16Z",
            "action": TransactionAction.buy.value,
            "wallet": related_wallet,
        }
        response = await client.post(
            "/wallet/transaction",
            json=tx,
        )
        assert response.status_code == status.HTTP_201_CREATED, response.json()

    response = await client.get(
        "/wallet", params={"order_by": "avax_invested", "order_desc": True}
    )

    item = next(
        w
        for w in response.json()
        if w["id"] == "0x7bA4FDFaC208b82feFc8e371d397E4C79e2568aE"
    )
    assert Decimal(item["avax_invested"]) == Decimal(1501)
