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

    print("=" * 70)
    print("Bienvenido al script para el cambio de ruta en ContpaqiFácil")
    print("=" * 70)
    print("\nSi los datos por defecto corresponden a su instalación,")
    print("presione ENTER sin rellenar ningún campo.\n")
    
    # === CONFIGURACIÓN DE RUTA BASE ===
    temp1 = input("Disco de instalación (sin :\\) [por defecto C]: ").strip()
    if len(temp1) != 1:
        temp1 = None
    
    print("\nRuta de instalación (sin unidad de disco):")
    print("Por defecto: Compacw\\Empresas")
    print("Ejemplo: C:\\Compacw\\Empresas (donde C es la unidad anterior)")
    
    temp2 = input("Ruta: ").strip()
    if len(temp2) == 0:
        temp2 = None
    else:
        temp2 = temp2.replace("'", "").replace('"', "")
    
    # Crear PathManager con configuración
    if temp1 is None and temp2 is None:
        datosRutas = PathManager()
    elif temp1 is None:
        datosRutas = PathManager(basePath=temp2)
    elif temp2 is None:
        datosRutas = PathManager(letterBase=temp1)
    else:
        datosRutas = PathManager(letterBase=temp1, basePath=temp2)
    
    print(f"Ruta configurada: {datosRutas.get_absPath()}")
    
    # === CONFIGURACIÓN DE TIPO (LOCAL/RED) ===
    print("\n" + "=" * 70)
    print("¿Cuál es el tipo de configuración que desea aplicar?")
    print("[0]: Local (rutas C:\\...)")
    print("[1]: Red (rutas \\\\SERVIDOR\\...)")
    type_selection = input("Opción: ").strip()
    
    if type_selection == "1":
        print("\n--- CONFIGURACIÓN DE RED ---")
        server_name = input("Nombre del servidor (hostname o IP): ").strip()
        
        print("\nVerifique la ruta en red:")
        print(f"Ejemplo con valores actuales: \\\\{server_name or 'localhost'}\\{datosRutas.basePath}")
        print("\nSi la ruta en red es DIFERENTE, especifíquela.")
        print("Si es la misma, presione ENTER.")
        
        server_route = input(f"Ruta en red [actual: {datosRutas.basePath}]: ").strip()
    
    # === CONSTRUCCIÓN DE newBase (FIX CRÍTICO) ===
    if len(server_name) == 0:
        # MODO LOCAL
        print("Configurando en modo LOCAL")
        
        # En modo local, newBase es solo la letra de disco
        datosRutas.newBase = datosRutas.letterBase.rstrip("\\")
        print(f"   Base destino: {datosRutas.newBase}")
        
    else:
        # MODO RED
        print(f"Configurando en modo RED (servidor: {server_name})")
        
        # Construir ruta de red COMPLETA
        datosRutas.build_netPath(
            hostname=server_name, 
            netPath=server_route if len(server_route) > 1 else None
        )
        
        # CRÍTICO: En modo red, newBase debe ser SOLO el servidor
        # NO incluir basePath porque change_path lo agregará
        net_path_full = datosRutas.get_netPath()
        
        # Extraer solo \\SERVIDOR\ (sin basePath)
        if net_path_full.startswith("\\\\"):
            # Encontrar el final del nombre del servidor
            parts = net_path_full.split("\\")
            # parts = ['', '', 'SERVIDOR', 'Compacw', 'Empresas']
            if len(parts) >= 3:
                datosRutas.newBase = "\\\\" + parts[2]  # "\\SERVIDOR"
            else:
                datosRutas.newBase = net_path_full
        else:
            datosRutas.newBase = net_path_full
        
        print(f"   Servidor destino: {datosRutas.newBase}")
        print(f"   Ruta completa: {net_path_full}")
    
    print("\n" + "=" * 70)
    print("Iniciando procesamiento...")
    print("=" * 70)
    
    # === PASO 1: OBTENER RUTAS DE EMPRESAS ===
    print("Leyendo catálogo de empresas...")
    mgw_path = Path(datosRutas.get_absPath()) / "MGW00001.DBF"
    
    if not mgw_path.exists():
        print(f"ERROR: No se encontró {mgw_path}")
        print("   Verifique que la ruta de instalación sea correcta.")
        input("Presione ENTER para salir...")
        return
    
    empresas = tablas.extract_info(mgw_path, path_manager=datosRutas, collect_paths=True)
    
    if not empresas:
        print("No se encontraron empresas registradas.")
        input("\nPresione ENTER para salir...")
        return
    
    print(f"Se encontraron {len(empresas)} empresa(s)")
    
    # === PASO 2: PROCESAR CADA EMPRESA ===
    print("Actualizando rutas en tablas de empresas...\n")
    
    total_cambios = 0
    empresas_procesadas = 0
    empresas_con_errores = 0
    
    with tqdm(empresas, desc="Procesando", unit="empresa") as pbar:
        for i, empresa_path in enumerate(pbar, start=1):
            # Extraer nombre de empresa para mostrar
            nombre_empresa = empresa_path[datosRutas.indexCompanyName():]
            pbar.set_description(f"Empresa {i}/{len(empresas)}: {nombre_empresa}")
            
            empresa_ok = True
            
            for tabla_nombre, columnas in datosRutas.tablePath:
                tabla_path = Path(empresa_path) / tabla_nombre
                
                if not tabla_path.exists():
                    print(f"Archivo no encontrado: {tabla_path}")
                    empresa_ok = False
                    continue
                
                try:
                    cambios = tablas.update_info(tabla_path, columnas, datosRutas)
                    total_cambios += len(cambios)
                except Exception as e:
                    print(f"Error en {tabla_path}: {e}")
                    empresa_ok = False
            
            if empresa_ok:
                empresas_procesadas += 1
            else:
                empresas_con_errores += 1
    
    # === RESUMEN FINAL ===
    print("\n" + "=" * 70)
    print("RESUMEN DE PROCESAMIENTO")
    print("=" * 70)
    print(f"Empresas procesadas correctamente: {empresas_procesadas}")
    print(f"Empresas con errores:             {empresas_con_errores}")
    print(f"Total de cambios aplicados:        {total_cambios}")
    print("=" * 70)
    
    if total_cambios == 0:
        print("ADVERTENCIA: No se aplicaron cambios.")
        print("   Posibles causas:")
        print("   - Las rutas ya están configuradas correctamente")
        print("   - La configuración de origen/destino es la misma")
        print("   - Los archivos están vacíos o sin rutas configuradas")
    
    input("\nPresione ENTER para salir...")

if __name__ == "__main__":
    main()