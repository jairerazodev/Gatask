# Gatask
:cat: Felina aplicación web utilizando FastAPI, Redis y aioredis para gestionar tareas, subtareas y listas.

+ El código es una aplicación web basada en FastAPI que utiliza Redis como base de datos mediante el paquete aioredis.

+ Se importan las librerías necesarias, incluyendo FastAPI, aioredis y Pydantic para la creación de los modelos de datos.

+ Se crea una instancia de FastAPI y se definen dos funciones asíncronas "get_db" y "close_db" para obtener y cerrar la conexión con Redis respectivamente.

+ Se definen varios modelos de datos utilizando Pydantic, incluyendo "Task" y "List" para las tareas y listas respectivamente, y versiones "Create" y "Update" de estos modelos.

+ Se definen varias rutas para la aplicación web utilizando @app.get, @app.post, @app.put y @app.delete. Cada función tiene una dependencia en "get_db" para obtener una conexión a Redis.

+ Se utilizan las funciones asíncronas de aioredis para interactuar con Redis y obtener o actualizar datos. Además, se utilizan funciones personalizadas como "get_task", "get_tasks_by_category", "update_data" y "delete_data" para realizar operaciones específicas en Redis.

+ Finalmente, se define una ruta adicional para obtener todas las listas en Redis y se utiliza la función "close_db" para cerrar la conexión con Redis al finalizar la aplicación.
