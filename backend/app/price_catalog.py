PRICE_UPDATED_AT = "2026-04-05"

PRICE_CATALOG = {
    "Куриное филе": {"price": 330.0, "measure": "kg", "unit_label": "₽/кг"},
    "Рис": {"price": 80.0, "measure": "kg", "unit_label": "₽/кг"},
    "Лук": {"price": 35.0, "measure": "kg", "unit_label": "₽/кг"},
    "Масло": {"price": 130.0, "measure": "l", "unit_label": "₽/л"},
    "Гречка": {"price": 50.0, "measure": "kg", "unit_label": "₽/кг"},
    "Картофель": {"price": 35.0, "measure": "kg", "unit_label": "₽/кг"},
    "Сметана": {"price": 300.0, "measure": "kg", "unit_label": "₽/кг"},
    "Овощная смесь": {"price": 375.0, "measure": "kg", "unit_label": "₽/кг"},
    "Говядина": {"price": 850.0, "measure": "kg", "unit_label": "₽/кг"},
    "Морковь": {"price": 20.0, "measure": "kg", "unit_label": "₽/кг"},
    "Томатная паста": {"price": 500.0, "measure": "kg", "unit_label": "₽/кг"},
    "Свинина": {"price": 450.0, "measure": "kg", "unit_label": "₽/кг"},
    "Домашний фарш": {"price": 520.0, "measure": "kg", "unit_label": "₽/кг"},
    "Говяжий фарш": {"price": 650.0, "measure": "kg", "unit_label": "₽/кг"},
    "Капуста": {"price": 50.0, "measure": "kg", "unit_label": "₽/кг"},
    "Болгарский перец": {"price": 220.0, "measure": "kg", "unit_label": "₽/кг"},
    "Шампиньоны": {"price": 260.0, "measure": "kg", "unit_label": "₽/кг"},
    "Чечевица": {"price": 220.0, "measure": "kg", "unit_label": "₽/кг"},
    "Фасоль": {"price": 220.0, "measure": "kg", "unit_label": "₽/кг"},
    "Свекла": {"price": 45.0, "measure": "kg", "unit_label": "₽/кг"},
    "Огурец": {"price": 180.0, "measure": "kg", "unit_label": "₽/кг"},
    "Помидор": {"price": 220.0, "measure": "kg", "unit_label": "₽/кг"},
    "Огурец соленый": {"price": 180.0, "measure": "kg", "unit_label": "₽/кг"},
    "Кукуруза": {"price": 240.0, "measure": "kg", "unit_label": "₽/кг"},
    "Чеснок": {"price": 260.0, "measure": "kg", "unit_label": "₽/кг"},
}

MEAL_MODES = {
    "1": {"label": "1", "main_per_day": 1, "salad_per_day": 0},
    "1+salad": {"label": "1 + салат", "main_per_day": 1, "salad_per_day": 1},
    "2": {"label": "2", "main_per_day": 2, "salad_per_day": 0},
    "2+salad": {"label": "2 + салат", "main_per_day": 2, "salad_per_day": 1},
    "3": {"label": "3", "main_per_day": 3, "salad_per_day": 0},
    "3+salad": {"label": "3 + салат", "main_per_day": 3, "salad_per_day": 1},
}

def get_price_catalog_list():
    result = []
    for name, meta in PRICE_CATALOG.items():
        result.append({
            "name": name,
            "default_price": meta["price"],
            "measure": meta["measure"],
            "unit_label": meta["unit_label"],
        })
    return result

def ingredient_cost(name, quantity, unit, overrides=None):
    meta = PRICE_CATALOG.get(name)
    if not meta:
        return 0.0

    overrides = overrides or {}
    price = float(overrides.get(name, meta["price"]))
    measure = meta["measure"]

    quantity = float(quantity)
    unit = str(unit).strip().lower()

    if measure == "kg":
        if unit == "g":
            return round((quantity / 1000.0) * price, 2)
        if unit == "kg":
            return round(quantity * price, 2)

    if measure == "l":
        if unit == "ml":
            return round((quantity / 1000.0) * price, 2)
        if unit == "l":
            return round(quantity * price, 2)

    if measure == "pc":
        if unit == "pc":
            return round(quantity * price, 2)

    return 0.0
