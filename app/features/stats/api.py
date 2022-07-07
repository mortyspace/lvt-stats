from dependency_injector.wiring import Provide, inject
from fastapi import Depends, Query, status

from app.containers import AppContainer

from . import API
from .containers import StatsContainer
from .models import Transaction, Wallet, WalletWithSentTo
from .tables import TRANSACTION_TABLE, WALLET_TABLE

CONTAINER: StatsContainer = AppContainer.features.stats  # type: ignore


@API.post(
    "/wallet/", status_code=status.HTTP_201_CREATED, response_model=Wallet
)
@inject
async def create_wallet(
    wallet: Wallet, cursor=Depends(Provide[AppContainer.resources.db.cursor])
):
    return await cursor.one(
        WALLET_TABLE.insert(wallet.dict()).returning(WALLET_TABLE), commit=True
    )


@API.post(
    "/wallet/{wallet}/transaction",
    response_model=Transaction,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create_wallet_transaction(
    wallet: str,
    transaction: Transaction,
    cursor=Depends(Provide[AppContainer.resources.db.cursor]),
):
    # if not await cursor.scalar(
    #     WALLET_TABLE.select(WALLET_TABLE.c.id == wallet)
    # ):
    #     raise 404
    data = transaction.dict()
    data["wallet"] = wallet
    return await cursor.one(
        TRANSACTION_TABLE.insert(data).returning(TRANSACTION_TABLE),
        commit=True,
    )


@API.get(
    "/wallet/",
    response_model=list[WalletWithSentTo],
    response_model_exclude={"received_from_id"},
)
@inject
async def get_wallet_many(
    cursor=Depends(Provide[AppContainer.resources.db.cursor]),
    page: int = Query(default=0, ge=0),
    per_page: int = Query(default=50, ge=10, le=200),
):
    wallets = await cursor.many(
        WALLET_TABLE.select(WALLET_TABLE.c.received_from_id.is_(None))
        .limit(per_page)
        .offset(page * per_page)
    )

    # get all related addresses
    related = await cursor.many(
        WALLET_TABLE.select(
            WALLET_TABLE.c.received_from_id.in_(w["id"] for w in wallets)
        )
    )

    # prepare related dict to map received_from_id
    related_wallets: dict[str, list[Wallet]] = {}
    for w in related:
        related_wallets.setdefault(w["received_from_id"], []).append(w)

    # prepare struct with related addreses
    for w in wallets:
        w["sent_to"] = related_wallets.get(w["id"], [])

    return wallets


@API.get("/wallet/{wallet}/transaction", response_model=list[Transaction])
@inject
async def get_wallet_transaction_many(
    wallet: str, cursor=Depends(Provide[AppContainer.resources.db.cursor])
):
    return await cursor.many(
        TRANSACTION_TABLE.select(TRANSACTION_TABLE.c.wallet == wallet)
    )


# @API.post("/addresses/with_transactions", response_code=20)
# async def create_address_with_transactions(
#     addresses: AddressWithTransactions,
#     cursor: DBCursorService = AppContainer.resources.db.cursor,
# ):
#     for address in addresses:
#         address_id = await cursor.scalar(
#             WALLET_TABLE.insert(
#                 address.dict(exclude="transactions")
#             ).returning(WALLET_TABLE.c.id)
#         )
#         for tx in address["transactions"]:
#             tx = tx.dict()
#             tx["address_id"] = address_id
#             await cursor.execute(WALLET_TABLE.insert(tx))
#     await cursor.commit()
