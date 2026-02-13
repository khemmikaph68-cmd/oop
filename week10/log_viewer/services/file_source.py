from ast import List
from week10.log_viewer.interfaces.data_source import ILogSource


class FileLogSource(ILogSource):
    def __init__(self, filepath):
        self.filepath = filepath

    def get_logs(self) -> List[str]:
        try:
            with open(self.filepath, 'r') as f:
                return f.readlines()
        except FileNotFoundError:
            return ["Error: File not found"]