import re
import httpx

THEMEALDB_BASE = "https://www.themealdb.com/api/json/v1/1"

INGREDIENT_TRANSLATIONS = {
    "Куриное филе": "chicken breast",
    "Рис": "rice",
    "Лук": "onion",
    "Масло": "oil",
    "Гречка": "buckwheat",
    "Картофель": "potato",
    "Сметана": "sour cream",
    "Овощная смесь": "vegetables",
    "Говядина": "beef",
    "Морковь": "carrot",
    "Томатная паста": "tomato paste",
    "Свинина": "pork",
    "Домашний фарш": "mince",
    "Говяжий фарш": "beef mince",
    "Капуста": "cabbage",
    "Болгарский перец": "bell pepper",
    "Шампиньоны": "mushroom",
    "Чечевица": "lentils",
    "Фасоль": "beans",
    "Свекла": "beetroot",
    "Огурец": "cucumber",
    "Помидор": "tomato",
    "Огурец соленый": "pickle",
    "Кукуруза": "corn",
    "Чеснок": "garlic",
    "Макароны": "pasta",
    "бычьи яйца": "bull testicles",
}

SPECIAL_NOTE_QUERIES = {
    "бычьи яйца": ["bull testicles", "testicle", "offal"],
    "bull testicles": ["bull testicles", "testicle", "offal"],
    "testicles": ["testicle", "offal"],
}

MEAT_WORDS = {
    "chicken": "chicken",
    "beef": "beef",
    "pork": "pork",
    "sausage": "pork",
    "ham": "pork",
    "bacon": "pork",
    "mince": "mince",
    "ground beef": "beef",
    "lamb": "beef",
    "turkey": "chicken",
    "egg": "vegetarian",
    "milk": "dairy",
    "cheese": "dairy",
    "cream": "dairy",
    "butter": "dairy",
}

def _dedupe_keep_order(items):
    seen = set()
    result = []
    for item in items:
        key = item.lower().strip()
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(item.strip())
    return result

def _extract_note_queries(user_note: str):
    note = (user_note or "").strip().lower()
    queries = []

    for trigger, mapped in SPECIAL_NOTE_QUERIES.items():
        if trigger in note:
            queries.extend(mapped)

    # quoted phrases
    for phrase in re.findall(r'"([^"]+)"', note):
        queries.append(phrase)

    # simple known ingredient aliases present in note
    for ru, en in INGREDIENT_TRANSLATIONS.items():
        if ru.lower() in note:
            queries.append(en)

    # english food-ish tokens
    for token in re.findall(r"[a-zA-Z][a-zA-Z\-]{2,}", note):
        if token.lower() not in {"want", "have", "with", "from", "menu", "recipe", "recipes"}:
            queries.append(token.lower())

    return _dedupe_keep_order(queries)

def _extract_pantry_queries(pantry_items):
    queries = []
    for item in pantry_items or []:
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        queries.append(INGREDIENT_TRANSLATIONS.get(name, name))
    return _dedupe_keep_order(queries)

def _derive_flags(ingredients):
    ingredient_names = " ".join(item["name"].lower() for item in ingredients)

    protein_type = "vegan"
    is_vegetarian = True
    is_vegan = True

    for word, kind in MEAT_WORDS.items():
        if word in ingredient_names:
            if kind in {"chicken", "beef", "pork", "mince"}:
                protein_type = kind
                is_vegetarian = False
                is_vegan = False
                break
            if kind == "vegetarian":
                protein_type = "vegetarian"
                is_vegan = False
            if kind == "dairy":
                protein_type = "vegetarian"
                is_vegan = False

    return protein_type, is_vegetarian, is_vegan

