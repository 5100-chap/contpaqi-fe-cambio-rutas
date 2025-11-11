from pathlib import Path
import dbf
from clases.path import PathManager

class DBFManager:
    
    def __init__(self):
        self.__results =  []
        self.__changes = []
    
    def extract_info(self, table_path: Path, path_manager:PathManager, collect_paths: bool = False) -> list:
        """
        Abre una tabla DBF y extrae información.
        - Si collect_paths=True, devuelve rutas locales transformadas desde CRUTADATOS.
        - Si collect_paths=False, devuelve una lista vacía (extensible para otros casos de lectura).
        """
        self.__results = []
        try:
            with dbf.Table(str(table_path)) as table:
                table.open(mode=dbf.READ_WRITE)  # mantenemos modo RW para consistencia con el original
                for record in table:
                    with record as rec:  # type: ignore
                        if collect_paths:  # caso MGW00001
                            new_path = rec["CRUTADATOS"].strip()
                            idx = new_path.lower().find(path_manager.basePath.lower())
                            if idx != -1:
                                self.__results.append(str(Path(path_manager.newBase) / new_path[idx:]))
        except FileNotFoundError:
            print(f"Archivo no encontrado: {table_path}")
        except dbf.DbfError as e:
            print(f"Error DBF en {table_path}: {e}")
        except Exception as e:
            print(f"Error inesperado en {table_path}: {e}")
        return self.__results
    
    def update_info(self, table_path: Path, columns: list, path_manager: PathManager) -> list:
        """
        Abre una tabla DBF, actualiza columnas de ruta y devuelve un reporte de cambios.
        Reporte por registro:
        { "before": {col: valor_original}, "after": {col: valor_actualizado} }
        Solo incluye registros donde hubo cambios efectivos.
        """
        self.__changes = []
        try:
            with dbf.Table(str(table_path)) as table:
                table.open(mode=dbf.READ_WRITE)
                for record in table:
                    with record as rec:  # type: ignore
                        before = {}
                        after = {}
                        changed = False
                        for col in columns:
                            try:
                                raw = rec[col] if col in rec else None
                                original = (raw or "").strip()
                                # Sustituimos usando path_manager
                                updated = path_manager.change_path(original, new_base=path_manager.newBase)
                                before[col] = original
                                after[col] = updated
                                if updated != original:
                                    rec[col] = updated
                                    changed = True
                            except KeyError:
                                print(f"Columna {col} no encontrada en {table_path}")
                        if changed:
                            self.__changes.append({"table": str(table_path), "before": before, "after": after})
        except FileNotFoundError:
            print(f"Archivo no encontrado: {table_path}")
        except dbf.DbfError as e:
            print(f"Error DBF en {table_path}: {e}")
        except Exception as e:
            print(f"Error inesperado en {table_path}: {e}")
        return self.__changes