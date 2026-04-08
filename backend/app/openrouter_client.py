import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/free").strip()
APP_NAME = os.getenv("APP_NAME", "BudgetBites").strip()
APP_SITE_URL = os.getenv("APP_SITE_URL", "http://localhost:5173").strip()
OPENROUTER_ENABLE_REASONING = os.getenv("OPENROUTER_ENABLE_REASONING", "false").strip().lower() == "true"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    default_headers={
        "HTTP-Referer": APP_SITE_URL,
        "X-OpenRouter-Title": APP_NAME,
    },
)

def extract_json(text: str):
    text = (text or "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start:end + 1])
        raise RuntimeError(f"LLM returned invalid JSON: {text[:1000]}")

def _build_kwargs(messages):
    kwargs = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
    }

    if OPENROUTER_ENABLE_REASONING:
        kwargs["extra_body"] = {
            "reasoning": {
                "enabled": True,
            }
        }

    return kwargs

async def call_openrouter(messages):
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY.startswith("PASTE_"):
        raise RuntimeError("OPENROUTER_API_KEY is missing or still a placeholder in backend/.env")

    try:
        response = client.chat.completions.create(**_build_kwargs(messages))
    except Exception as exc:
        raise RuntimeError(f"OpenRouter SDK error: {exc}")

    try:
        content = response.choices[0].message.content or ""
    except Exception:
        try:
            raw = response.model_dump_json()
        except Exception:
            raw = str(response)
        raise RuntimeError(f"Unexpected OpenRouter response format: {raw[:1000]}")

    return extract_json(content)

async def generate_batch_plan_with_llm(
    budget_rub,
    days,
    meal_mode_label,
    main_per_day,
    salad_per_day,
    excluded_tags,
    pantry_items,
    user_note,
    recipes,
    target_min_spend=None,
):
    target_note = ""
    if target_min_spend:
        target_note = f"- Постарайся получить итоговую стоимость не ниже {target_min_spend} RUB, если каталог это позволяет.\n"

    prompt = f"""
Ты помощник по планированию питания для студента в России.

Собери realistic batch-cooking plan.

Параметры:
- Бюджет: {budget_rub} RUB
- Дней: {days}
- Режим: {meal_mode_label}
- Основных блюд в день: {main_per_day}
- Салатов в день: {salad_per_day}
- Исключённые теги: {excluded_tags}
- Продукты, которые уже есть дома: {pantry_items}
- Комментарий пользователя: {user_note if user_note else "нет"}

Правила:
- Используй ТОЛЬКО рецепты из каталога.
- Не придумывай новые блюда.
- НИКОГДА не выдумывай recipe_id.
- Используй ТОЛЬКО recipe_id, которые реально присутствуют в каталоге ниже.
- Если точного блюда под пожелание пользователя нет даже среди внешних кандидатов, честно напиши это в reasoning и собери лучший допустимый план из доступных recipe_id.
- План должен быть batch-friendly.
- Для каждого дня выдай полный список recipe_ids на день.
- Если нужен салат, в каждом дне должен быть минимум один salad recipe.
- Если пользователь НЕ vegetarian/vegan, не делай полностью plan без animal protein, если бюджет позволяет.
- Если список pantry пуст, но в комментарии пользователя явно перечислены продукты, учитывай эти упоминания.
- Старайся учитывать pantry items.
- Старайся учитывать комментарий пользователя, если он дан.
- Уложись в бюджет.
{target_note}- Верни СТРОГО JSON без markdown.

Формат JSON:
{{
  "reasoning": "краткое объяснение",
  "batches": [
    {{"batch_number": 1, "recipe_id": 1}},
    {{"batch_number": 2, "recipe_id": 25}}
  ],
  "schedule": [
    {{"day_number": 1, "recipe_ids": [1, 25]}},
    {{"day_number": 2, "recipe_ids": [1, 25]}}
  ]
}}

Каталог рецептов:
{json.dumps(recipes, ensure_ascii=False)}
""".strip()

    return await call_openrouter([
        {"role": "system", "content": "Ты очень строгий JSON API. Отвечай только валидным JSON."},
        {"role": "user", "content": prompt},
    ])

async def suggest_replacement_with_llm(
    budget_rub,
    current_total_cost_rub,
    batch_number,
    target_recipe_id,
    target_recipe_cost_rub,
    candidate_recipes,
):
    max_allowed_cost = budget_rub - (current_total_cost_rub - target_recipe_cost_rub)

    prompt = f"""
Нужно заменить одно batch-блюдо в существующем плане.

Параметры:
- Общий бюджет: {budget_rub} RUB
- Текущая стоимость плана: {current_total_cost_rub} RUB
- Номер batch для замены: {batch_number}
- Текущий recipe_id: {target_recipe_id}
- Максимально допустимая стоимость нового batch: {max_allowed_cost} RUB

Правила:
- Выбери ТОЛЬКО один recipe_id из списка кандидатов.
- Не выбирай текущий recipe_id.
- НИКОГДА не выдумывай recipe_id.
- Верни СТРОГО JSON без markdown.

Формат JSON:
{{"recipe_id": 12}}

Кандидаты:
{json.dumps(candidate_recipes, ensure_ascii=False)}
""".strip()

    return await call_openrouter([
        {"role": "system", "content": "Ты очень строгий JSON API. Отвечай только валидным JSON."},
        {"role": "user", "content": prompt},
    ])
