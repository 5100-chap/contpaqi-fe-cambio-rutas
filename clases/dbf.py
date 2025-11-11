from pathlib import Path
import dbf

class DBFManager:
    
    def __init__(self):
        self.__results = []
        self.__changes = []
    
    def extract_info(self, table_path: Path, path_manager, collect_paths: bool = False) -> list:
        """
        Extrae información de MGW00001.DBF (tabla maestra de empresas).
        
        Retorna lista de rutas LOCALES donde están los archivos de cada empresa.
        Estas rutas se usan para abrir los archivos DBF de cada empresa.
        
        NO debe transformar usando newBase, solo construir rutas locales válidas.
        """
        self.__results = []
        
        try:
            with dbf.Table(str(table_path)) as table:
                table.open(mode=dbf.READ_ONLY)  # Solo lectura
                
                for record in table:
                    if collect_paths:
                        # Obtener CRUTADATOS (ruta donde están los datos de la empresa)
                        ruta_datos = (record["CRUTADATOS"] or "").strip()
                        
                        if not ruta_datos:
                            continue
                        
                        # Normalizar
                        ruta_norm = ruta_datos.replace("/", "\\")
                        
                        # Si la ruta ya es absoluta y válida, usarla directamente
                        # Ejemplo: "C:\Compacw\Empresas\00001234"
                        if ":\\" in ruta_norm or ruta_norm.startswith("\\\\"):
                            # Ya es una ruta absoluta
                            self.__results.append(ruta_norm)
                        else:
                            # Ruta relativa, construir desde letterBase
                            # Buscar donde empieza basePath
                            base_lower = path_manager.basePath.lower()
                            idx = ruta_norm.lower().find(base_lower)
                            
                            if idx != -1:
                                # Extraer desde basePath
                                relative = ruta_norm[idx:]
                                ruta_local = path_manager.letterBase + relative
                                self.__results.append(ruta_local)
                            else:
                                # No contiene basePath, asumir que es ruta completa
                                self.__results.append(ruta_norm)
                        
        except FileNotFoundError:
            print(f"ERROR: Archivo no encontrado: {table_path}")
        except dbf.DbfError as e:
            print(f"ERROR: Error DBF en {table_path}: {e}")
        except KeyError as e:
            print(f"ERROR: Columna no encontrada en {table_path}: {e}")
        except Exception as e:
            print(f"ERROR: Error inesperado en {table_path}: {e}")
        
        return self.__results
    
    def update_info(self, table_path: Path, columns: list, path_manager) -> list:
        """
        Actualiza columnas de tipo ruta en una tabla DBF.
        
        Transforma rutas de:
        - Local → Red: "C:\\...\\Formatos" → "\\\\SERVIDOR\\...\\Formatos"
        - Red → Local: "\\\\VIEJO\\...\\Formatos" → "C:\\...\\Formatos"
        - Red → Red: "\\\\VIEJO\\...\\Formatos" → "\\\\NUEVO\\...\\Formatos"
        
        Retorna lista de cambios realizados.
        """
        self.__changes = []
        
        try:
            with dbf.Table(str(table_path)) as table:
                table.open(mode=dbf.READ_WRITE)
                
                # Obtener nombres de campos disponibles
                available_fields = set(table.field_names)
                
                for record in table:
                    record_changed = False
                    before = {}
                    after = {}
                    
                    # Iniciar contexto de escritura
                    with record as rec:
                        for col in columns:
                            # Verificar que la columna existe
                            if col not in available_fields:
                                print(f"WARNING:  Columna '{col}' no encontrada en {table_path.name}")
                                continue
                            
                            # Obtener valor actual
                            original = (rec[col] or "").strip()
                            
                            # Si está vacío, no procesar
                            if not original:
                                continue
                            
                            # Transformar ruta usando newBase
                            updated = path_manager.change_path(
                                original, 
                                new_base=path_manager.newBase
                            )
                            
                            # Registrar valores (incluso si no hay cambio, para debug)
                            before[col] = original
                            after[col] = updated
                            
                            # Solo escribir si hay cambio REAL
                            if updated != original:
                                try:
                                    # CRÍTICO: Asignar el nuevo valor
                                    rec[col] = updated
                                    record_changed = True
                                    
                                except dbf.DataOverflowError as e:
                                    # El valor es más largo que el campo
                                    print(f"⚠️  Valor muy largo para {col} en {table_path.name}")
                                    
                                    # Truncar al tamaño máximo del campo
                                    field_info = table.field_info(col)
                                    max_len = field_info.length
                                    truncated = updated[:max_len]
                                    
                                    print(f"   Original: {updated}")
                                    print(f"   Truncado: {truncated}")
                                    
                                    rec[col] = truncated
                                    after[col] = truncated  # Actualizar el registro
                                    record_changed = True
                                    
                                except Exception as e:
                                    print(f"ERROR: Error al escribir {col} en {table_path.name}: {e}")
                    
                    # Registrar cambios si hubo modificaciones
                    if record_changed:
                        self.__changes.append({
                            "table": str(table_path),
                            "before": before,
                            "after": after
                        })
        
        except FileNotFoundError:
            print(f"ERROR: Archivo no encontrado: {table_path}")
        except dbf.DbfError as e:
            print(f"ERROR: Error DBF en {table_path}: {e}")
        except Exception as e:
            print(f"ERROR: Error inesperado en {table_path}: {e}")
        
        return self.__changes