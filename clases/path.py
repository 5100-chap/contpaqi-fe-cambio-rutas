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
        self.newBase = self.letterBase 
        self.__netPath = "\\\\localhost\\"
        self.__absPath = self.letterBase + self.basePath
    
    def indexCompanyName(self):
        # Retorna el índice donde empieza el nombre de empresa en una ruta
        # Ejemplo: "C:\Compacw\Empresas\00001234" → índice 21 (después de "Empresas\")
        return len(self.__absPath) + 1
    
    def build_netPath(self, hostname=None, netPath=None):
        """
        Construye la ruta de red, asegurando que siempre termine en 'Empresas'.
        
        Lógica:
        - Si netPath es None, usa basePath por defecto
        - Si netPath está definido, verifica que termine en 'Empresas'
        - Si no termina en 'Empresas', lo agrega
        """
        if hostname is not None:
            self.__netPath = f"\\\\{hostname}\\"
        
        if netPath is None:
            # Usar basePath por defecto
            self.__netPath = self.__netPath + self.basePath
        else:
            # Normalizar netPath
            clean_path = netPath.strip("\\/").replace("/", "\\")
            
            # Verificar si termina en 'Empresas'
            if not clean_path.lower().endswith("empresas"):
                # No termina en 'Empresas', agregarlo
                if clean_path:
                    self.__netPath = self.__netPath + clean_path + "\\Empresas"
                else:
                    self.__netPath = self.__netPath + "Empresas"
            else:
                # Ya termina en 'Empresas'
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
        Reemplaza la base de una ruta manteniendo la estructura relativa DESPUÉS de basePath.
        
        LÓGICA INTELIGENTE:
        1. Busca dónde está basePath en la ruta original
        2. Extrae todo lo que viene DESPUÉS de basePath
        3. Verifica si newBase ya termina con "Empresas"
        4. Construye la nueva ruta correctamente
        
        Ejemplos:
            Caso 1 - Compartida completa a compartida parcial:
            old: "\\\\VIEJO\\Compacw\\Empresas\\Empresa1\\Facturas"
            basePath: "Compacw\\Empresas"
            newBase: "\\\\NUEVO\\Empresas"
            
            → Encuentra "Compacw\\Empresas" en posición X
            → Extrae todo después: "\\Empresa1\\Facturas"
            → newBase ya termina en "Empresas" → usar directamente
            → Resultado: "\\\\NUEVO\\Empresas\\Empresa1\\Facturas"
            
            Caso 2 - Compartida parcial a compartida completa:
            old: "\\\\VIEJO\\Empresas\\Empresa1\\Facturas"
            basePath: "Compacw\\Empresas"
            newBase: "\\\\NUEVO\\Compacw\\Empresas"
            
            → Encuentra "Empresas" (parte de basePath) en posición X
            → Extrae todo después: "\\Empresa1\\Facturas"
            → newBase ya termina correctamente → usar directamente
            → Resultado: "\\\\NUEVO\\Compacw\\Empresas\\Empresa1\\Facturas"
        """
        # Normalizar entrada
        old = self._normalize(old_path)
        if not old:
            return old_path
        
        # Determinar base de destino
        target_base = new_base if new_base is not None else self.newBase
        target_base = target_base.rstrip("\\/")
        
        # Buscar basePath en la ruta original
        base_lower = self.basePath.lower()  # "compacw\\empresas"
        old_lower = old.lower()
        
        # Intentar encontrar el basePath completo
        idx = old_lower.find(base_lower)
        
        if idx == -1:
            # No se encontró basePath completo, intentar solo "empresas"
            empresas_lower = "empresas"
            idx = old_lower.find(empresas_lower)
            
            if idx != -1:
                # Encontró "empresas" - extraer desde ahí
                # Encontrar el final de "empresas"
                end_empresas = idx + len(empresas_lower)
                relative_part = old[end_empresas:].lstrip("\\/")
            else:
                # No se encontró nada, retornar sin cambios
                return old_path
        else:
            # Se encontró basePath completo
            # Extraer desde el FINAL de basePath
            end_base = idx + len(base_lower)
            relative_part = old[end_base:].lstrip("\\/")
        
        # Verificar si target_base ya termina con "Empresas"
        target_lower = target_base.lower()
        
        if target_lower.endswith("empresas"):
            # Ya termina con "Empresas", concatenar directamente
            new_path = target_base + "\\" + relative_part
        elif target_lower.endswith("compacw"):
            # Termina con "Compacw", agregar "\\Empresas"
            new_path = target_base + "\\Empresas\\" + relative_part
        elif target_base.endswith(":"):
            # Unidad de disco (C:), agregar basePath completo
            new_path = target_base + "\\" + self.basePath + "\\" + relative_part
        else:
            # Otro caso, agregar basePath completo
            new_path = target_base + "\\" + self.basePath + "\\" + relative_part
        
        # Normalizar múltiples barras
        if new_path.startswith("\\\\"):
            # Ruta UNC: mantener \\ inicial, eliminar duplicaciones
            new_path = "\\\\" + new_path[2:].replace("\\\\", "\\")
        else:
            # Ruta normal: eliminar dobles barras
            new_path = new_path.replace("\\\\", "\\")
        
        return new_path