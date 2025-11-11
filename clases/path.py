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
        
        # Normalizar basePath (sin barras al inicio/final)
        self.basePath = basePath.strip("\\/").replace("/", "\\")
        
        self.letterBase = letterBase.upper() + ":\\"
        self.newBase = self.letterBase  # Por defecto: local
        self.__netPath = "\\\\localhost\\"
        self.__absPath = self.letterBase + self.basePath
    
    def indexCompanyName(self):
        # Retorna el índice donde empieza el nombre de empresa en una ruta
        # Ejemplo: "C:\Compacw\Empresas\00001234" → índice 21 (después de "Empresas\")
        return len(self.__absPath) + 1
    
    def build_netPath(self, hostname=None, netPath=None):
        """Construye la ruta de red."""
        if hostname is not None:
            self.__netPath = f"\\\\{hostname}\\"
        
        if netPath is None:
            self.__netPath = self.__netPath + self.basePath
        else:
            # Normalizar netPath
            clean_path = netPath.strip("\\/").replace("/", "\\")
            self.__netPath = self.__netPath + clean_path
    
    def get_netPath(self) -> str:
        return self.__netPath
    
    def get_absPath(self) -> str:
        return self.__absPath
    
    def _normalize(self, p: str) -> str:
        """Normaliza separadores a backslash."""
        if p is None or not p:
            return ""
        return str(p).replace("/", "\\").strip()
    
    def change_path(self, old_path: str, new_base: str = None) -> str:
        """
        Reemplaza la base de una ruta manteniendo la estructura relativa.
        
        IMPORTANTE: Solo reemplaza la parte ANTES de basePath, no duplica basePath.
        
        Ejemplos:
            1) Local → Red:
               old: "C:\\Compacw\\Empresas\\00001234\\Formatos"
               basePath: "Compacw\\Empresas"
               newBase: "\\\\SERVIDOR"
               → "\\\\SERVIDOR\\Compacw\\Empresas\\00001234\\Formatos"
            
            2) Red → Local:
               old: "\\\\VIEJO\\Compacw\\Empresas\\00001234\\Formatos"
               basePath: "Compacw\\Empresas"
               newBase: "C:"
               → "C:\\Compacw\\Empresas\\00001234\\Formatos"
        """
        # Normalizar entrada
        old = self._normalize(old_path)
        if not old:
            return old_path
        
        # Determinar base de destino
        target_base = new_base if new_base is not None else self.newBase
        
        # Buscar el punto donde empieza basePath
        base_lower = self.basePath.lower()
        old_lower = old.lower()
        
        idx = old_lower.find(base_lower)
        
        if idx == -1:
            # No se encontró basePath en la ruta → retornar sin cambios
            return old_path
        
        # Extraer DESDE basePath en adelante (incluyendo basePath)
        # Ejemplo: "C:\Compacw\Empresas\00001234" → "Compacw\Empresas\00001234"
        relative_part = old[idx:]
        
        # Limpiar target_base de barras finales
        target_clean = target_base.rstrip("\\/")
        
        # Casos especiales según el tipo de target_base
        if target_clean.endswith(":"):
            # Unidad de disco: "C:" → "C:\..."
            new_path = target_clean + "\\" + relative_part
        elif target_clean.startswith("\\\\"):
            # Ruta UNC: "\\SERVIDOR" → "\\SERVIDOR\..."
            new_path = target_clean + "\\" + relative_part
        else:
            # Otra ruta: "D:\MiCarpeta" → "D:\MiCarpeta\..."
            new_path = target_clean + "\\" + relative_part
        
        # Normalizar múltiples barras (pero preservar \\ inicial en rutas UNC)
        if new_path.startswith("\\\\"):
            # Ruta UNC: mantener \\ inicial, eliminar triplicaciones
            new_path = "\\\\" + new_path[2:].replace("\\\\", "\\")
        else:
            # Ruta normal: eliminar dobles barras
            new_path = new_path.replace("\\\\", "\\")
        
        return new_path