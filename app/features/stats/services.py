import pickle
from pathlib import Path

# from app.resources.services import ModelQueryService

# from .models import Address, Transaction


class MigrationService:
    def __init__(self, address_query, transaction_query):
        self.address_query = address_query
        self.transaction_query = transaction_query

    def download(self, picked_file_path: Path):
        aggregated = pickle.loads(picked_file_path.read_bytes())
        for addr, data in aggregated:
            pass
            # address = self.address_query.create(
            #     Address.parse_obj({"hash": addr})
            # )
            # for maddr in data["moved"]:
            #     self.address_query.create(
            #         Address.parse_obj(
            #             {"hash": maddr, "received_from_id_id": address.id}
            #         )
            #     )

            # for tx, value in data["buys"]["WAVAX_txs"].items():
            #     self.transaction_query.create(
            #     )
