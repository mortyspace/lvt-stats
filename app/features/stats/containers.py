from dependency_injector import containers, providers

from app.resources.containers import ResourcesContainer

from . import API

# from .models import Address, Transaction
# from .services import MigrationService
# from .tables import TRANSACTION_TABLE, WALLET_TABLE


class StatsContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    api = providers.Object(API)
    resources: ResourcesContainer = providers.DependenciesContainer(
        db=providers.DependenciesContainer()
    )  # type: ignore

    # address_query = providers.Factory(
    #     ModelQueryService, resources.db.connection, WALLET_TABLE, Address
    # )
    # transaction_query = providers.Factory(
    #     ModelQueryService,
    #     resources.db.connection,
    #     TRANSACTION_TABLE,
    #     Transaction,
    # )

    # migration = providers.Factory(
    #     MigrationService, address_query, transaction_query
    # )