def _parse_meal_to_recipe(meal):
    ingredients = []
    for i in range(1, 21):
        name = (meal.get(f"strIngredient{i}") or "").strip()
        measure = (meal.get(f"strMeasure{i}") or "").strip()
        if not name:
            continue
        ingredients.append({
            "name": name,
            "quantity": 1,
            "unit": "pc",
            "measure_text": measure,
        })

    protein_type, is_vegetarian, is_vegan = _derive_flags(ingredients)

    title = (meal.get("strMeal") or "").strip()
    category_raw = (meal.get("strCategory") or "").strip().lower()
    category = "salad" if ("salad" in title.lower() or "salad" in category_raw) else "main"

    estimated_cost_rub = 220 if category == "salad" else 650
    tags = ["external_recipe"]
    if protein_type == "pork":
        tags.append("contains_pork")
    if protein_type == "beef":
        tags.append("contains_beef")
    if protein_type == "chicken":
        tags.append("contains_chicken")
    if is_vegetarian:
        tags.append("vegetarian")
    if is_vegan:
        tags.append("vegan")

    instructions = (meal.get("strInstructions") or "").strip()
    description = instructions.split(".")[0].strip()
    if not description:
        description = f"External recipe from TheMealDB: {title}"

    return {
        "id": 900000000 + int(meal["idMeal"]),
        "title": title,
        "description": description,
        "category": category,
        "difficulty": "medium",
        "estimated_cost_rub": estimated_cost_rub,
        "cooking_time_min": 45 if category == "main" else 15,
        "portions": 4,
        "protein_type": protein_type,
        "is_batch_friendly": True,
        "is_vegetarian": is_vegetarian,
        "is_vegan": is_vegan,
        "tags": tags,
        "ingredients": ingredients,
        "external_source": "TheMealDB",
        "external_url": meal.get("strSource") or meal.get("strYoutube") or "",
    }

def _passes_filters(recipe, excluded_tags):
    excluded = {str(tag).strip().lower() for tag in excluded_tags or [] if str(tag).strip()}
    recipe_tags = {str(tag).strip().lower() for tag in recipe.get("tags", [])}

    if "vegan_only" in excluded and not recipe.get("is_vegan"):
        return False
    if "vegetarian_only" in excluded and not recipe.get("is_vegetarian") and "vegan_only" not in excluded:
        return False
    if "contains_pork" in excluded and "contains_pork" in recipe_tags:
        return False
    if "contains_beef" in excluded and "contains_beef" in recipe_tags:
        return False

    return True

async def _lookup_meal(client, meal_id):
    response = await client.get(f"{THEMEALDB_BASE}/lookup.php", params={"i": meal_id})
    response.raise_for_status()
    data = response.json()
    meals = data.get("meals") or []
    return meals[0] if meals else None

async def _search_by_name(client, query):
    response = await client.get(f"{THEMEALDB_BASE}/search.php", params={"s": query})
    response.raise_for_status()
    data = response.json()
    return data.get("meals") or []

async def _search_by_ingredient(client, query):
    response = await client.get(f"{THEMEALDB_BASE}/filter.php", params={"i": query.replace(" ", "_")})
    response.raise_for_status()
    data = response.json()
    return data.get("meals") or []

async def search_external_recipes(user_note, pantry_items, excluded_tags, limit=6):
    queries = _extract_pantry_queries(pantry_items) + _extract_note_queries(user_note)
    queries = _dedupe_keep_order(queries)[:6]

    if not queries:
        return []

    found = []
    seen_ids = set()

    async with httpx.AsyncClient(timeout=20) as client:
        for query in queries:
            meals_by_name = await _search_by_name(client, query)
            for meal in meals_by_name[:3]:
                recipe = _parse_meal_to_recipe(meal)
                if recipe["id"] in seen_ids or not _passes_filters(recipe, excluded_tags):
                    continue
                seen_ids.add(recipe["id"])
                found.append(recipe)
                if len(found) >= limit:
                    return found

            meals_by_ingredient = await _search_by_ingredient(client, query)
            for meal in meals_by_ingredient[:3]:
                full = await _lookup_meal(client, meal["idMeal"])
                if not full:
                    continue
                recipe = _parse_meal_to_recipe(full)
                if recipe["id"] in seen_ids or not _passes_filters(recipe, excluded_tags):
                    continue
                seen_ids.add(recipe["id"])
                found.append(recipe)
                if len(found) >= limit:
                    return found

    return found
