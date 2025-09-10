import dbf
from pathlib import Path
from tqdm import tqdm  # <- barra de progreso

"""
Script para cambio de rutas en tablas DBF (Contpaqi).
Autor: Helker Hubbard
Año: 2025

Este programa es software libre: puedes redistribuirlo y/o modificarlo 
bajo los términos de la Licencia Pública General de GNU publicada por la 
Free Software Foundation, ya sea la versión 3 de la Licencia, o 
(a tu elección) cualquier versión posterior.

Este programa se distribuye con la esperanza de que sea útil, 
pero SIN NINGUNA GARANTÍA; sin siquiera la garantía implícita de 
COMERCIABILIDAD o IDONEIDAD PARA UN PROPÓSITO PARTICULAR. 
Consulta la Licencia Pública General de GNU para más detalles.

Deberías haber recibido una copia de la Licencia Pública General de GNU
junto con este programa. En caso contrario, consulta <https://www.gnu.org/licenses/>.
"""


BASE_PATH = "Compacw\\Empresas"
INDEX_COMPANY_NAME = len("C:\\Compacw\\Empresas\\")

def change_path(old_path: str, new_base: str) -> str:
    """Reemplaza la ruta base si coincide con la definida."""
    if not old_path:
        return old_path
    idx = old_path.lower().find(BASE_PATH.lower())
    return str(Path(new_base) / old_path[idx:]) if idx != -1 else old_path

def process_table(table_path: Path, columns: list, new_base: str, collect_paths=False) -> list:
    """Abre una tabla DBF, actualiza columnas de ruta y opcionalmente devuelve rutas locales."""
    results = []
    try:
        with dbf.Table(str(table_path)) as table:
            table.open(mode=dbf.READ_WRITE)
            for record in table:
                with record as rec:  # type: ignore
                    for col in columns:
                        try:
                            rec[col] = change_path(rec[col].strip(), new_base)
                        except KeyError:
                            print(f"Columna {col} no encontrada en {table_path}")
                    if collect_paths:  # caso MGW00001
                        new_path = rec["CRUTADATOS"].strip()
                        idx = new_path.lower().find(BASE_PATH.lower())
                        if idx != -1:
                            results.append(str(Path("C:/") / new_path[idx:]))
    except FileNotFoundError:
        print(f"Archivo no encontrado: {table_path}")
    except dbf.DbfError as e:
        print(f"Error DBF en {table_path}: {e}")
    except Exception as e:
        print(f"Error inesperado en {table_path}: {e}")
    return results

def main():
    server_name = str()
    type_selection = "0"

    print("Cambio de rutas")
    print("opciones")
    print("[0]: local")
    print("[1]: red")
    type_selection = input("Seleccione una opción: ")

    new_base = r"C:/"

    if (type_selection == "1"):
        server_name = str(input("Ingrese el nombre del nuevo servidor: "))
        if(len(server_name.strip()) == 0): 
            print("No ha introducido el nombre del servidor, se configurará de manera local")
        else:
            server_path = r"\\" + server_name
            new_base = server_path.strip()

    # tablas relacionadas a cada empresa
    tables = [
        ("mgw10006.dbf", ["CFORMAPR01", "CREPIMPCFD", "CPLAMIGCFD", "CRUTAENT01"]),
        ("mgw10000.dbf", ["CRUTAPLA01", "CRUTAPLA02", "CRUTAENT01"])
    ]

    # Paso 1: obtener todas las rutas de empresas
    empresas = process_table(Path(r"C:\Compacw\Empresas\MGW00001.DBF"),
                             ["CRUTADATOS", "CRUTARES01"], new_base, collect_paths=True)

    # Paso 2: actualizar tablas de cada empresa con barra de progreso
    with tqdm(empresas, desc="Procesando empresas", unit="empresa") as pbar:
        for i, empresa_path in enumerate(pbar, start=1):
            for name, cols in tables:
                # 👉 Aquí actualizas la bandera sobre la barra
                pbar.set_description(f"Empresa {i}: procesando {empresa_path[INDEX_COMPANY_NAME:]}")
                # Ejemplo de tu lógica
                table_file = Path(empresa_path) / name
                process_table(table_file, cols, new_base)
    
    print("Empresas procesadas con éxito.")
    input()

if __name__ == "__main__":
    main()