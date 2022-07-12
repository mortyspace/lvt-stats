import sqlalchemy as sa
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.containers import AppContainer

from .models import Transaction, TransactionAction, Wallet, WalletWithAggrInfo
from .tables import TRANSACTION_TABLE, WALLET_TABLE

API = APIRouter()


@API.post(
    "/wallet", status_code=status.HTTP_201_CREATED, response_model=Wallet
)
@inject
async def create_wallet(
    wallet: Wallet,
    cursor=Depends(Provide[AppContainer.resources.db.cursor]),
):
    return await cursor.one(
        WALLET_TABLE.insert(wallet.dict()).returning(WALLET_TABLE), commit=True
    )


@API.get(
    "/wallet",
    response_model=list[WalletWithAggrInfo],
    response_model_exclude={"received_from_id"},
)
@inject
async def get_wallet_many(
    response: Response,
    cursor=Depends(Provide[AppContainer.resources.db.cursor]),
    page: int = Query(default=0, ge=0),
    per_page: int = Query(default=50, ge=10, le=200),
    order_by: str = "",
    order_desc: bool = False,
):
    TT = TRANSACTION_TABLE
    TA = TransactionAction
    aggr_query = (
        sa.select(
            [
                sa.func.coalesce(
                    WALLET_TABLE.c.received_from_id, WALLET_TABLE.c.id
                ).label("grouped_wallet"),
                sa.func.sum(
                    sa.case(
                        [(TT.c.action == TA.buy, TT.c.avax)],
                        else_=0,
                    )
                ).label("avax_invested"),
                sa.func.sum(
                    sa.case(
                        [(TT.c.action == TA.sell, TT.c.avax)],
                        else_=0,
                    )
                ).label("avax_got_back"),
                sa.func.sum(
                    sa.case(
                        [(TT.c.action == TA.buy, TT.c.avax * TT.c.price)],
                        else_=0,
                    )
                ).label("usd_invested"),
                sa.func.sum(
                    sa.case(
                        [(TT.c.action == TA.sell, TT.c.avax * TT.c.price)],
                        else_=0,
                    )
                ).label("usd_got_back"),
                sa.func.sum(
                    sa.case(
                        [(TT.c.action == TA.buy, TT.c.lvt)],
                        else_=0,
                    )
                ).label("lvt_bought"),
                sa.func.sum(
                    sa.case(
                        [(TT.c.action == TA.invest_v1, TT.c.lvt)],
                        else_=0,
                    )
                ).label("lvt_invested_v1"),
                sa.func.sum(
                    sa.case(
                        [(TT.c.action == TA.invest_v2, TT.c.lvt)],
                        else_=0,
                    )
                ).label("lvt_invested_v2"),
                sa.func.greatest(
                    sa.func.sum(
                        sa.case(
                            [
                                (
                                    TT.c.action.in_(
                                        [TA.invest_v1, TA.invest_v2]
                                    ),
                                    TT.c.lvt,
                                )
                            ],
                            else_=0,
                        )
                    )
                    / sa.func.nullif(
                        sa.func.sum(
                            sa.case(
                                [(TT.c.action == TA.buy, TT.c.lvt)],
                                else_=0,
                            )
                        ),
                        sa.cast(0, sa.Numeric(23, 8)),
                    ),
                    sa.cast(0, sa.Numeric(23, 8)),
                ).label("lvt_invested_ratio"),
            ]
        )
        .join(WALLET_TABLE, WALLET_TABLE.c.id == TT.c.wallet)
        .group_by("grouped_wallet")
        .subquery()
    )

    # filter received wallets only without dependent
    wallets_query = (
        sa.select(
            [
                WALLET_TABLE.c.id,
                sa.func.coalesce(aggr_query.c.avax_invested, 0).label(
                    "avax_invested"
                ),
                sa.func.coalesce(aggr_query.c.avax_got_back, 0).label(
                    "avax_got_back"
                ),
                sa.func.coalesce(aggr_query.c.usd_invested, 0).label(
                    "usd_invested"
                ),
                sa.func.coalesce(aggr_query.c.usd_got_back, 0).label(
                    "usd_got_back"
                ),
                sa.func.coalesce(aggr_query.c.lvt_bought, 0).label(
                    "lvt_bougth"
                ),
                sa.func.coalesce(aggr_query.c.lvt_invested_v1, 0).label(
                    "lvt_invested_v1"
                ),
                sa.func.coalesce(aggr_query.c.lvt_invested_v2, 0).label(
                    "lvt_invested_v2"
                ),
                sa.func.coalesce(aggr_query.c.lvt_invested_ratio, 0).label(
                    "lvt_invested_ratio"
                ),
            ]
        )
        .outerjoin(
            aggr_query, WALLET_TABLE.c.id == aggr_query.c.grouped_wallet
        )
        .where(WALLET_TABLE.c.received_from_id.is_(None))
    )

    total_count = await cursor.scalar(
        sa.select(sa.func.count("*")).select_from(wallets_query.subquery())
    )
    response.headers["X-Total-Count"] = str(total_count)
    response.headers["X-Has-More"] = str(page * per_page < total_count)

    wallets_query = wallets_query.offset(per_page * page).limit(per_page)

    if order_by in set(str(c) for c in wallets_query.subquery().c):
        wallets_query = wallets_query.order_by(
            sa.desc(order_by) if order_desc else order_by
        )

    return await cursor.many(wallets_query)


@API.get("/wallet/{wallet}/transaction", response_model=list[Transaction])
@inject
async def get_wallet_transaction_many(
    wallet: str,
    cursor=Depends(Provide[AppContainer.resources.db.cursor]),
):
    return await cursor.many(
        TRANSACTION_TABLE.select(TRANSACTION_TABLE.c.wallet == wallet)
    )


@API.post(
    "/wallet/transaction",
    response_model=Transaction,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create_wallet_transaction(
    transaction: Transaction,
    cursor=Depends(Provide[AppContainer.resources.db.cursor]),
):
    data = transaction.dict()
    if not await cursor.scalar(
        WALLET_TABLE.select(WALLET_TABLE.c.id == data["wallet"])
    ):
        raise HTTPException(status_code=404, detail="Wallet not found")
    return await cursor.one(
        TRANSACTION_TABLE.insert(data).returning(TRANSACTION_TABLE),
        commit=True,
    )
