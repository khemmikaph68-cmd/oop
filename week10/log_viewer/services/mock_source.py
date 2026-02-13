from typing import List
from week10.log_viewer.interfaces.data_source import ILogSource


class MockLogSource(ILogSource):
    def get_logs(self) -> List[str]:
        return [
            "[INFO] System started",
            "[WARN] Memory usage high",
            "[ERROR] Connection lost"
        ]