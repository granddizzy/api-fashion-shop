import math

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import json
import os
from typing import Optional, List

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


@app.get("/catalog", response_class=JSONResponse)
async def get_products(
        category: Optional[str] = Query(None, description="Категория продукта"),
        brand: Optional[str] = Query(None, description="Бренд продукта"),
        designer: Optional[str] = Query(None, description="Дизайнер продукта"),
        trending_now: Optional[bool] = Query(None, description="Трендовый товар"),
        sort_by: Optional[int] = Query("title", description="Сортировать по: title, rating, price"),
        order: Optional[str] = Query("asc", description="Порядок сортировки: asc (по возрастанию), desc (по убыванию)"),
        page: Optional[int] = Query(1, description="Номер страницы"),
        limit: Optional[int] = Query(9, description="Количество элементов на странице"),
        size: Optional[List[str]] = Query(None, description="Фильтрация по размеру (например: S, M, L)"),
        type: Optional[str] = Query(None, description="Тип продукта (women, men, kids, accessories)"),
        min_price: Optional[float] = Query(None, description="Минимальная цена"),
        max_price: Optional[float] = Query(None, description="Максимальная цена")
):
    filtered_data = data

    # Фильтрация по категории
    if category:
        filtered_data = [item for item in filtered_data if item["category"].lower() == category.lower()]

    # Фильтрация по бренду
    if brand:
        filtered_data = [item for item in filtered_data if item["brand"].lower() == brand.lower()]

    # Фильтрация по дизайнеру
    if designer:
        filtered_data = [item for item in filtered_data if item["designer"].lower() == designer.lower()]

    # Фильтрация по трендовым товарам
    if trending_now is not None:
        filtered_data = [item for item in filtered_data if item.get("trending_now") == trending_now]

    # Фильтрация по размеру
    if size:
        filtered_data = [item for item in filtered_data if any(s in item['size'] for s in size)]

    # Фильтрация по типу
    if type:
        filtered_data = [item for item in filtered_data if item["type"].lower() == type.lower()]

    # Фильтрация по цене
    if min_price is not None:
        filtered_data = [item for item in filtered_data if item["price"] >= min_price]

    if max_price is not None:
        filtered_data = [item for item in filtered_data if item["price"] <= max_price]

    # Сортировка
    valid_sort_fields = ["title", "price"]
    if sort_by not in valid_sort_fields:
        sort_by = "title"

    filtered_data.sort(key=lambda x: x[sort_by], reverse=(order == "desc"))

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
async def get_product_by_id(
        id: Optional[int] = Query(None, description="ID продукта")
):
    product = next((item for item in data if item["id"] == id), None)
    if product is None:
        return JSONResponse(content={"message": "Product not found"}, status_code=404)
    return product


@app.get("/fetured", response_class=JSONResponse)
async def get_fetured_items():
    fetured_items = [item for item in data if item["fetured"]]
    if fetured_items is None:
        return JSONResponse(content={"message": "Items not found"}, status_code=404)
    return fetured_items
