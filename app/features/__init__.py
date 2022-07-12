from dependency_injector import containers, providers

# from .stats.containers import StatsContainer


class FeaturesContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    resources = providers.DependenciesContainer()
    # stats: StatsContainer = providers.Container(
    #     StatsContainer, resources=resources, config=config.stats
    # )  # type: ignore
