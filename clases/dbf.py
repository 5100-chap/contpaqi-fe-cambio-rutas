from pathlib import Path
import dbf

class DBFManager:
    
    def __init__(self):
        self.__results = []
        self.__changes = []
    
    def extract_info(self, table_path: Path, path_manager, collect_paths: bool = False) -> list:
        """
        Extrae información de MGW00001.DBF (tabla maestra de empresas).
        
        IMPORTANTE: Siempre retorna rutas LOCALES para poder acceder a los archivos,
        independientemente de cómo estén configuradas en el DBF.
        
        Usa absPath (ruta local completa) como base para construir las rutas.
        """
        self.__results = []
        
        try:
            with dbf.Table(str(table_path)) as table:
                table.open(mode=dbf.READ_ONLY)
                
                for record in table:
                    if collect_paths:
                        # Obtener CRUTADATOS (ruta donde están los datos de la empresa)
                        ruta_datos = (record["CRUTADATOS"] or "").strip()
                        
                        if not ruta_datos:
                            continue
                        
                        # Normalizar
                        ruta_norm = ruta_datos.replace("/", "\\")
                        
                        # ESTRATEGIA: Buscar la parte relativa después de "Empresas"
                        # Ejemplo: "\\SERVIDOR\Compacw\Empresas\Empresa1" → "Empresa1"
                        
                        empresas_idx = ruta_norm.lower().rfind("empresas")
                        
                        if empresas_idx != -1:
                            # Encontró "Empresas", extraer lo que viene después
                            after_empresas = ruta_norm[empresas_idx + len("empresas"):].lstrip("\\/")
                            
                            # Construir ruta local usando absPath
                            # absPath = "C:\Compacw\Empresas"
                            # after_empresas = "Empresa1"
                            # Resultado: "C:\Compacw\Empresas\Empresa1"
                            ruta_local = path_manager.get_absPath() + "\\" + after_empresas
                            self.__results.append(ruta_local)
                        else:
                            # No encontró "Empresas", intentar usar la ruta como está
                            # si es absoluta
                            if ":\\" in ruta_norm or ruta_norm.startswith("\\\\"):
                                self.__results.append(ruta_norm)
                        
        except FileNotFoundError:
            print(f"Error: Archivo no encontrado: {table_path}")
        except dbf.DbfError as e:
            print(f"Error: Error DBF en {table_path}: {e}")
        except KeyError as e:
            print(f"Error: Columna no encontrada: {e}")
        except Exception as e:
            print(f"Error: Error inesperado: {e}")
        
        return self.__results
    
    def update_info(self, table_path: Path, columns: list, path_manager) -> list:
        """
        Actualiza columnas de tipo ruta en una tabla DBF.
        
        VERSIÓN ROBUSTA: Múltiples estrategias de escritura para asegurar persistencia.
        """
        self.__changes = []
        table = None
        
        try:
            # Estrategia: Abrir SIN context manager para control total
            table = dbf.Table(str(table_path))
            table.open(mode=dbf.READ_WRITE)
            
            # Obtener campos disponibles
            available_fields = set(table.field_names)
            
            # Iterar sobre registros
            record_index = 0
            for record in table:
                record_index += 1
                before = {}
                after = {}
                updates_to_apply = {}
                
                # FASE 1: Determinar qué cambiar
                for col in columns:
                    if col not in available_fields:
                        continue
                    
                    # Leer valor actual
                    try:
                        original = str(record[col] or "").strip()
                    except:
                        original = ""
                    
                    if not original:
                        continue
                    
                    # Transformar ruta
                    updated = path_manager.change_path(
                        original, 
                        new_base=path_manager.newBase
                    )
                    
                    # Registrar
                    before[col] = original
                    after[col] = updated
                    
                    # Solo si hay cambio real
                    if updated != original:
                        # Verificar longitud del campo
                        field_info = table.field_info(col)
                        max_len = field_info.length
                        
                        if len(updated) > max_len:
                            print(f"Advertencia:  Truncando {col}: {len(updated)} → {max_len} chars")
                            updated = updated[:max_len]
                            after[col] = updated
                        
                        updates_to_apply[col] = updated
                
                # FASE 2: Aplicar cambios si hay alguno
                if updates_to_apply:
                    try:
                        # MÉTODO 1: Context manager con asignación directa
                        with record as rec:
                            for col, value in updates_to_apply.items():
                                rec[col] = value
                        
                        # Registrar cambio exitoso
                        self.__changes.append({
                            "table": table_path.name,
                            "record": record_index,
                            "before": before,
                            "after": after
                        })
                        
                    except Exception as e1:
                        print(f"Advertencia:  Método 1 falló para registro {record_index}: {e1}")
                        
                        # MÉTODO 2: Scatter assignment (dbf alternativo)
                        try:
                            dbf.write(record, **updates_to_apply)
                            
                            self.__changes.append({
                                "table": table_path.name,
                                "record": record_index,
                                "before": before,
                                "after": after
                            })
                        except Exception as e2:
                            print(f"Error: Método 2 también falló: {e2}")
                            print(f"   Registro: {record_index}")
                            print(f"   Cambios intentados: {list(updates_to_apply.keys())}")
            
            # CRÍTICO: Cerrar explícitamente para flush
            print(f"\n💾 Cerrando tabla: {table_path.name}")
            table.close()
            print(f"✅ Tabla cerrada correctamente")
            
        except FileNotFoundError:
            print(f"Error: Archivo no encontrado: {table_path}")
        except dbf.DbfError as e:
            print(f"Error: Error DBF en {table_path}: {e}")
        except Exception as e:
            print(f"Error: Error inesperado en {table_path}: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Asegurar cierre incluso si hay error
            if table is not None:
                try:
                    if not table.status.closed:
                        table.close()
                except:
                    pass
        
        return self.__changes
    
    def get_detailed_log(self) -> str:
        """Genera un log detallado de todos los cambios realizados."""
        if not self.__changes:
            return "No se realizaron cambios."
        
        log_lines = []
        log_lines.append("\n" + "="*80)
        log_lines.append("DETALLE DE CAMBIOS REALIZADOS")
        log_lines.append("="*80)
        
        for i, change in enumerate(self.__changes, 1):
            log_lines.append(f"\n[Cambio #{i}] Archivo: {change['table']}")
            log_lines.append("-" * 80)
            
            for col in change['before'].keys():
                before = change['before'][col]
                after = change['after'][col]
                
                log_lines.append(f"  Campo: {col}")
                log_lines.append(f"    ANTES: {before}")
                log_lines.append(f"    AHORA: {after}")
        
        log_lines.append("\n" + "="*80)
        return "\n".join(log_lines)