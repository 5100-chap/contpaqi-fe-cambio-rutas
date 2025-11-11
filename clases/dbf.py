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
    
    def update_info(self, table_path: Path, columns: list, path_manager: PathManager) -> list:
        self.__changes = []
        try:
            with dbf.Table(str(table_path)) as table:
                table.open(mode=dbf.READ_WRITE)
                fields = set(table.field_names)

                for record in table:
                    with record as rec:
                        before = {}
                        after = {}
                        changed = False

                        for col in columns:
                            if col not in fields:
                                print(f"Columna {col} no encontrada en {table_path}")
                                continue

                            original = (rec[col] or "").strip()
                            updated = path_manager.change_path(original, new_base=path_manager.newBase)

                            before[col] = original
                            after[col] = updated

                            if updated != original:
                                try:
                                    # log antes de escribir
                                    print(f"[WRITE] Tabla: {table_path} - Registro: {table._current_record} - Campo: {col}")
                                    print(f"        Antes repr: {repr(original)}")
                                    print(f"        Intentando escribir repr: {repr(updated)}")
                                    rec[col] = updated
                                    # log justo después
                                    print(f"        OK escrito repr: {repr(rec[col])}")
                                    changed = True
                                except dbf.DbfError as e:
                                    print(f"Error al escribir {col} en {table_path}: {e}")
                                except Exception as e:
                                    print(f"Excepción inesperada al escribir {col} en {table_path}: {e}")

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
        try:
            with dbf.Table(str(table_path)) as t2:
                t2.open()
                
                for i, r in enumerate(t2):
                    if i >= 5: break
                    val = r[col] if col in r else None
                    print(f"[READBACK] Tabla: {table_path} - registro {i} - {col} repr: {repr(val)}")
        except Exception as e:
            print("Error readback:", e)
