from pathlib import Path
from tqdm import tqdm

from clases.dbf import DBFManager
from clases.path import PathManager


"""
Script para cambio de rutas en tablas DBF (Contpaqi): Versión con clases 0.8.
Autor del Script Base: Helker Hubbard
Autor de esta versión modificada: 5100-chap
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
    print("Bienvenido al script para el cambio de ruta en Contpaqi Factura Electronica")
    print("=" * 70)
    print("\nSi los datos por defecto corresponden a su instalación,")
    print("presione ENTER sin rellenar ningún campo.\n")
    
    # === CONFIGURACIÓN DE RUTA BASE ===
    temp1 = input("Definiri unidad de disco (sin :\\) [por defecto: C]: ").strip()
    if len(temp1) != 1:
        temp1 = None
    
    print("\nDefine la ruta de instalación (sin unidad de disco):")
    print("Por defecto: Compacw\\Empresas")
    print("Ejemplo de contrucción con valores predeterminados: C:\\Compacw\\Empresas (donde C es la unidad anteriormente definida)")
    
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
    
    print(f"Ruta absoluta construida: {datosRutas.get_absPath()}")
    
    # === CONFIGURACIÓN DE TIPO (LOCAL/RED) ===
    print("\n" + "=" * 70)
    print("¿Cuál es el tipo de configuración que desea aplicar?")
    print("[0]: Local (C:\\...)")
    print("[1]: Red (\\\\SERVIDOR\\...)")
    type_selection = input("Eliga su opción [Por defecto: 0]: ").strip()
    
    if type_selection == "1":
        print("\n--- CONFIGURACIÓN DE RED ---")
        server_name = input("Nombre del servidor (hostname o IP): ").strip()
        
        print("Verifique la ruta en red:")
        print(f"Ejemplo con valores actuales: \\\\{server_name or 'localhost'}\\{datosRutas.basePath}")
        print("Si la ruta en red es DIFERENTE, especifíquela.")
        print("Si es la misma, presione ENTER.")
        
        server_route = input(f"Ruta en red [actual: {datosRutas.basePath}]: ").strip()
    
    # === CONSTRUCCIÓN DE newBase ===
    if len(server_name) == 0:
        # MODO LOCAL
        print(str("Advertencia: Nombre del servidor no definido, cambiando a" if type_selection == '1' else "Configurando en") + " modo LOCAL")
        
        # En modo local, newBase es solo la letra de disco
        datosRutas.newBase = datosRutas.letterBase.rstrip("\\")
        print(f"Base destino: {datosRutas.newBase}")
        
    else:
        # MODO RED
        print(f"Configurando en modo RED (servidor: {server_name})")
        
        # Construir ruta de red (build_netPath ya maneja la lógica de "Empresas")
        datosRutas.build_netPath(
            hostname=server_name, 
            netPath=server_route if len(server_route) > 1 else None
        )
        
        # newBase es la ruta de red completa hasta "Empresas"
        # Esto es correcto porque change_path extraerá la parte DESPUÉS de "Empresas"
        datosRutas.newBase = datosRutas.get_netPath()
        
        print(f"Base destino: {datosRutas.newBase}")
        
        # Verificar estructura
        if datosRutas.newBase.lower().endswith("empresas"):
            print(f"La ruta termina correctamente en 'Empresas'")
        else:
            print(f"Advertencia: La ruta no termina en 'Empresas'")
            print(f"Esto puede causar rutas incorrectas")
    
    print("\n" + "=" * 70)
    print("Iniciando procesamiento...")
    print("=" * 70)
    
    # === PASO 1: OBTENER RUTAS DE EMPRESAS ===
    print("Leyendo catálogo de empresas...")
    mgw_path = Path(datosRutas.get_absPath()) / "MGW00001.DBF"
    
    if not mgw_path.exists():
        print(f"ERROR: No se encontró {mgw_path}")
        print("   Verifique que la ruta de instalación sea correcta.")
        input("\nPresione ENTER para salir...")
        return
    
    empresas = tablas.extract_info(mgw_path, path_manager=datosRutas, collect_paths=True)
    
    if not empresas:
        print("No se encontraron empresas registradas.")
        input("\nPresione ENTER para salir...")
        return
    
    print(f"Se encontraron {len(empresas)} empresa(s)")
    
    # === PASO 1.5: ACTUALIZAR MGW00001.DBF (TABLA MAESTRA) ===
    print("Actualizando catálogo principal de empresas (MGW00001.DBF)...")
    
    cambios_catalogo = tablas.update_info(
        mgw_path,
        ["CRUTADATOS", "CRUTARES01"],
        datosRutas
    )
    
    if cambios_catalogo:
        print(f"Catálogo actualizado: {len(cambios_catalogo)} cambio(s)")
        print("\nDetalle de cambios en catálogo:")
        for cambio in cambios_catalogo[:3]:
            print(f"\n  Registro #{cambio.get('record', '?')}:")
            for col in cambio['before'].keys():
                before = cambio['before'][col][:60] + "..." if len(cambio['before'][col]) > 60 else cambio['before'][col]
                after = cambio['after'][col][:60] + "..." if len(cambio['after'][col]) > 60 else cambio['after'][col]
                print(f"    {col}:")
                print(f"      Antes: {before}")
                print(f"      Ahora: {after}")
        
        if len(cambios_catalogo) > 3:
            print(f"  ... y {len(cambios_catalogo) - 3} cambio(s) más")
    else:
        print("No se realizaron cambios en el catálogo (las rutas ya están actualizadas)")
    
    # === PASO 2: PROCESAR CADA EMPRESA ===
    print("Actualizando rutas en tablas de empresas...\n")
    
    total_cambios = 0
    empresas_procesadas = 0
    empresas_con_errores = 0
    
    # Log detallado de cada empresa
    cambios_por_empresa = []
    
    with tqdm(empresas, desc="Procesando", unit="empresa", disable=False) as pbar:
        for i, empresa_path in enumerate(pbar, start=1):
            # Extraer nombre de empresa
            nombre_empresa = empresa_path[datosRutas.indexCompanyName():]
            pbar.set_description(f"[{i}/{len(empresas)}] {nombre_empresa}")
            
            empresa_ok = True
            cambios_empresa = []
            
            for tabla_nombre, columnas in datosRutas.tablePath:
                tabla_path = Path(empresa_path) / tabla_nombre
                
                if not tabla_path.exists():
                    print(f"{nombre_empresa}: {tabla_nombre} no encontrado")
                    empresa_ok = False
                    continue
                
                try:
                    # Procesar tabla
                    cambios = tablas.update_info(tabla_path, columnas, datosRutas)
                    
                    if cambios:
                        cambios_empresa.extend(cambios)
                        total_cambios += len(cambios)
                        
                        # Mostrar resumen de cambios en esta tabla
                        print(f"{nombre_empresa}/{tabla_nombre}: {len(cambios)} cambio(s)")
                    
                except Exception as e:
                    print(f"Error en {nombre_empresa}/{tabla_nombre}: {e}")
                    empresa_ok = False
            
            if empresa_ok:
                empresas_procesadas += 1
                if cambios_empresa:
                    cambios_por_empresa.append({
                        "empresa": nombre_empresa,
                        "path": empresa_path,
                        "cambios": cambios_empresa
                    })
            else:
                empresas_con_errores += 1
    
    # === RESUMEN FINAL ===
    print("\n" + "=" * 70)
    print("RESUMEN DE PROCESAMIENTO")
    print("=" * 70)
    print(f"Cambios en catálogo (MGW00001):   {len(cambios_catalogo)}")
    print(f"Empresas procesadas correctamente: {empresas_procesadas}")
    print(f"Empresas con errores:             {empresas_con_errores}")
    print(f"Total de cambios en empresas:      {total_cambios}")
    print(f"TOTAL GENERAL DE CAMBIOS:          {len(cambios_catalogo) + total_cambios}")
    print("=" * 70)
    
    if len(cambios_catalogo) + total_cambios == 0:
        print("ADVERTENCIA: No se aplicaron cambios.")
        print("   Posibles causas:")
        print("   - Las rutas ya están configuradas correctamente")
        print("   - La configuración de origen/destino es la misma")
        print("   - Los archivos están vacíos o sin rutas configuradas")
        print("Sugerencia: Use el script de debug para inspeccionar los DBF")
    else:
        # Mostrar resumen por empresa
        print("\n" + "=" * 70)
        print("DETALLE DE CAMBIOS")
        print("=" * 70)
        
        # Mostrar cambios en catálogo primero
        if cambios_catalogo:
            print("CATÁLOGO PRINCIPAL (MGW00001.DBF)")
            print("=" * 70)
            for i, cambio in enumerate(cambios_catalogo, 1):
                print(f"\n[Empresa #{i}] Registro: {cambio.get('record', '?')}")
                for col in cambio['before'].keys():
                    before = cambio['before'][col]
                    after = cambio['after'][col]
                    
                    before_short = before[:50] + "..." if len(before) > 50 else before
                    after_short = after[:50] + "..." if len(after) > 50 else after
                    
                    print(f"{col}:")
                    print(f"Antes: {before_short}")
                    print(f"Ahora: {after_short}")
        
        # Mostrar cambios por empresa
        if cambios_por_empresa:
            print("\n" + "=" * 70)
            print("TABLAS DE CADA EMPRESA (mgw10006.dbf, mgw10000.dbf)")
            print("=" * 70)
            
            for emp_info in cambios_por_empresa:
                print(f"{emp_info['empresa']}")
                print(f"Ruta: {emp_info['path']}")
                print(f"Cambios: {len(emp_info['cambios'])}")
            
            # Mostrar primeros cambios como ejemplo
            for i, cambio in enumerate(emp_info['cambios'][:2], 1):
                print(f"\n   Cambio #{i} en {cambio['table']}:")
                for col in cambio['before'].keys():
                    before = cambio['before'][col]
                    after = cambio['after'][col]
                    
                    # Truncar si es muy largo
                    before_short = before[:50] + "..." if len(before) > 50 else before
                    after_short = after[:50] + "..." if len(after) > 50 else after
                    
                    print(f"{col}:")
                    print(f"Antes: {before_short}")
                    print(f"Ahora: {after_short}")
            
            if len(emp_info['cambios']) > 2:
                print(f"   ... y {len(emp_info['cambios']) - 2} cambio(s) más")
        
        # Opción de guardar log completo
        print("\n" + "=" * 70)
        print("¿Guardar log completo en archivo? (s/N): ", end="")
        guardar = input().strip().lower()
        
        if guardar in ['s', 'si', 'sí', 'yes', 'y']:
            log_file = Path("cambios_rutas.log")
            
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("LOG DE CAMBIOS - CONTPAQi Facturación Electrónica\n")
                f.write("="*80 + "\n\n")
                
                # Catálogo principal
                if cambios_catalogo:
                    f.write("="*80 + "\n")
                    f.write("CATÁLOGO PRINCIPAL DE EMPRESAS (MGW00001.DBF)\n")
                    f.write("="*80 + "\n\n")
                    
                    for i, cambio in enumerate(cambios_catalogo, 1):
                        f.write(f"[Empresa #{i}] Registro: {cambio.get('record', '?')}\n")
                        f.write("-" * 80 + "\n")
                        
                        for col in cambio['before'].keys():
                            f.write(f"  Campo: {col}\n")
                            f.write(f"    ANTES: {cambio['before'][col]}\n")
                            f.write(f"    AHORA: {cambio['after'][col]}\n")
                        f.write("\n")
                
                # Tablas de empresas
                for emp_info in cambios_por_empresa:
                    f.write(f"\n{'='*80}\n")
                    f.write(f"EMPRESA: {emp_info['empresa']}\n")
                    f.write(f"RUTA: {emp_info['path']}\n")
                    f.write(f"{'='*80}\n\n")
                    
                    for i, cambio in enumerate(emp_info['cambios'], 1):
                        f.write(f"[Cambio #{i}] Archivo: {cambio['table']}\n")
                        f.write(f"  Registro: {cambio.get('record', '?')}\n")
                        f.write("-" * 80 + "\n")
                        
                        for col in cambio['before'].keys():
                            f.write(f"  Campo: {col}\n")
                            f.write(f"    ANTES: {cambio['before'][col]}\n")
                            f.write(f"    AHORA: {cambio['after'][col]}\n")
                        f.write("\n")
            
            print(f"Log guardado en: {log_file.absolute()}")
    
    input("\nPresione ENTER para salir...")

if __name__ == "__main__":
    main()