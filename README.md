### Logica API

- Lógica API permite cargar archivos de manera asíncrona sin bloquear el hilo principal. -- Se basa en modelos de Pydantic para validar los datos, si el archivo cargado cumple con los requerimientos del modelo, es guardado en una base de datos de postgres, de lo contrario será catalogado como **Exception**.

- El endpoint **/api/inventory** en su método de petición **POST**, permite cargar un archivo, el cual es almacenado y puesto en cola usando registros en la base de datos. Luego, el servidor contesta al usuario, indicándole que el archivo fue cargado, sin embargo, esto no quiere decir que la información contenida en el mismo sea válida. Existe un método corriendo en un hilo, que comprueba los archivos pendientes por procesar y los válida.

**¿Por qué un archivo no es cargado?**

- Porque las columnas tienen nombres o datos que no corresponden. Recuerda que deben tener las siguientes columnas:

| FechaInventario | GLN_Cliente   | GLN_Sucursal  | Gtin_Producto | Inventario_Final | PrecioUnidad |
| --------------- | ------------- | ------------- | ------------- | ---------------- | ------------ |
| 28/03/2022      | 7711000000183 | 7701023999014 | 7708951417931 | 0                | 7731.09      |

- Porque los códigos de cliente, sucursal o producto, no están relacionados con un registro de los modelos **client**, **branch** o **product** respectivamente. Ya que estos códigos son llaves foráneas que se relacionan con estos modelos. Al iniciar la aplicación, el sistema carga datos de prueba mediante archivos **JSON**, puedes revisarlos en el directorio **data** del proyecto. También se incluyo un archivo de prueba con más de 1 millón de registros para que puedan probar el sistema. Notaran que mientras procesa el archivo pueden cargar otros, o consultar los datos subidos en el endpoint **/api/inventory** en su método de petición **GET**.

**Instalación**

La instalación es muy sencilla si cuentan con Docker instalado en el sistema, en ese caso pueden seguir los siguientes pasos.

1. Situarse en el directorio raíz del proyecto, donde se encuentra el archivo **Dockerfile**. Allí, abrimos una terminal y ejecutamos el comando: **docker build -t logica_api:1.0.0 .** importante la etiqueta **logica_api:1.0.0**, ya que así se referencia en el **docker-compose.yaml**.

2. Luego, abrimos el archivo **docker-compose.yaml** y cambiamos las rutas de los volúmenes. Para ello, buscamos la sección llamada "**volumes**" donde declaramos los volúmenes que queremos usar en los servicios, luego buscamos la opción **device** dentro del volumen **logica_data** que configura la ruta en el sistema host que se enlazará con el contenedor. En el caso del YAML, se está enlazando a la ruta "**C:/Users/Altergeist/Documents/data/db/logica**". Esta es la ruta que debes cambiar en tu máquina local. Recuerda que esta ruta ya debe existir en tu equipo, es decir, debes crear la carpeta para que se pueda enlazar con el volumen. De la misma manera, cambiamos la ruta en el volumen **logica_uploads**, que en el caso del YAML debe estar configurada con **C:/Users/Altergeist/Documents/data/uploads/logica**.

Una vez realices estos cambios específicos para tu equipo, debes correr el comando **docker compose up -d** en la raíz del proyecto. Docker, empezará a subir los servicios, puede tardar un momento dependiendo de la velocidad de descarga del internet, recuerda que la aplicación tarda un momento mientras carga los datos de prueba a la base de datos. Puedes mirar el estado ejecutando **docker logs logica_api**

Cuando la aplicación allá cargado por completo, puedes dirigirte a [http://localhost:8888/docs](http://localhost:8888/docs "http://localhost:8888/docs") donde verás la documentación de Swagger.
