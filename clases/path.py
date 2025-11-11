from pathlib import Path
class PathManager:
    def __init__(self, letterBase='C', tablePath=None, basePath="Compacw\\Empresas"):
        if tablePath is None:
            self.tablePath = [
                ("mgw10006.dbf", ["CFORMAPR01", "CREPIMPCFD", "CPLAMIGCFD", "CRUTAENT01"]),
                ("mgw10000.dbf", ["CRUTAPLA01", "CRUTAPLA02", "CRUTAENT01"])
            ]
        else:
            self.tablePath = tablePath
        self.basePath = basePath
        self.letterBase = letterBase.upper() + ":\\"
        self.newBase = self.letterBase
        self.__netPath = "\\\\localhost\\"
        self.__absPath = self.letterBase + basePath
    
    def indexCompanyName(self):
        return len(self.__absPath)

    def build_netPath(self, hostname=None, netPath=None):
        if netPath is None:
            self.__netPath = self.__netPath + self.basePath
        else:
            self.__netPath = self.__netPath + netPath
        if hostname is not None:
            self.__netPath = self.__netPath.replace("localhost", hostname, 1)

    def get_netPath(self) -> str:
        return self.__netPath

    def get_absPath(self) -> str:
        return self.__absPath
    
    def _normalize(self, p: str) -> str:
        if p is None:
            return ""
        return str(p).replace("/", "\\").strip()

    def change_path(self, old_path: str, new_base: str = None) -> str:
        
        old = self._normalize(old_path)
        if not old:
            return old_path

        target_base = new_base if new_base is not None else self.newBase
        idx = old.lower().find(self.basePath.lower())
        if idx != -1:
            # conservamos slash forward en new_base si new_base lo tiene
            suffix = old[idx:].lstrip("\\/")
            return str(Path(target_base.replace("/", "\\")) / suffix)
        return old_path

        # fallback
        return old
