from pathlib import Path
from tqdm import tqdm

from clases.dbf import DBFManager
from clases.path import PathManager

"""
Script para cambio de rutas en tablas DBF (Contpaqi).
Autor: Helker Hubbard
Modificado por 5100-chap
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


def main():
    tablas = DBFManager()
    type_selection = "0"
    server_name = str()
    server_route = str()

    print("Bienvenido al script para el cambio de ruta, primero necesitamos saber algunos datos")
    print("Si estos datos por defecto corresponden a su instalación favor de dar ENTER sin rellenar ningun campo")
    temp1 = str(input("Seleccione el disco en donde esta instalado Contpaqi Factura Electrónica sin los dos puntos ni los diagonales (:\\) (por defecto C): "))
    if (len(temp1.strip()) != 1):
        temp1 = None
    print("Seleccione la ruta en donde esta instalado Contpaqi Factura Electrónica sin la Unidad del Disco (C:\\) ")
    print("Por defecto el valor es \"Compacw\\Empresas\", a continuación se mostrara un ejemplo de como procesaria la ruta con los valores por defecto")
    temp2 = str(input(
        "Esto se veria reflejado dentro del script como \"C:\\Compacw\\Empresas\" donde C es la unidad definida previamente: "))
    if (len(temp2.strip()) == 0):
        temp2 = None
    else:
        # temp2 = repr(temp2)
        temp2 = temp2.replace("'", "").replace('"', "")
    if temp1 == None or temp2 == None:
        if temp2 == temp1:
            datosRutas = PathManager()
        elif temp1 == None:
            datosRutas = PathManager(basePath=temp2)
        elif temp2 == None:
            datosRutas = PathManager(letterBase=temp1)
    else:
        datosRutas = PathManager(letterBase=temp1, basePath=temp2)
    print("¿Cuál es el tipo de configuración que desea configurar?")
    print("[0]: local")
    print("[1]: red")
    type_selection = input("Seleccione una opción: ")

    if (type_selection == "1"):
        server_name = str(input("Ingrese el nombre del nuevo servidor (hostname o Direccion IP): "))
        print("Verifique que la ruta a apuntar en red sea la misma que la ruta donde esta instalado el Contpaqi")
        print("En dado caso de que sea asi, y usando valores predeterminados su ruta seria \"\\\\localhost\\Compacw\\Empresas\"")
        print("Donde localhost es el nombre del nuevo servidor que se definio previamente" )
        print("En dado caso de que NO sea asi, favor de configurar la ruta de red o de ENTER en caso de estar correcto: ")
        server_route = str(input("Formato esperado \"Ruta\\Subruta1\\Subruta2\\...\", Ruta actual \'" + str(datosRutas.basePath) + "\': "))
    if (len(server_name.strip()) == 0):
        print(("No ha introducido el nombre del servidor, s" if type_selection == "1" else "S") + "e configurará de manera local")
        datosRutas.build_netPath(netPath=server_route if (len(server_route.strip()) > 1) else None)
    else:
        datosRutas.build_netPath(hostname=server_name, netPath=server_route if (len(server_route.strip()) > 1) else None)
        datosRutas.newBase = datosRutas.get_netPath()
        
    # Paso 1: obtener todas las rutas de empresas (solo lectura)
    empresas = tablas.extract_info(
        Path(datosRutas.get_absPath() + "\\MGW00001.DBF"), path_manager=datosRutas, collect_paths=True)

    # Paso 2: actualizar tablas de cada empresa con barra de progreso y reporte de cambios
    total_cambios = 0
    with tqdm(empresas, desc="Procesando empresas", unit="empresa") as pbar:
        for i, empresa_path in enumerate(pbar, start=1):
            for name, cols in datosRutas.tablePath:
                pbar.set_description(
                    f"Empresa {i}: procesando {empresa_path[datosRutas.indexCompanyName():]}")
                table_file = Path(empresa_path) / name
                cambios = tablas.update_info(table_file, cols, datosRutas)
                total_cambios += len(cambios)

    print(f"Empresas procesadas con éxito. Cambios aplicados: {total_cambios}")

if __name__ == "__main__":
    main()
