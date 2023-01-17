# Gatask
:cat: Felina aplicación web utilizando FastAPI y Redis, gestiona tareas, subtareas y listas.

  `
    # Instalar FastAPI y Redis

    !pip install fastapi redis

    # Importar las librerías en el script

    from fastapi import FastAPI, HTTPException
    from fastapi.responses import JSONResponse
    from fastapi.encoders import jsonable_encoder
    from pydantic import BaseModel
    import redis

    # Crear y configurar una conexión a la base de datos Redis:

    # Crear una conexión a Redis
    r = redis.Redis(host='localhost', port=6379, db=0)

    # También podemos crear una función para inicializar la conexión con la base de datos y otra para cerrarla:

    def connect_to_db():
        r = redis.Redis(host='localhost', port=6379, db=0)
        return r

    def close_db(r):
        r.connection_pool.disconnect()

    # Ahora podemos utilizar estas funciones para conectarnos a la base de datos antes de realizar cualquier operación CRUD y cerrar la conexión después de terminar.

    # Crear los modelos de datos para las tareas y las listas, con las propiedades y validaciones necesarias:

    class Task(BaseModel):
        id: int
        name: str
        category: str
        subtasks: List[Task]

    class List(BaseModel):
        id: int
        name: str
        tasks: List[Task]

    class TaskCreate(Task):
        pass

    class TaskUpdate(Task):
        pass

    class ListCreate(List):
        pass

    class ListUpdate(List):
        pass

    # Crear las rutas y funciones de manejo de peticiones para las tareas y las listas, utilizando las funciones de CRUD de Redis para manipular los datos en la base de datos:

    @app.get("/tasks")
    def read_tasks():
        tasks = r.hgetall('tasks')
        return tasks

    # En cuanto a las funciones CRUD, podemos crear funciones para cada una de estas operaciones y utilizar las funciones de Redis correspondientes para realizarlas. Por ejemplo, para crear una tarea podríamos usar la función r.hmset() y para obtener una tarea, podríamos usar r.hgetall().

    # Aquí te dejo un ejemplo de cómo podría lucir la función para crear una tarea:

    @app.post("/tasks")
    def create_task(task: TaskCreate):

    # Use redis to insert the task in the database
    task_id = redis_client.incr("task_id")
    task_data = task.dict()
    task_data["id"] = task_id
      redis_client.hmset(f"task:{task_id}", task_data)

    # Add the task to the appropriate category list
      redis_client.lpush(f"category:{task.category}", task_id)

    # Return the task with the assigned id
    return {"id": task_id, **task_data}

    # Update an existing task
    @app.put("/tasks/{task_id}")
      def update_task(task_id: int, task: TaskUpdate):

    # Get the current task data
    current_task_data = redis_client.hgetall(f"task:{task_id}")
    if not current_task_data:
      raise HTTPException(status_code=404, detail="Task not found")

    # Update the task data
    current_task_data.update(task.dict())
      redis_client.hmset(f"task:{task_id}", current_task_data)

    # Update the category if needed
    current_category = current_task_data.get("category")
    if current_category != task.category:
      redis_client.lrem(f"category:{current_category}", 0, task_id)
      redis_client.lpush(f"category:{task.category}", task_id)
      return current_task_data

    # Delete an existing task
    @app.delete("/tasks/{task_id}")
    def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id=task_id)
    if task is None:
    raise HTTPException(status_code=404, detail="Task not found")
    crud.delete_task(db, task)
    return {"msg": "Task deleted"}

    # Get tasks by category
    @app.get("/tasks/category/{category}")
    def read_tasks_by_category(category: str, db: Session = Depends(get_db)):
    tasks = crud.get_tasks_by_category(db, category=category)
    return tasks

    # Update task category
    @app.put("/tasks/{task_id}/category/{category}")
    def update_task_category(task_id: int, category: str, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id=task_id)
    if task is None:
    raise HTTPException(status_code=404, detail="Task not found")
    task = crud.update_task_category(db, task, category)
    return task

    Get all lists
    @app.get("/lists")
    def read_lists(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    lists = crud.get_lists(db, skip=skip, limit=limit)
    return lists

    # Create a new list
    @app.post("/lists")
    def create_list(list: ListCreate, db: Session = Depends(get_db)):

    # Use the create_list function from the crud module to insert the new list into the database
    db_list = crud.create_list(db, list)

    # Return the created list with a 201 status code
    return JSONResponse(content=jsonable_encoder(db_list), status_code=201)

    # Update an existing list
    @app.put("/lists/{list_id}")
      def update_list(list_id: int, list: ListUpdate, db: Session = Depends(get_db)):

    # Use the update_list function from the crud module to update the list in the database
    db_list = crud.update_list(db, list_id, list)

    # Return the updated list
    return db_list

    # Delete an existing list
    @app.delete("/lists/{list_id}")
    def delete_list(list_id: int, db: Session = Depends(get_db)):

    # Use the delete_list function from the crud module to delete the list from the database
    crud.delete_list(db, list_id)

    # Return a 204 status code to indicate that the list was deleted
    return JSONResponse(status_code=204)

    # Create a new subtask
    @app.post("/tasks/{task_id}/subtasks")
    def create_subtask(task_id: int, subtask: SubtaskCreate):

    # Connect to redis
    r = redis.Redis(host='redis', port=6379)
    try:

    # Get the task from the database
    task_data = r.hgetall(f'task:{task_id}')
    if task_data:

    # Create the subtask and add it to the task's subtasks list
    subtask_data = subtask.dict()
    subtask_id = r.incr('subtask:id')
    subtask_data['id'] = subtask_id
    r.hmset(f'subtask:{subtask_id}', subtask_data)
    r.lpush(f'task:{task_id}:subtasks', subtask_id)
    return JSONResponse(content=subtask_data, status_code=201)
    else:
    raise HTTPException(status_code=404, detail="Task not found")
    except Exception as e:
    raise HTTPException(status_code=500, detail="An error occurred while creating the subtask")

    # Delete an existing subtask
    @app.delete("/tasks/{task_id}/subtasks/{subtask_id}")
    def delete_subtask(task_id: int, subtask_id: int, db: Session = Depends(get_db)):
    # Get the task that the subtask belongs to
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
    raise HTTPException(status_code=404, detail="Task not found")

    # Get the subtask to delete
    subtask = db.query(Task).filter(Task.id == subtask_id).first()
    if subtask is None:
        raise HTTPException(status_code=404, detail="Subtask not found")

    # Check that the subtask belongs to the task
    if subtask not in task.subtasks:
        raise HTTPException(status_code=400, detail="Subtask does not belong to task")

    # Delete the subtask
    task.subtasks.remove(subtask)
    db.delete(subtask)
    db.commit()
    return {"msg": "Subtask deleted"}
    Update an existing list
    @app.put("/lists/{list_id}")
    def update_list(list_id: int, list: ListUpdate, db: Session = Depends(get_db)):
    db_list = db.query(List).filter(List.id == list_id).first()
    if db_list is None:
    raise HTTPException(status_code=404, detail="List not found")
    update_data(db_list, list.dict(exclude_unset=True))
    db.commit()
    return db_list

    Delete an existing list
    @app.delete("/lists/{list_id}")
    def delete_list(list_id: int, db: Session = Depends(get_db)):
    db_list = db.query(List).filter(List.id == list_id).first()
    if db_list is None:
    raise HTTPException(status_code=404, detail="List not found")
    # Check that the list is not one of the main lists (planning, execution, completed, deleted)
    if db_list.name in ["planning", "execution", "completed", "deleted"]:
    raise HTTPException(status_code=400, detail="Cannot delete main lists")
    db.delete(db_list)
    db.commit()
    return {"msg": "List deleted"}
  `
Es importante notar que este ejemplo es solo una sugerencia y puede requerir adaptaciones para trabajar con su proyecto específico. Además, algunos de los métodos como `get_db` y `update_data` deben ser implementados adicionalmente. El uso de Redis en lugar de SQLAlchemy debería ser similar, pero con cambios en el código para acceder a la base de datos y realizar operaciones en ella. Se recomienda revisar la documentación de Redis y las librerías relacion
