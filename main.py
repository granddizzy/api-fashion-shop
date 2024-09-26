import math

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import json
import os
from typing import Optional

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), 'data.json')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем запросы с этих доменов
    allow_credentials=True,  # Разрешаем отправку credentials (cookies, авторизация)
    allow_methods=["*"],  # Разрешаем все методы (GET, POST и т.д.)
    allow_headers=["*"],  # Разрешаем любые заголовки
)


def load_data():
    with open(DATA_FILE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


data = load_data()


def get_average_price(sizes):
    if not sizes:
        return 0
    total_price = sum(size['price'] for size in sizes)
    return total_price / len(sizes)


@app.get("/catalog", response_class=JSONResponse)
async def get_pizzas(
        # category: Optional[int] = Query(None, description="Категория продукта"),
        sort_by: Optional[int] = Query(None, description="Сортировать по: title, rating, price"),
        order: Optional[str] = Query("asc", description="Порядок сортировки: asc (по возрастанию), desc (по убыванию)"),
        page: Optional[int] = Query(1, description="Номер страницы"),
        limit: Optional[int] = Query(8, description="Количество элементов на странице")
):
    # Фильтрация по категории
    # if category is not None and category > 0:
    #     filtered_data = [pizza for pizza in data if category is None or pizza["category"] == category]
    # else:
    #     filtered_data = data

    filtered_data = data

    # Сортировка
    sort_fields = {
        # 0: "rating",  # Cортировка по популярности
        1: "price",  # Сортировка по цене
        2: "title"  # Сортировка по алфавиту
    }
    field_to_sort_by = sort_fields.get(sort_by)

    # if field_to_sort_by in {"title", "rating", "price"}:
    #     reverse_order = (order == "desc")
    #     filtered_data.sort(key=lambda x: x[field_to_sort_by], reverse=reverse_order)

    # if field_to_sort_by == "average_price":
    #     filtered_data.sort(key=lambda x: get_average_price(x["sizes"]), reverse=(order == "desc"))
    # elif field_to_sort_by in {"title", "rating"}:
    #     filtered_data.sort(key=lambda x: x[field_to_sort_by], reverse=(order == "desc"))

    filtered_data.sort(key=lambda x: x[field_to_sort_by], reverse=(order == "desc"))

    # Пагинация
    total_items = len(filtered_data)
    total_pages = math.ceil(total_items / limit)
    start = (page - 1) * limit
    end = start + limit
    paginated_data = filtered_data[start:end]

    return {
        "total": total_pages,
        "page": page,
        "limit": limit,
        "data": paginated_data
    }


@app.get("/product", response_class=JSONResponse)
async def get_pizza_by_id(
        id: Optional[int] = Query(None, description="ID продукта")
):
    product = next((item for item in data if item["id"] == id), None)
    if product is None:
        return JSONResponse(content={"message": "Product not found"}, status_code=404)
    return product


@app.get("/fetured", response_class=JSONResponse)
async def get_fetured_items():
    fetured_items = next((item for item in data if item["fetured"] == True), None)
    if fetured_items is None:
        return JSONResponse(content={"message": "Items not found"}, status_code=404)
    return fetured_items