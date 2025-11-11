# Contpaqi Factura Electrónica - Script para cambio de rutas (versión con clases)

Este script en **Python** esta diseñado para cambiar las rutas de todas las tablas y empresas en el sistema **Contpaqi Factura Electrónica**.

## Descripción General

En ocasiones, cuando se cambia un sistema **Contpaqi Factura Electrónica** de **modo local a red** (o viceversa), las rutas internas de las bases de datos DBF quedan configuradas con la ruta previa.

* Si solo existen unas pocas empresas, se pueden actualizar manualmente usando un gestor de DBF.
* Sin embargo, cuando existen **muchas empresas registradas**, este proceso manual se vuelve bastante tedioso y propenso a errores.
* Ademas puede resultar confuso editar dichos archivos para aquellos que no estan familiarizados con este tipo de archivos

Este script ayuda a automatiza el cambio de rutas, permitiendo que todas las tablas relevantes se actualicen de una forma rápida, flexible y consistente.

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

### Se recomienda fuertemente tener respaldos de las empresas, así como tener respaldada la carpeta Compacw antes de ejecutar el script

## Requisitos

Por el momento para poder correr el script se requiere de:

* [Python **3.9+**](https://www.python.org/downloads/windows/) *(Ultima version del script probada con Python 3.13.9)*
* Librería [`dbf`](https://pypi.org/project/dbf/)
* Librería [`tqdm`](https://pypi.org/project/tqdm/) (para la barra de progreso)
* Sistema Operativo Windows (7 - 11) *(Ultima version del script probada con Windows 10)*
* Al menos *200 MB* libres para el script + el espacio requerido por los paquetes para instalacion

Ademas **se requiere que todos los requisitos esten presentes en la computadora con Contpaqi Factura Electrónica que desea realizar los cambios**, de otra forma, el script fallará

### Requisitos opcionales

* [Git](https://github.com/git-for-windows/git/releases/latest)

## Instalación

Para descargar e instalar el script se puede usar el siguiente comando para obtener la versión mas reciente si se tiene instalado **Git**

```bash
git clone https://github.com/5100-chap/contpaqi-fe-cambio-rutas.git
```

O bien se puede descargar el [ZIP](https://github.com/5100-chap/contpaqi-fe-cambio-rutas/archive/refs/heads/main.zip) y descomprimir en el lugar de su preferencia.

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

4. Seguir las indicaciones para cambiar las rutas de manera satisfactoria

## Notas

Esta versión del script esta diseñada para ser lo mas flexible posible en cuanto a ubicacion de instalación de **Contpaqi Factura Electrónica**, asi que es recomendable entender previamente en donde esta instalado dicho programa, asi como la ubicación de los archivos y tener conocimiento básico de como se comparten las carpetas que se desean acceder dentro de la red si llegara a aplicar.

## IMPORTANTE

Este script **no es una herramienta oficial de CONTPAQi®**, fue desarrollado de manera independiente con fines de apoyo a ingenieros y/o soporte técnico que requieran este tipo de modificaciones. Úsalo bajo tu propia responsabilidad y **se reitera en realizar siempre un respaldo de tus bases de datos antes de ejecutar cualquier cambio**. El autor original, así como los autores y colaboradores de este script, no se hace responsable de pérdidas de información, mal uso o daños derivados de su aplicación.

## Licencia

Este proyecto está bajo la licencia **GPL v3** para garantizar que siempre sea **software libre y gratuito**.

Consulta el archivo [`LICENSE`](./LICENSE) para más información.
