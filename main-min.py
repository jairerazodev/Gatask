import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import aioredis

app = FastAPI()

async def get_db():
    redis = await aioredis.create_redis_pool(('localhost', 6379), db=0)
    return redis

async def close_db(redis):
    redis.close()
    await redis.wait_closed()

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

@app.get("/tasks")
async def read_tasks(redis: aioredis.Redis = Depends(get_db)):
    tasks = await redis.hgetall('tasks')
    return tasks

@app.post("/tasks")
async def create_task(task: TaskCreate, redis: aioredis.Redis = Depends(get_db)):
    task_id = await redis.incr("task_id")
    task_data = task.dict()
    task_data["id"] = task_id
    await redis.hmset_dict(f"task:{task_id}", task_data)
    await redis.lpush(f"category:{task.category}", task_id)
    return {"id": task_id, **task_data}

@app.put("/tasks/{task_id}")
async def update_task(task_id: int, task: TaskUpdate, redis: aioredis.Redis = Depends(get_db)):
    current_task_data = await redis.hgetall(f"task:{task_id}")
    if not current_task_data:
        raise HTTPException(status_code=404, detail="Task not found")
    current_task_data.update(task.dict())
    await redis.hmset_dict(f"task:{task_id}", current_task_data)
    current_category = current_task_data.get("category")
    if current_category != task.category:
        await redis.lrem(f"category:{current_category}", 0, task_id)
        await redis.lpush(f"category:{task.category}", task_id)
    return current_task_data

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int, redis: aioredis.Redis = Depends(get_db)):
    task = await get_task(redis, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    await delete_data(redis, task_id)
    return {"msg": "Task deleted"}

@app.get("/tasks/category/{category}")
async def read_tasks_by_category(category: str, redis: aioredis.Redis = Depends(get_db)):
    tasks = await get_tasks_by_category(redis, category)
    return tasks

@app.put("/tasks/{task_id}/category/{category}")
async def update_task_category(task_id: int, category: str, redis: aioredis.Redis = Depends(get_db)):
    task = await get_task(redis, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task = await update_data(redis, task_id, category)
    return task

@app.get("/lists")
async def read_lists(skip: int = 0, limit: int = 100, redis: aioredis.Redis = Depends(get_db)):
    lists = await get_lists(redis, skip, limit)
    return lists

async def get_task(redis, task_id):
    task = await redis.hgetall(f"task:{task_id}")
    if task:
        return task
    return None

async def get_tasks_by_category(redis, category):
    task_ids = await redis.lrange(f"category:{category}", 0, -1)
    tasks = []
    for task_id in task_ids:
        task = await redis.hgetall(f"task:{task_id}")
        tasks.append(task)
    return tasks

async def update_data(redis, task_id, category):
    task = await redis.hgetall(f"task:{task_id}")
    if task:
        task["category"] = category
        await redis.hmset_dict(f"task:{task_id}", task)
        return task
    return None

async def delete_data(redis, task_id):
    task = await redis.hgetall(f"task:{task_id}")
    if task:
        await redis.delete(f"task:{task_id}")
        await redis.lrem(f"category:{task['category']}", 0, task_id)

async def get_lists(redis, skip, limit):
    lists = await redis.lrange("lists", skip, skip + limit - 1)
    return lists


async def get_db():
    redis = await aioredis.create_redis_pool(('localhost', 6379), db=0)
    return redis

async def get_task(redis, task_id):
    task = await redis.hgetall(f"task:{task_id}")
    if task:
        return task
    return None

async def get_tasks_by_category(redis, category):
    task_ids = await redis.lrange(f"category:{category}", 0, -1)
    tasks = []
    for task_id in task_ids:
        task = await redis.hgetall(f"task:{task_id}")
        tasks.append(task)
    return tasks

async def update_data(redis, task_id, category):
    task = await redis.hgetall(f"task:{task_id}")
    if task:
        task["category"] = category
        await redis.hmset_dict(f"task:{task_id}", task)
        return task
    return None

async def delete_data(redis, task_id):
    task = await redis.hgetall(f"task:{task_id}")
    if task:
        await redis.delete(f"task:{task_id}")
        await redis.lrem(f"category:{task['category']}", 0, task_id)

async def get_lists(redis, skip, limit):
    lists = await redis.lrange("lists", skip, skip + limit - 1)
    return lists

async def close_db(redis):
    redis.close()
    await redis.wait_closed()
