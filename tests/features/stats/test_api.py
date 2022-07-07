import pytest
from fastapi import status
from httpx import AsyncClient

from app.containers import AppContainer
from app.features.stats.models import TransactionAction
from app.resources.services import DBCursorService


@pytest.mark.asyncio
async def test_create_wallet_with_received(
    client: AsyncClient, cursor: DBCursorService, app: AppContainer
):
    api = app.features.stats.api()
    input_wallet = {"id": "0x7bA4FDFaC208b82feFc8e371d397E4C79e2568aE"}
    response = await client.post(
        api.url_path_for("create_wallet"), json=input_wallet
    )
    assert response.status_code == status.HTTP_201_CREATED, response.content
    created_wallet = response.json()

    response = await client.get(api.url_path_for("get_wallet_many"))
    wallet = response.json()[0]
    wallet.pop("sent_to")
    created_wallet.pop("received_from_id")
    assert wallet == created_wallet

    response = await client.post(
        api.url_path_for("create_wallet"),
        json={
            "id": "0x5bA4FDFaC208b82feFc8e371d397E4C79e2568aa",
            "received_from_id": "0x7bA4FDFaC208b82feFc8e371d397E4C79e2568aE",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED, response.content

    response = await client.get(api.url_path_for("get_wallet_many"))
    wallet = response.json()[0]
    assert (
        wallet["sent_to"][0]["id"]
        == "0x5bA4FDFaC208b82feFc8e371d397E4C79e2568aa"
    )
    assert wallet["id"] == created_wallet["id"]


@pytest.mark.asyncio
async def test_create_transaction_many(client: AsyncClient, app: AppContainer):
    api = app.features.stats.api()
    wallet = "0x7bA4FDFaC208b82feFc8e371d397E4C79e2568aE"
    await client.post(
        api.url_path_for("create_wallet"),
        json={"id": wallet},
    )

    for i in range(1, 5):
        tx = {
            "id": f"0x6a4cd8db312486a{i}74fa7b8ea6d6"
            "0d4a4e5bba2b69fae7a72c9117ea4051de5d",
            "avax": f"2{i}.{i}",
            "price": f"114.{i}",
            "lvt": f"123{i}04.{i}",
            "executed_at": f"2021-12-1{i}T03:34:16Z",
            "action": TransactionAction.buy,
        }
        print("tx", tx)
        response = await client.post(
            api.url_path_for("create_wallet_transaction", wallet=wallet),
            json=tx,
        )
        assert response.status_code == status.HTTP_201_CREATED, response.json()
