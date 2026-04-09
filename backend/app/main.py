import json
import os
from copy import deepcopy
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from passlib.context import CryptContext

from .database import Base, engine, get_db, SessionLocal
from .models import Recipe, MealPlan, User
from .schemas import (
    GeneratePlanRequest,
    ToggleFavoriteRequest,
    ReplaceBatchRequest,
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
)
from .seed_data import seed_recipes
from .price_catalog import PRICE_UPDATED_AT, MEAL_MODES, get_price_catalog_list, ingredient_cost
from .openrouter_client import generate_batch_plan_with_llm, suggest_replacement_with_llm
from .external_recipe_client import search_external_recipes

app = FastAPI(title="BudgetBites API V3.1")

origins = [
    origin.strip()
    for origin in os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS", "30"))
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_recipes(db)
    finally:
        db.close()

@app.get("/api/health")
def health():
    return {"status": "ok"}

def verify_password(plain_password, password_hash):
    return pwd_context.verify(plain_password, password_hash)

def hash_password(password):
    return pwd_context.hash(password)

def create_access_token(user_id: int, email: str):
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def serialize_user(user: User):
    return {
        "id": user.id,
        "email": user.email,
    }

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
    return user

def normalize_list(values):
    return [str(v).strip() for v in values if str(v).strip()]

def parse_tags(tags: str):
    return {tag.strip().lower() for tag in tags.split(",") if tag.strip()}

def parse_json_field(raw, default):
    try:
        return json.loads(raw or "")
    except Exception:
        return default

def sanitize_overrides(overrides):
    clean = {}
    for item in get_price_catalog_list():
        name = item["name"]
        value = overrides.get(name)
        if value is None:
            continue
        try:
            num = float(value)
            if num > 0:
                clean[name] = round(num, 2)
        except Exception:
            continue
    return clean

def normalize_pantry_items(items):
    normalized = []
    for item in items:
        if hasattr(item, "name"):
            name = str(item.name).strip()
            quantity = float(item.quantity)
            unit = str(item.unit).strip().lower()
        else:
            name = str(item.get("name", "")).strip()
            quantity = float(item.get("quantity", 0))
            unit = str(item.get("unit", "")).strip().lower()

        if not name or quantity <= 0:
            continue
        if unit not in {"g", "kg", "ml", "l", "pc"}:
            continue

        normalized.append({
            "name": name,
            "quantity": quantity,
            "unit": unit,
        })
    return normalized

def convert_quantity(quantity, from_unit, to_unit):
    from_unit = str(from_unit).strip().lower()
    to_unit = str(to_unit).strip().lower()
    quantity = float(quantity)

    if from_unit == to_unit:
        return quantity

    mass_units = {"g", "kg"}
    volume_units = {"ml", "l"}

    if from_unit in mass_units and to_unit in mass_units:
        if from_unit == "kg" and to_unit == "g":
            return quantity * 1000.0
        if from_unit == "g" and to_unit == "kg":
            return quantity / 1000.0

    if from_unit in volume_units and to_unit in volume_units:
        if from_unit == "l" and to_unit == "ml":
            return quantity * 1000.0
        if from_unit == "ml" and to_unit == "l":
            return quantity / 1000.0

    return None

def compute_recipe_cost(recipe: Recipe, price_overrides):
    ingredients = parse_json_field(recipe.ingredients_json, [])
    total = 0.0
    for ingredient in ingredients:
        total += ingredient_cost(
            ingredient.get("name"),
            ingredient.get("quantity"),
            ingredient.get("unit"),
            price_overrides,
        )
    total = round(total, 2)
    return total if total > 0 else round(recipe.estimated_cost_rub, 2)

def build_recipe_view(recipe: Recipe, price_overrides):
    return {
        "id": recipe.id,
        "title": recipe.title,
        "description": recipe.description,
        "category": recipe.category,
        "difficulty": recipe.difficulty,
        "estimated_cost_rub": compute_recipe_cost(recipe, price_overrides),
        "cooking_time_min": recipe.cooking_time_min,
        "portions": recipe.portions,
        "protein_type": recipe.protein_type,
        "is_batch_friendly": recipe.is_batch_friendly,
        "is_vegetarian": recipe.is_vegetarian,
        "is_vegan": recipe.is_vegan,
        "tags": [tag.strip() for tag in recipe.tags.split(",") if tag.strip()],
        "ingredients": parse_json_field(recipe.ingredients_json, []),
    }

def apply_recipe_filters(recipes, excluded_tags):
    excluded = {tag.strip().lower() for tag in excluded_tags if tag.strip()}
    vegan_only = "vegan_only" in excluded
    vegetarian_only = "vegetarian_only" in excluded
    no_pork = "contains_pork" in excluded
    no_beef = "contains_beef" in excluded

    filtered = []
    for recipe in recipes:
        recipe_tags = parse_tags(recipe.tags)

        if vegan_only and not recipe.is_vegan:
            continue
        if not vegan_only and vegetarian_only and not recipe.is_vegetarian:
            continue
        if no_pork and "contains_pork" in recipe_tags:
            continue
        if no_beef and "contains_beef" in recipe_tags:
            continue

        filtered.append(recipe)

    return filtered

def compute_missing_ingredients(selected_recipes, pantry_items):
    required = defaultdict(float)
    labels = {}

    for recipe in selected_recipes:
        for ingredient in recipe["ingredients"]:
            name = str(ingredient.get("name", "")).strip()
            unit = str(ingredient.get("unit", "")).strip().lower()
            quantity = float(ingredient.get("quantity", 0))
            if not name or quantity <= 0:
                continue
            key = (name.lower(), unit)
            required[key] += quantity
            labels[key] = name

    missing = []
    for (name_lower, unit), needed_qty in required.items():
        available_qty = 0.0
        for pantry_item in pantry_items:
            if pantry_item["name"].strip().lower() != name_lower:
                continue
            converted = convert_quantity(pantry_item["quantity"], pantry_item["unit"], unit)
            if converted is not None:
                available_qty += converted

        diff = round(needed_qty - available_qty, 2)
        if diff > 0:
            missing.append({
                "name": labels[(name_lower, unit)],
                "quantity": diff,
                "unit": unit,
            })

    missing.sort(key=lambda item: item["name"])
    return missing

def estimate_min_budget(recipe_views, days, meal_mode):
    mode = MEAL_MODES[meal_mode]
    main_needed = days * mode["main_per_day"]
    salad_needed = days * mode["salad_per_day"]

    mains = sorted([r for r in recipe_views if r["category"] != "salad"], key=lambda x: x["estimated_cost_rub"])
    salads = sorted([r for r in recipe_views if r["category"] == "salad"], key=lambda x: x["estimated_cost_rub"])

    selected = []
    main_covered = 0
    for recipe in mains:
        if main_covered >= main_needed:
            break
        selected.append(recipe)
        main_covered += recipe["portions"]

    if main_covered < main_needed:
        raise HTTPException(status_code=400, detail="Not enough main dishes in the catalog for the selected meal mode.")

    salad_covered = 0
    for recipe in salads:
        if salad_covered >= salad_needed:
            break
        selected.append(recipe)
        salad_covered += recipe["portions"]

    if salad_covered < salad_needed:
        raise HTTPException(status_code=400, detail="Not enough salads in the catalog for the selected meal mode.")

    return round(sum(item["estimated_cost_rub"] for item in selected), 2)

def validate_batch_plan(llm_result, recipe_map, budget_rub, days, meal_mode, excluded_tags):
    mode = MEAL_MODES[meal_mode]
    total_slots = mode["main_per_day"] + mode["salad_per_day"]

    batches = llm_result.get("batches")
    schedule = llm_result.get("schedule")
    reasoning = str(llm_result.get("reasoning", "")).strip()

    if not isinstance(batches, list) or not batches:
        raise HTTPException(status_code=500, detail="LLM returned an invalid batches list.")
    if not isinstance(schedule, list) or len(schedule) != days:
        raise HTTPException(status_code=500, detail="LLM returned an invalid schedule list.")

    seen_batch_numbers = set()
    selected_recipe_ids = []

    for batch in batches:
        batch_number = batch.get("batch_number")
        recipe_id = batch.get("recipe_id")

        if not isinstance(batch_number, int) or batch_number < 1:
            raise HTTPException(status_code=500, detail="Invalid batch_number.")
        if batch_number in seen_batch_numbers:
            raise HTTPException(status_code=500, detail="LLM returned a duplicate batch_number.")
        if recipe_id not in recipe_map:
            raise HTTPException(status_code=500, detail="LLM returned a recipe_id outside the allowed catalog.")

        seen_batch_numbers.add(batch_number)
        selected_recipe_ids.append(recipe_id)

    total_cost_rub = round(sum(recipe_map[recipe_id]["estimated_cost_rub"] for recipe_id in selected_recipe_ids), 2)
    if total_cost_rub > budget_rub:
        raise HTTPException(status_code=400, detail=f"The generated plan exceeds the budget: {total_cost_rub} RUB > {budget_rub} RUB.")

    usage_counter = Counter()
    normalized_schedule = []

    for index, day in enumerate(schedule, start=1):
        day_number = day.get("day_number")
        recipe_ids = day.get("recipe_ids")

        if day_number != index:
            raise HTTPException(status_code=500, detail="LLM returned invalid day numbering.")
        if not isinstance(recipe_ids, list) or len(recipe_ids) != total_slots:
            raise HTTPException(status_code=500, detail="LLM returned an invalid number of meals per day.")

        day_recipes = []
        for recipe_id in recipe_ids:
            if recipe_id not in selected_recipe_ids:
                raise HTTPException(status_code=500, detail="Schedule contains a recipe_id that is not present in batches.")
            usage_counter[recipe_id] += 1
            day_recipes.append(recipe_map[recipe_id])

        main_count = sum(1 for r in day_recipes if r["category"] != "salad")
        salad_count = sum(1 for r in day_recipes if r["category"] == "salad")

        if main_count < mode["main_per_day"]:
            raise HTTPException(status_code=500, detail="A day does not contain enough main dishes.")
        if salad_count < mode["salad_per_day"]:
            raise HTTPException(status_code=500, detail="A day does not contain enough salads.")

        normalized_schedule.append({
            "day_number": day_number,
            "recipe_ids": recipe_ids,
        })

    for recipe_id, used_count in usage_counter.items():
        if used_count > recipe_map[recipe_id]["portions"]:
            raise HTTPException(
                status_code=500,
                detail=f"Recipe {recipe_map[recipe_id]['title']} is used {used_count} times but only supports {recipe_map[recipe_id]['portions']} portions."
            )

    excluded = {tag.strip().lower() for tag in excluded_tags if tag.strip()}
    plant_only = ("vegan_only" in excluded) or ("vegetarian_only" in excluded)
    if not plant_only and budget_rub >= 1000:
        has_animal_protein = any(
            recipe_map[recipe_id]["protein_type"] in {"chicken", "pork", "beef", "mince"}
            for recipe_id in selected_recipe_ids
        )
        if not has_animal_protein:
            raise HTTPException(status_code=500, detail="The generated plan for a regular user contains no animal protein.")

    return {
        "reasoning": reasoning,
        "batches": [{"batch_number": batch["batch_number"], "recipe_id": batch["recipe_id"]} for batch in batches],
        "schedule": normalized_schedule,
        "total_cost_rub": total_cost_rub,
    }

def build_plan_payload(validated_plan, recipe_map, pantry_items, meal_mode, price_overrides, user_note):
    unique_recipe_ids = [batch["recipe_id"] for batch in validated_plan["batches"]]
    selected_recipes = [recipe_map[recipe_id] for recipe_id in unique_recipe_ids]

    batches = []
    for batch in validated_plan["batches"]:
        recipe = recipe_map[batch["recipe_id"]]
        batches.append({
            "batch_number": batch["batch_number"],
            "recipe": recipe,
        })

    schedule = []
    for day in validated_plan["schedule"]:
        schedule.append({
            "day_number": day["day_number"],
            "meals": [recipe_map[recipe_id] for recipe_id in day["recipe_ids"]]
        })

    missing_ingredients = compute_missing_ingredients(selected_recipes, pantry_items)

    return {
        "meal_mode": meal_mode,
        "price_overrides": price_overrides,
        "user_note": user_note,
        "reasoning": validated_plan["reasoning"],
        "total_cost_rub": validated_plan["total_cost_rub"],
        "batches": batches,
        "schedule": schedule,
        "missing_ingredients": missing_ingredients,
    }

def serialize_meal_plan(plan: MealPlan):
    parsed_plan = parse_json_field(plan.plan_json, {})
    return {
        "meal_plan_id": plan.id,
        "budget_rub": plan.budget_rub,
        "days": plan.days,
        "meal_mode": parsed_plan.get("meal_mode", "1"),
        "meal_mode_label": MEAL_MODES.get(parsed_plan.get("meal_mode", "1"), MEAL_MODES["1"])["label"],
        "excluded_tags": normalize_list(plan.excluded_tags.split(",")),
        "pantry_items": parse_json_field(plan.pantry_items_json, []),
        "is_favorite": plan.is_favorite,
        "created_at": plan.created_at.isoformat(),
        "reasoning": plan.llm_reasoning,
        "user_note": parsed_plan.get("user_note", ""),
        "total_cost_rub": plan.total_cost_rub,
        "batches": parsed_plan.get("batches", []),
        "schedule": parsed_plan.get("schedule", []),
        "missing_ingredients": parsed_plan.get("missing_ingredients", []),
        "price_overrides": parsed_plan.get("price_overrides", {}),
    }

def save_meal_plan(db: Session, current_user: User, request: GeneratePlanRequest, pantry_items, payload):
    meals_per_day_total = MEAL_MODES[request.meal_mode]["main_per_day"] + MEAL_MODES[request.meal_mode]["salad_per_day"]

    plan = MealPlan(
        user_id=current_user.id,
        budget_rub=request.budget_rub,
        days=request.days,
        meals_per_day=meals_per_day_total,
        excluded_tags=",".join(request.excluded_tags),
        pantry_items_json=json.dumps(pantry_items, ensure_ascii=False),
        total_cost_rub=payload["total_cost_rub"],
        llm_reasoning=payload["reasoning"],
        plan_json=json.dumps({
            "meal_mode": payload["meal_mode"],
            "price_overrides": payload["price_overrides"],
            "user_note": payload["user_note"],
            "batches": payload["batches"],
            "schedule": payload["schedule"],
            "missing_ingredients": payload["missing_ingredients"],
        }, ensure_ascii=False),
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan

def get_owned_plan_or_404(db: Session, meal_plan_id: int, current_user: User):
    plan = (
        db.query(MealPlan)
        .filter(MealPlan.id == meal_plan_id, MealPlan.user_id == current_user.id)
        .first()
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Meal plan not found.")
    return plan

async def build_catalog_with_external(request: GeneratePlanRequest, allowed_views, pantry_items):
    external = []
    try:
        external = await search_external_recipes(
            user_note=request.user_note,
            pantry_items=pantry_items,
            excluded_tags=request.excluded_tags,
            limit=6,
        )
    except Exception:
        external = []

    existing_ids = {item["id"] for item in allowed_views}
    existing_titles = {item["title"].strip().lower() for item in allowed_views}

    for item in external:
        if item["id"] in existing_ids:
            continue
        if item["title"].strip().lower() in existing_titles:
            continue
        allowed_views.append(item)

    return allowed_views

async def generate_and_store_plan(db: Session, current_user: User, request: GeneratePlanRequest):
    if request.meal_mode not in MEAL_MODES:
        raise HTTPException(status_code=400, detail="Invalid meal mode.")

    price_overrides = sanitize_overrides(request.price_overrides)
    pantry_items = normalize_pantry_items(request.pantry_items)
    user_note = str(request.user_note or "").strip()

    recipes = db.query(Recipe).all()
    allowed_recipes = apply_recipe_filters(recipes, request.excluded_tags)
    if not allowed_recipes:
        raise HTTPException(status_code=400, detail="No recipes available after applying filters.")

    allowed_views = [build_recipe_view(recipe, price_overrides) for recipe in allowed_recipes]
    allowed_views = await build_catalog_with_external(request, allowed_views, pantry_items)

    min_budget = estimate_min_budget(allowed_views, request.days, request.meal_mode)
    if request.budget_rub < min_budget:
        raise HTTPException(
            status_code=400,
            detail=f"The selected meal mode requires at least about {min_budget} ₽ for {request.days} day(s)."
        )

    mode = MEAL_MODES[request.meal_mode]
    target_min = round(request.budget_rub * 0.8, 2)

    recipe_map = {recipe["id"]: recipe for recipe in allowed_views}
    validated_plan = None
    last_error = None

    for _attempt in range(3):
        try:
            llm_result = await generate_batch_plan_with_llm(
                budget_rub=request.budget_rub,
                days=request.days,
                meal_mode_label=mode["label"],
                main_per_day=mode["main_per_day"],
                salad_per_day=mode["salad_per_day"],
                excluded_tags=request.excluded_tags,
                pantry_items=pantry_items,
                user_note=user_note,
                recipes=allowed_views,
                target_min_spend=target_min,
            )

            validated_plan = validate_batch_plan(
                llm_result=llm_result,
                recipe_map=recipe_map,
                budget_rub=request.budget_rub,
                days=request.days,
                meal_mode=request.meal_mode,
                excluded_tags=request.excluded_tags,
            )
            break
        except HTTPException as exc:
            last_error = exc
            continue
        except Exception as exc:
            last_error = HTTPException(status_code=502, detail=f"LLM request failed: {str(exc)}")
            break

    if validated_plan is None:
        raise last_error or HTTPException(status_code=500, detail="Failed to generate a valid meal plan.")

    if validated_plan["total_cost_rub"] < target_min:
        validated_plan["reasoning"] = (
            f"{validated_plan['reasoning']} "
            f"Каталог не позволил приблизиться к бюджету: итог {validated_plan['total_cost_rub']} ₽ при бюджете {request.budget_rub} ₽."
        ).strip()

    payload = build_plan_payload(
        validated_plan=validated_plan,
        recipe_map=recipe_map,
        pantry_items=pantry_items,
        meal_mode=request.meal_mode,
        price_overrides=price_overrides,
        user_note=user_note,
    )
    return save_meal_plan(db, current_user, request, pantry_items, payload)

@app.post("/api/auth/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="User with this email already exists.")

    user = User(
        email=email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, user.email)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": serialize_user(user),
    }

@app.post("/api/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = create_access_token(user.id, user.email)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": serialize_user(user),
    }

@app.get("/api/auth/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return serialize_user(current_user)

@app.get("/api/meta")
def get_meta(db: Session = Depends(get_db)):
    recipes = db.query(Recipe).all()
    ingredient_names = set()
    for recipe in recipes:
        for item in parse_json_field(recipe.ingredients_json, []):
            name = str(item.get("name", "")).strip()
            if name:
                ingredient_names.add(name)

    price_catalog = get_price_catalog_list()
    price_index = {item["name"]: item for item in price_catalog}

    pantry_options = []
    for name in sorted(ingredient_names):
        default_unit = "pc"
        if name in price_index:
            if price_index[name]["measure"] == "kg":
                default_unit = "g"
            elif price_index[name]["measure"] == "l":
                default_unit = "ml"
        pantry_options.append({
            "name": name,
            "default_unit": default_unit,
        })

    return {
        "price_updated_at": PRICE_UPDATED_AT,
        "meal_modes": [
            {"value": key, "label": value["label"]}
            for key, value in MEAL_MODES.items()
        ],
        "filters": [
            {"value": "contains_pork", "label": "Без свинины"},
            {"value": "contains_beef", "label": "Без говядины"},
            {"value": "vegetarian_only", "label": "Вегетарианское"},
            {"value": "vegan_only", "label": "Веганское"},
        ],
        "pantry_options": pantry_options,
        "price_catalog": price_catalog,
    }

@app.get("/api/recipes")
def list_recipes(db: Session = Depends(get_db)):
    recipes = db.query(Recipe).order_by(Recipe.category.asc(), Recipe.estimated_cost_rub.asc()).all()
    return [build_recipe_view(recipe, {}) for recipe in recipes]

@app.post("/api/meal-plans/generate")
async def generate_meal_plan(
    payload: GeneratePlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    saved_plan = await generate_and_store_plan(db, current_user, payload)
    return serialize_meal_plan(saved_plan)

@app.get("/api/meal-plans/history")
def get_history(
    limit: int = 15,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plans = (
        db.query(MealPlan)
        .filter(MealPlan.user_id == current_user.id)
        .order_by(MealPlan.created_at.desc())
        .limit(min(max(limit, 1), 15))
        .all()
    )
    result = []
    for plan in plans:
        parsed = parse_json_field(plan.plan_json, {})
        result.append({
            "meal_plan_id": plan.id,
            "created_at": plan.created_at.isoformat(),
            "total_cost_rub": plan.total_cost_rub,
            "days": plan.days,
            "meal_mode": parsed.get("meal_mode", "1"),
            "meal_mode_label": MEAL_MODES.get(parsed.get("meal_mode", "1"), MEAL_MODES["1"])["label"],
            "is_favorite": plan.is_favorite,
            "summary": ", ".join(
                batch["recipe"]["title"] for batch in parsed.get("batches", [])[:3]
            ),
        })
    return result

@app.get("/api/meal-plans/favorites")
def get_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plans = (
        db.query(MealPlan)
        .filter(MealPlan.user_id == current_user.id, MealPlan.is_favorite == True)
        .order_by(MealPlan.created_at.desc())
        .all()
    )
    result = []
    for plan in plans:
        parsed = parse_json_field(plan.plan_json, {})
        result.append({
            "meal_plan_id": plan.id,
            "created_at": plan.created_at.isoformat(),
            "total_cost_rub": plan.total_cost_rub,
            "days": plan.days,
            "meal_mode": parsed.get("meal_mode", "1"),
            "meal_mode_label": MEAL_MODES.get(parsed.get("meal_mode", "1"), MEAL_MODES["1"])["label"],
            "is_favorite": plan.is_favorite,
            "summary": ", ".join(
                batch["recipe"]["title"] for batch in parsed.get("batches", [])[:3]
            ),
        })
    return result

@app.get("/api/meal-plans/{meal_plan_id}")
def get_meal_plan(
    meal_plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = get_owned_plan_or_404(db, meal_plan_id, current_user)
    return serialize_meal_plan(plan)

@app.post("/api/meal-plans/{meal_plan_id}/favorite")
def toggle_favorite(
    meal_plan_id: int,
    payload: ToggleFavoriteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = get_owned_plan_or_404(db, meal_plan_id, current_user)
    plan.is_favorite = payload.is_favorite
    db.commit()
    db.refresh(plan)
    return {"meal_plan_id": plan.id, "is_favorite": plan.is_favorite}

@app.post("/api/meal-plans/{meal_plan_id}/regenerate")
async def regenerate_plan(
    meal_plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = get_owned_plan_or_404(db, meal_plan_id, current_user)

    parsed = parse_json_field(plan.plan_json, {})
    pantry_raw = parse_json_field(plan.pantry_items_json, [])
    request = GeneratePlanRequest(
        budget_rub=plan.budget_rub,
        days=plan.days,
        meal_mode=parsed.get("meal_mode", "1"),
        excluded_tags=normalize_list(plan.excluded_tags.split(",")),
        pantry_items=pantry_raw,
        price_overrides=parsed.get("price_overrides", {}),
        user_note=parsed.get("user_note", ""),
    )
    saved_plan = await generate_and_store_plan(db, current_user, request)
    return serialize_meal_plan(saved_plan)

@app.post("/api/meal-plans/{meal_plan_id}/replace-batch")
async def replace_batch(
    meal_plan_id: int,
    payload: ReplaceBatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = get_owned_plan_or_404(db, meal_plan_id, current_user)

    parsed = parse_json_field(plan.plan_json, {})
    pantry_raw = parse_json_field(plan.pantry_items_json, [])
    request = GeneratePlanRequest(
        budget_rub=plan.budget_rub,
        days=plan.days,
        meal_mode=parsed.get("meal_mode", "1"),
        excluded_tags=normalize_list(plan.excluded_tags.split(",")),
        pantry_items=pantry_raw,
        price_overrides=parsed.get("price_overrides", {}),
        user_note=parsed.get("user_note", ""),
    )
    price_overrides = sanitize_overrides(request.price_overrides)

    recipes = db.query(Recipe).all()
    allowed_recipes = apply_recipe_filters(recipes, request.excluded_tags)
    allowed_views = [build_recipe_view(recipe, price_overrides) for recipe in allowed_recipes]
    allowed_views = await build_catalog_with_external(request, allowed_views, normalize_pantry_items(request.pantry_items))
    recipe_map = {recipe["id"]: recipe for recipe in allowed_views}

    current_plan = deepcopy(parsed)
    batches = current_plan.get("batches", [])
    schedule = current_plan.get("schedule", [])

    target_batch = next((batch for batch in batches if batch.get("batch_number") == payload.batch_number), None)
    if not target_batch:
        raise HTTPException(status_code=404, detail="Batch not found.")

    target_recipe_id = target_batch["recipe"]["id"]
    selected_recipe_ids = [batch["recipe"]["id"] for batch in batches]

    candidates = [
        recipe for recipe in allowed_views
        if recipe["id"] != target_recipe_id and recipe["id"] not in selected_recipe_ids
    ]
    if not candidates:
        raise HTTPException(status_code=400, detail="No suitable candidates found for replacement.")

    try:
        llm_result = await suggest_replacement_with_llm(
            budget_rub=request.budget_rub,
            current_total_cost_rub=plan.total_cost_rub,
            batch_number=payload.batch_number,
            target_recipe_id=target_recipe_id,
            target_recipe_cost_rub=recipe_map[target_recipe_id]["estimated_cost_rub"],
            candidate_recipes=candidates,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM request failed: {str(exc)}")

    new_recipe_id = llm_result.get("recipe_id")
    if new_recipe_id not in {recipe["id"] for recipe in candidates}:
        raise HTTPException(status_code=500, detail="LLM returned an invalid replacement recipe_id.")

    for batch in batches:
        if batch["batch_number"] == payload.batch_number:
            batch["recipe"] = recipe_map[new_recipe_id]

    for day in schedule:
        new_meals = []
        for meal in day["meals"]:
            if meal["id"] == target_recipe_id:
                new_meals.append(recipe_map[new_recipe_id])
            else:
                new_meals.append(meal)
        day["meals"] = new_meals

    fake_llm_result = {
        "reasoning": f"{plan.llm_reasoning} | Replaced batch {payload.batch_number}",
        "batches": [{"batch_number": batch["batch_number"], "recipe_id": batch["recipe"]["id"]} for batch in batches],
        "schedule": [{"day_number": day["day_number"], "recipe_ids": [meal["id"] for meal in day["meals"]]} for day in schedule],
    }

    validated_plan = validate_batch_plan(
        llm_result=fake_llm_result,
        recipe_map=recipe_map,
        budget_rub=request.budget_rub,
        days=request.days,
        meal_mode=request.meal_mode,
        excluded_tags=request.excluded_tags,
    )

    payload_plan = build_plan_payload(
        validated_plan=validated_plan,
        recipe_map=recipe_map,
        pantry_items=normalize_pantry_items(request.pantry_items),
        meal_mode=request.meal_mode,
        price_overrides=price_overrides,
        user_note=request.user_note,
    )
    saved_plan = save_meal_plan(db, current_user, request, normalize_pantry_items(request.pantry_items), payload_plan)
    return serialize_meal_plan(saved_plan)
