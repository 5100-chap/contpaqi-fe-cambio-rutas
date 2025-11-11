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
                table.open(mode=dbf.READ_WRITE)
                base_lower = path_manager.basePath.lower()

                for record in table:
                    with record as rec:
                        if collect_paths:
                            new_path = (rec["CRUTADATOS"] or "").strip()
                            idx = new_path.lower().find(base_lower)
                            if idx != -1:
                                suffix = new_path[idx:].replace("/", "\\").lstrip("\\/")
                                base = path_manager.newBase.replace("/", "\\").rstrip("\\/")
                                self.__results.append(f"{base}\\{suffix}")
        except FileNotFoundError:
            print(f"Archivo no encontrado: {table_path}")
        except dbf.DbfError as e:
            print(f"Error DBF en {table_path}: {e}")
        except Exception as e:
            print(f"Error inesperado en {table_path}: {e}")
        return self.__results
    
    def _get_field_len(table, col):
        # table.field_info(col) devuelve (type, length, decimals) en dbf 2.x
        ftype, flen, fdec = table.field_info(col)
        return flen
    
    def update_info(self, table_path: Path, columns: list, path_manager: PathManager) -> list:
        self.__changes = []
        try:
            with dbf.Table(str(table_path)) as table:
                table.open(mode=dbf.READ_WRITE)

                # Lista de campos existentes
                fields = set(table.field_names)

                # Pre-calcular longitudes
                lens = {col: _get_field_len(table, col) for col in columns if col in fields}

                for record in table:
                    with record as rec:
                        before = {}
                        after = {}
                        changed = False

                        for col in columns:
                            if col not in fields:
                                print(f"Columna {col} no encontrada en {table_path}")
                                continue

                            raw = rec[col]
                            original = (raw or "").strip()

                            updated = path_manager.change_path(original, new_base=path_manager.newBase)

                            # Truncar si excede la longitud del campo
                            maxlen = lens.get(col, None)
                            if maxlen is not None and updated is not None:
                                updated = updated[:maxlen]

                            before[col] = original
                            after[col] = updated

                            if updated != original:
                                rec[col] = updated
                                changed = True

                        if changed:
                            self.__changes.append({
                                "table": str(table_path),
                                "before": before,
                                "after": after
                            })
        except FileNotFoundError:
            print(f"Archivo no encontrado: {table_path}")
        except dbf.DbfError as e:
            print(f"Error DBF en {table_path}: {e}")
        except Exception as e:
            print(f"Error inesperado en {table_path}: {e}")
        return self.__changes