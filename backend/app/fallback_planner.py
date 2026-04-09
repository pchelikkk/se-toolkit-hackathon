from .price_catalog import MEAL_MODES

def _score_recipe(recipe, pantry_items, user_note):
    pantry_names = {str(item.get("name", "")).strip().lower() for item in pantry_items or []}
    note = (user_note or "").lower()

    recipe_text = " ".join([
        str(recipe.get("title", "")).lower(),
        str(recipe.get("description", "")).lower(),
        " ".join(str(i.get("name", "")).lower() for i in recipe.get("ingredients", [])),
    ])

    score = 0

    for pantry_name in pantry_names:
        if pantry_name and pantry_name in recipe_text:
            score += 3

    for token in note.split():
        token = token.strip(",.!?;:()[]{}\"'").lower()
        if len(token) >= 4 and token in recipe_text:
            score += 5

    return score

def build_fallback_plan(recipes, budget_rub, days, meal_mode, pantry_items, user_note):
    mode = MEAL_MODES[meal_mode]
    main_per_day = mode["main_per_day"]
    salad_per_day = mode["salad_per_day"]

    mains = [r for r in recipes if r.get("category") != "salad"]
    salads = [r for r in recipes if r.get("category") == "salad"]

    mains = sorted(
        mains,
        key=lambda r: (-_score_recipe(r, pantry_items, user_note), r.get("estimated_cost_rub", 10**9))
    )
    salads = sorted(
        salads,
        key=lambda r: (-_score_recipe(r, pantry_items, user_note), r.get("estimated_cost_rub", 10**9))
    )

    selected = []
    covered_main = 0

    for recipe in mains:
        if covered_main >= days * main_per_day:
            break
        selected.append(recipe)
        covered_main += int(recipe.get("portions", 1) or 1)

    covered_salad = 0
    for recipe in salads:
        if covered_salad >= days * salad_per_day:
            break
        if salad_per_day > 0:
            selected.append(recipe)
            covered_salad += int(recipe.get("portions", 1) or 1)

    # try to stay in budget by trimming expensive extras first
    total_cost = round(sum(float(r.get("estimated_cost_rub", 0)) for r in selected), 2)
    while total_cost > budget_rub and len(selected) > 1:
        removable = sorted(selected, key=lambda r: float(r.get("estimated_cost_rub", 0)), reverse=True)
        removed = removable[0]
        selected.remove(removed)
        total_cost = round(sum(float(r.get("estimated_cost_rub", 0)) for r in selected), 2)

    # rebuild selected groups
    selected_main = [r for r in selected if r.get("category") != "salad"]
    selected_salad = [r for r in selected if r.get("category") == "salad"]

    # if trimming broke minimum coverage, re-add cheapest matching recipes
    covered_main = sum(int(r.get("portions", 1) or 1) for r in selected_main)
    if covered_main < days * main_per_day:
        for recipe in sorted(mains, key=lambda r: r.get("estimated_cost_rub", 10**9)):
            if recipe in selected_main:
                continue
            selected_main.append(recipe)
            total_cost += float(recipe.get("estimated_cost_rub", 0))
            covered_main += int(recipe.get("portions", 1) or 1)
            if covered_main >= days * main_per_day:
                break

    covered_salad = sum(int(r.get("portions", 1) or 1) for r in selected_salad)
    if salad_per_day > 0 and covered_salad < days * salad_per_day:
        for recipe in sorted(salads, key=lambda r: r.get("estimated_cost_rub", 10**9)):
            if recipe in selected_salad:
                continue
            selected_salad.append(recipe)
            total_cost += float(recipe.get("estimated_cost_rub", 0))
            covered_salad += int(recipe.get("portions", 1) or 1)
            if covered_salad >= days * salad_per_day:
                break

    main_slots = []
    for recipe in selected_main:
        main_slots.extend([recipe["id"]] * int(recipe.get("portions", 1) or 1))
    main_slots = main_slots[: days * main_per_day]

    salad_slots = []
    for recipe in selected_salad:
        salad_slots.extend([recipe["id"]] * int(recipe.get("portions", 1) or 1))
    salad_slots = salad_slots[: days * salad_per_day]

    schedule = []
    main_index = 0
    salad_index = 0

    for day in range(1, days + 1):
        recipe_ids = []

        for _ in range(main_per_day):
            if main_index < len(main_slots):
                recipe_ids.append(main_slots[main_index])
                main_index += 1

        for _ in range(salad_per_day):
            if salad_index < len(salad_slots):
                recipe_ids.append(salad_slots[salad_index])
                salad_index += 1

        schedule.append({
            "day_number": day,
            "recipe_ids": recipe_ids,
        })

    batches = []
    seen = set()
    batch_number = 1
    for recipe in selected_main + selected_salad:
        if recipe["id"] in seen:
            continue
        seen.add(recipe["id"])
        batches.append({
            "batch_number": batch_number,
            "recipe_id": recipe["id"],
        })
        batch_number += 1

    return {
        "reasoning": "Fallback planner was used because the external LLM was unavailable or returned an invalid plan.",
        "batches": batches,
        "schedule": schedule,
        "total_cost_rub": round(sum(float(r.get("estimated_cost_rub", 0)) for r in selected_main + selected_salad), 2),
    }
