# Contpaqi Factura Electrónica - Script para cambio de rutas

Este script en **Python** esta diseñado para cambiar las rutas de todas las tablas y empresas en el sistema **Contpaqi Factura Electrónica**.

## Descripción General

En ocasiones, cuando se cambia un sistema **Contpaqi Factura Electrónica** de **modo local a red** (o viceversa), las rutas internas de las bases de datos DBF quedan configuradas con la ruta previa.

* Si solo existen unas pocas empresas, se pueden actualizar manualmente usando un gestor de DBF.
* Sin embargo, cuando existen **muchas empresas registradas**, este proceso manual se vuelve tedioso y propenso a errores.

Este script ayuda a automatiza el cambio de rutas, permitiendo que todas las tablas relevantes se actualicen de una forma rápida y consistente.

## ¿Cómo afecta a las tablas y a los campos?

El script modifica las rutas en las siguientes tablas y columnas, basadas en la documentación oficial de **Contpaqi Factura Electrónica**:

### 🔹 Tabla `MGW10000` - Parámetros

| No. | Campo        | Tipo | Longitud | Descripción                                        |
| --- | ------------ | ---- | -------- | -------------------------------------------------- |
| 187 | `CRUTAPLA01` | C    | 253      | Ruta de la plantilla utilizada para visualizar CFD |
| 188 | `CRUTAPLA02` | C    | 253      | Ruta de la plantilla utilizada para visualizar CFD |
| 198 | `CRUTAENT01` | C    | 253      | Ruta de entrega por omisión para la empresa        |

### 🔹 Tabla `MGW10006` - Conceptos de documento

| No. | Campo        | Tipo | Longitud | Descripción                                                                        |
| --- | ------------ | ---- | -------- | ---------------------------------------------------------------------------------- |
| 11  | `CFORMAPR01` | C    | 253      | Ruta y nombre de la forma preimpresa para imprimir los documentos                  |
| 158 | `CREPIMPCFD` | C    | 253      | Ruta y nombre del archivo del reporte en formato de impresión                      |
| 176 | `CPLAMIGCFD` | C    | 253      | Ruta de la plantilla de formato amigable para entrega de CFD (exclusivo AdminPAQ®) |
| 185 | `CRUTAENT01` | C    | 253      | Ruta de entrega por omisión para el concepto                                       |

### 🔹 Tabla `MGW00001` - Empresas

| No. | Campo        | Tipo | Longitud | Descripción                    |
| --- | ------------ | ---- | -------- | ------------------------------ |
| 3   | `CRUTADATOS` | C    | 253      | Ruta de la empresa             |
| 4   | `CRUTARES01` | C    | 253      | Ruta de respaldo de la empresa |

## Requisitos

* Python **3.9+**
* Librería [`dbf`](https://pypi.org/project/dbf/)
* Librería [`tqdm`](https://pypi.org/project/tqdm/) (para la barra de progreso)

# Instalación:

En el ambiente de trabajo se debe de asegurar de tener instalado las librerias anteriormente mencionadas, pueden ser instaladas con:

```bash
pip install dbf tqdm
```

## Uso del script

1. Coloca el script en tu entorno local de trabajo, **el cual obligatoriamente debe de ser en donde esta instalado el servidor u el monousuario de Contpaqi Factura Electrónica**.
2. Abrir la terminal que se tenga por defecto *(Ejemplo: CMD, Powershell, Windows Terminal)* en donde esta los archivos del script o en su defecto ir a la carpeta donde esta el script con *cd*
3. Ejecutar el siguiente comando:

```bash
python main.py
```

4. Selecciona el tipo de configuración:

   * **\[0]** Local
   * **\[1]** Red

5. Si eliges red, deberás ingresar el nombre del servidor. **Asegurate de ejecutar el sistema sobre la computadora destinada a ser el servidor.**

## IMPORTANTE

Este script **no es una herramienta oficial de CONTPAQi®**, fue desarrollado de manera independiente con fines de apoyo a ingenieros de soporte técnico. Úsalo bajo tu propia responsabilidad y **realiza siempre un respaldo de tus bases de datos antes de ejecutar cualquier cambio**. El autor, asi como los colaboradores de este script, no se hace responsable de pérdidas de información, mal uso o daños derivados de su aplicación.

## Licencia

Este proyecto está bajo la licencia **GPL v3** para garantizar que siempre sea **software libre y gratuito**.

Consulta el archivo [`LICENSE`](./LICENSE) para más información.
