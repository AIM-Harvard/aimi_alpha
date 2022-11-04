from Config import Instance
from .DataConverter import DataConverter

class DsegConverter(DataConverter):
    def convert(self, instance: Instance) -> None:
        return super().convert(instance)