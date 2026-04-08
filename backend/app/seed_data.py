import json
from .models import Recipe

RECIPES = [
    {
        "title": "Курица с рисом",
        "description": "Домашняя курица с рисом и луком.",
        "category": "main",
        "difficulty": "medium",
        "estimated_cost_rub": 420,
        "cooking_time_min": 45,
        "portions": 4,
        "protein_type": "chicken",
        "is_batch_friendly": True,
        "is_vegetarian": False,
        "is_vegan": False,
        "tags": "contains_chicken,high_protein",
        "ingredients": [
            {"name": "Куриное филе", "quantity": 700, "unit": "g"},
            {"name": "Рис", "quantity": 350, "unit": "g"},
            {"name": "Лук", "quantity": 150, "unit": "g"},
            {"name": "Масло", "quantity": 20, "unit": "ml"}
        ],
        "instructions": "Отвари рис. Обжарь лук и курицу. Смешай."
    },
    {
        "title": "Гречка с курицей",
        "description": "Гречка с кусочками курицы и луком.",
        "category": "main",
        "difficulty": "medium",
        "estimated_cost_rub": 390,
        "cooking_time_min": 40,
        "portions": 4,
        "protein_type": "chicken",
        "is_batch_friendly": True,
        "is_vegetarian": False,
        "is_vegan": False,
        "tags": "contains_chicken,high_protein",
        "ingredients": [
            {"name": "Куриное филе", "quantity": 650, "unit": "g"},
            {"name": "Гречка", "quantity": 350, "unit": "g"},
            {"name": "Лук", "quantity": 150, "unit": "g"},
            {"name": "Масло", "quantity": 20, "unit": "ml"}
        ],
        "instructions": "Отвари гречку. Обжарь лук и курицу. Смешай."
    },
    {
        "title": "Курица с картофельным пюре",
        "description": "Курица с мягким картофельным пюре.",
        "category": "main",
        "difficulty": "medium",
        "estimated_cost_rub": 430,
        "cooking_time_min": 55,
        "portions": 4,
        "protein_type": "chicken",
        "is_batch_friendly": True,
        "is_vegetarian": False,
        "is_vegan": False,
        "tags": "contains_chicken,high_protein",
        "ingredients": [
            {"name": "Куриное филе", "quantity": 650, "unit": "g"},
            {"name": "Картофель", "quantity": 1000, "unit": "g"},
            {"name": "Сметана", "quantity": 120, "unit": "g"},
            {"name": "Лук", "quantity": 120, "unit": "g"},
            {"name": "Масло", "quantity": 20, "unit": "ml"}
        ],
        "instructions": "Сделай пюре. Обжарь курицу с луком. Подавай вместе."
    },
    {
        "title": "Макароны с курицей и овощами",
        "description": "Паста с курицей и овощной смесью.",
        "category": "main",
        "difficulty": "medium",
        "estimated_cost_rub": 470,
        "cooking_time_min": 40,
        "portions": 4,
        "protein_type": "chicken",
        "is_batch_friendly": True,
        "is_vegetarian": False,
        "is_vegan": False,
        "tags": "contains_chicken,pasta,high_protein",
        "ingredients": [
            {"name": "Макароны", "quantity": 450, "unit": "g"},
            {"name": "Куриное филе", "quantity": 600, "unit": "g"},
            {"name": "Овощная смесь", "quantity": 400, "unit": "g"},
            {"name": "Масло", "quantity": 20, "unit": "ml"}
        ],
        "instructions": "Отвари макароны. Обжарь курицу и овощи. Смешай."
    },
    {
        "title": "Ризотто с курицей",
        "description": "Простое сливочное ризотто с курицей.",
        "category": "main",
        "difficulty": "medium",
        "estimated_cost_rub": 520,
        "cooking_time_min": 45,
        "portions": 4,
        "protein_type": "chicken",
        "is_batch_friendly": True,
        "is_vegetarian": False,
        "is_vegan": False,
        "tags": "contains_chicken,risotto",
        "ingredients": [
            {"name": "Рис", "quantity": 400, "unit": "g"},
            {"name": "Куриное филе", "quantity": 600, "unit": "g"},
            {"name": "Лук", "quantity": 150, "unit": "g"},
            {"name": "Сметана", "quantity": 100, "unit": "g"},
            {"name": "Масло", "quantity": 20, "unit": "ml"}
        ],
        "instructions": "Обжарь лук и курицу. Добавь рис и готовь до мягкости, вмешай сметану."
    },
    {
        "title": "Гуляш из говядины с картофелем",
        "description": "Тушёная говядина с картофелем и овощами.",
        "category": "main",
        "difficulty": "medium",
        "estimated_cost_rub": 760,
        "cooking_time_min": 80,
        "portions": 4,
        "protein_type": "beef",
        "is_batch_friendly": True,
        "is_vegetarian": False,
        "is_vegan": False,
        "tags": "contains_beef,stew,high_protein",
        "ingredients": [
            {"name": "Говядина", "quantity": 700, "unit": "g"},
            {"name": "Картофель", "quantity": 1000, "unit": "g"},
            {"name": "Лук", "quantity": 180, "unit": "g"},
            {"name": "Морковь", "quantity": 180, "unit": "g"},
            {"name": "Томатная паста", "quantity": 120, "unit": "g"},
            {"name": "Масло", "quantity": 20, "unit": "ml"}
        ],
        "instructions": "Обжарь мясо и овощи, добавь томатную пасту, туши до мягкости."
    },
    {
        "title": "Тушёная говядина с гречкой",
        "description": "Говядина в подливе с гречкой.",
        "category": "main",
        "difficulty": "medium",
        "estimated_cost_rub": 690,
        "cooking_time_min": 75,
        "portions": 4,
        "protein_type": "beef",
        "is_batch_friendly": True,
        "is_vegetarian": False,
        "is_vegan": False,
        "tags": "contains_beef,stew,high_protein",
        "ingredients": [
            {"name": "Говядина", "quantity": 650, "unit": "g"},
            {"name": "Гречка", "quantity": 350, "unit": "g"},
            {"name": "Лук", "quantity": 150, "unit": "g"},
            {"name": "Морковь", "quantity": 150, "unit": "g"},
            {"name": "Томатная паста", "quantity": 100, "unit": "g"},
            {"name": "Масло", "quantity": 20, "unit": "ml"}
        ],
        "instructions": "Туши говядину с овощами, подай с гречкой."
    },
    {
        "title": "Рис с говядиной и овощами",
        "description": "Сытный рис с говядиной и овощами.",
        "category": "main",
        "difficulty": "medium",
        "estimated_cost_rub": 710,
        "cooking_time_min": 60,
        "portions": 4,
        "protein_type": "beef",
        "is_batch_friendly": True,
        "is_vegetarian": False,
        "is_vegan": False,
        "tags": "contains_beef,high_protein",
        "ingredients": [
            {"name": "Говядина", "quantity": 650, "unit": "g"},
            {"name": "Рис", "quantity": 350, "unit": "g"},
            {"name": "Овощная смесь", "quantity": 400, "unit": "g"},
            {"name": "Лук", "quantity": 150, "unit": "g"},
            {"name": "Масло", "quantity": 20, "unit": "ml"}
        ],
        "instructions": "Обжарь мясо и овощи, приготовь рис, соедини."
    },
    {
        "title": "Свинина с картофелем",
        "description": "Жареная свинина с картофелем и луком.",
        "category": "main",
        "difficulty": "medium",
        "estimated_cost_rub": 520,
        "cooking_time_min": 50,
        "portions": 4,
        "protein_type": "pork",
        "is_batch_friendly": True,
        "is_vegetarian": False,
        "is_vegan": False,
        "tags": "contains_pork,high_protein",
        "ingredients": [
            {"name": "Свинина", "quantity": 650, "unit": "g"},
            {"name": "Картофель", "quantity": 1000, "unit": "g"},
            {"name": "Лук", "quantity": 150, "unit": "g"},
            {"name": "Морковь", "quantity": 150, "unit": "g"},
            {"name": "Масло", "quantity": 20, "unit": "ml"}
        ],
        "instructions": "Обжарь свинину, приготовь картофель, соедини с овощами."
    },
    {
        "title": "Рис со свининой и морковью",
        "description": "Сытный рис со свининой, морковью и луком.",
        "category": "main",
        "difficulty": "medium",
        "estimated_cost_rub": 490,
        "cooking_time_min": 45,
        "portions": 4,
        "protein_type": "pork",
        "is_batch_friendly": True,
        "is_vegetarian": False,
        "is_vegan": False,
        "tags": "contains_pork,high_protein",
        "ingredients": [
            {"name": "Свинина", "quantity": 600, "unit": "g"},
            {"name": "Рис", "quantity": 350, "unit": "g"},
            {"name": "Морковь", "quantity": 180, "unit": "g"},
            {"name": "Лук", "quantity": 150, "unit": "g"},
            {"name": "Масло", "quantity": 20, "unit": "ml"}
        ],
        "instructions": "Отвари рис. Обжарь свинину с овощами. Смешай."
    },
    {
        "title": "Макароны со свиным гуляшом",
        "description": "Макароны с быстрым гуляшом из свинины.",
        "category": "main",
        "difficulty": "medium",
        "estimated_cost_rub": 540,
        "cooking_time_min": 50,
        "portions": 4,
        "protein_type": "pork",
        "is_batch_friendly": True,
        "is_vegetarian": False,
        "is_vegan": False,
        "tags": "contains_pork,pasta,high_protein",
        "ingredients": [
            {"name": "Макароны", "quantity": 450, "unit": "g"},
            {"name": "Свинина", "quantity": 600, "unit": "g"},
            {"name": "Лук", "quantity": 150, "unit": "g"},
            {"name": "Томатная паста", "quantity": 120, "unit": "g"},
            {"name": "Масло", "quantity": 20, "unit": "ml"}
        ],
        "instructions": "Отвари макароны. Обжарь свинину с луком и томатной пастой."
    },
    {
        "title": "Макароны с домашним фаршем",
        "description": "Паста с домашним фаршем и томатной основой.",
        "category": "main",
        "difficulty": "medium",
        "estimated_cost_rub": 560,
        "cooking_time_min": 45,
        "portions": 4,
        "protein_type": "mince",
        "is_batch_friendly": True,
        "is_vegetarian": False,
        "is_vegan": False,
        "tags": "contains_beef,contains_pork,pasta,mince",
        "ingredients": [
            {"name": "Макароны", "quantity": 450, "unit": "g"},
            {"name": "Домашний фарш", "quantity": 650, "unit": "g"},
            {"name": "Лук", "quantity": 150, "unit": "g"},
            {"name": "Томатная паста", "quantity": 120, "unit": "g"},
            {"name": "Масло", "quantity": 20, "unit": "ml"}
        ],
        "instructions": "Отвари макароны. Обжарь фарш с луком, добавь томатную пасту."
    },
    {
        "title": "Болоньезе",
        "description": "Паста болоньезе с говяжьим фаршем.",
        "category": "main",
        "difficulty": "medium",
        "estimated_cost_rub": 610,
        "cooking_time_min": 50,
        "portions": 4,
        "protein_type": "mince",
        "is_batch_friendly": True,
        "is_vegetarian": False,
        "is_vegan": False,
        "tags": "contains_beef,pasta,mince",
        "ingredients": [
            {"name": "Макароны", "quantity": 450, "unit": "g"},
            {"name": "Говяжий фарш", "quantity": 650, "unit": "g"},
            {"name": "Лук", "quantity": 150, "unit": "g"},
            {"name": "Морковь", "quantity": 120, "unit": "g"},
            {"name": "Томатная паста", "quantity": 140, "unit": "g"},
            {"name": "Масло", "quantity": 20, "unit": "ml"}
        ],
        "instructions": "Обжарь фарш с овощами, добавь томатную пасту, подай с макаронами."
    },
    {
        "title": "Тефтели с рисом",
        "description": "Тефтели из фарша с рисом и подливой.",
        "category": "main",
        "difficulty": "medium",
        "estimated_cost_rub": 590,
        "cooking_time_min": 60,
        "portions": 4,
        "protein_type": "mince",
        "is_batch_friendly": True,
        "is_vegetarian": False,
        "is_vegan": False,
        "tags": "contains_beef,contains_pork,mince,high_protein",
        "ingredients": [
            {"name": "Домашний фарш", "quantity": 650, "unit": "g"},
            {"name": "Рис", "quantity": 350, "unit": "g"},
            {"name": "Лук", "quantity": 150, "unit": "g"},
            {"name": "Томатная паста", "quantity": 120, "unit": "g"},
            {"name": "Масло", "quantity": 20, "unit": "ml"}
        ],
        "instructions": "Сделай тефтели, потуши в подливе, подай с рисом."
    },
    {
        "title": "Котлеты с картофельным пюре",
        "description": "Классические котлеты с пюре.",
        "category": "main",
        "difficulty": "medium",
        "estimated_cost_rub": 610,
        "cooking_time_min": 60,
        "portions": 4,
        "protein_type": "mince",
        "is_batch_friendly": True,
        "is_vegetarian": False,
        "is_vegan": False,
        "tags": "contains_pork,contains_beef,mince",
        "ingredients": [
            {"name": "Домашний фарш", "quantity": 700, "unit": "g"},
            {"name": "Картофель", "quantity": 1000, "unit": "g"},
            {"name": "Лук", "quantity": 120, "unit": "g"},
            {"name": "Сметана", "quantity": 100, "unit": "g"},
            {"name": "Масло", "quantity": 20, "unit": "ml"}
        ],
        "instructions": "Сделай котлеты, приготовь пюре, подай вместе."
    },
    {
        "title": "Ленивые голубцы",
        "description": "Фарш, рис и капуста в одной большой сковороде.",
        "category": "main",
        "difficulty": "medium",
        "estimated_cost_rub": 560,
        "cooking_time_min": 55,
        "portions": 4,
        "protein_type": "mince",
        "is_batch_friendly": True,
        "is_vegetarian": False,
        "is_vegan": False,
        "tags": "contains_pork,contains_beef,mince",
        "ingredients": [
            {"name": "Домашний фарш", "quantity": 650, "unit": "g"},
            {"name": "Рис", "quantity": 250, "unit": "g"},
            {"name": "Капуста", "quantity": 500, "unit": "g"},
            {"name": "Лук", "quantity": 120, "unit": "g"},
            {"name": "Томатная паста", "quantity": 100, "unit": "g"},
            {"name": "Масло", "quantity": 20, "unit": "ml"}
        ],
        "instructions": "Обжарь фарш, добавь рис и капусту, туши до готовности."
    },
    {
        "title": "Фаршированные перцы",
        "description": "Перцы с фаршем и рисом.",
        "category": "main",
        "difficulty": "medium",
        "estimated_cost_rub": 650,
        "cooking_time_min": 70,
        "portions": 4,
        "protein_type": "mince",
        "is_batch_friendly": True,
        "is_vegetarian": False,
        "is_vegan": False,
        "tags": "contains_pork,contains_beef,mince",
        "ingredients": [
            {"name": "Домашний фарш", "quantity": 650, "unit": "g"},
            {"name": "Рис", "quantity": 250, "unit": "g"},
            {"name": "Болгарский перец", "quantity": 600, "unit": "g"},
            {"name": "Лук", "quantity": 120, "unit": "g"},
            {"name": "Томатная паста", "quantity": 100, "unit": "g"}
        ],
        "instructions": "Начини перцы фаршем с рисом и туши до готовности."
    },
    {
        "title": "Гречка с фаршем",
        "description": "Гречка с обжаренным фаршем и луком.",
        "category": "main",
        "difficulty": "easy",
        "estimated_cost_rub": 520,
        "cooking_time_min": 40,
        "portions": 4,
        "protein_type": "mince",
        "is_batch_friendly": True,
        "is_vegetarian": False,
        "is_vegan": False,
        "tags": "contains_pork,contains_beef,mince",
        "ingredients": [
            {"name": "Домашний фарш", "quantity": 600, "unit": "g"},
            {"name": "Гречка", "quantity": 350, "unit": "g"},
            {"name": "Лук", "quantity": 120, "unit": "g"},
            {"name": "Масло", "quantity": 20, "unit": "ml"}
        ],
        "instructions": "Отвари гречку. Обжарь фарш с луком. Смешай."
    },
    {
        "title": "Ризотто с грибами",
        "description": "Простое грибное ризотто.",
        "category": "main",
        "difficulty": "medium",
        "estimated_cost_rub": 360,
        "cooking_time_min": 40,
        "portions": 4,
        "protein_type": "vegetarian",
        "is_batch_friendly": True,
        "is_vegetarian": True,
        "is_vegan": False,
        "tags": "vegetarian,risotto",
        "ingredients": [
            {"name": "Рис", "quantity": 400, "unit": "g"},
            {"name": "Шампиньоны", "quantity": 400, "unit": "g"},
            {"name": "Лук", "quantity": 150, "unit": "g"},
            {"name": "Сметана", "quantity": 100, "unit": "g"},
            {"name": "Масло", "quantity": 20, "unit": "ml"}
        ],
        "instructions": "Обжарь грибы с луком, добавь рис и доведи до готовности, вмешай сметану."
    },
    {
        "title": "Рис с овощами",
        "description": "Рис с овощами на одной сковороде.",
        "category": "main",
        "difficulty": "easy",
        "estimated_cost_rub": 250,
        "cooking_time_min": 35,
        "portions": 4,
        "protein_type": "vegan",
        "is_batch_friendly": True,
        "is_vegetarian": True,
        "is_vegan": True,
        "tags": "vegan,vegetarian",
        "ingredients": [
            {"name": "Рис", "quantity": 400, "unit": "g"},
            {"name": "Овощная смесь", "quantity": 450, "unit": "g"},
            {"name": "Лук", "quantity": 120, "unit": "g"},
            {"name": "Масло", "quantity": 20, "unit": "ml"}
        ],
        "instructions": "Обжарь овощи и лук, добавь рис и готовь до мягкости."
    },
    {
        "title": "Гречка с грибами",
        "description": "Гречка с грибами и луком.",
        "category": "main",
        "difficulty": "easy",
        "estimated_cost_rub": 290,
        "cooking_time_min": 35,
        "portions": 4,
        "protein_type": "vegan",
        "is_batch_friendly": True,
        "is_vegetarian": True,
        "is_vegan": True,
        "tags": "vegan,vegetarian",
        "ingredients": [
            {"name": "Гречка", "quantity": 400, "unit": "g"},
            {"name": "Шампиньоны", "quantity": 400, "unit": "g"},
            {"name": "Лук", "quantity": 120, "unit": "g"},
            {"name": "Масло", "quantity": 20, "unit": "ml"}
        ],
        "instructions": "Отвари гречку. Обжарь грибы с луком и смешай."
    },
    {
        "title": "Овощное рагу с картофелем",
        "description": "Тушёные овощи с картофелем.",
        "category": "main",
        "difficulty": "easy",
        "estimated_cost_rub": 280,
        "cooking_time_min": 45,
        "portions": 4,
        "protein_type": "vegan",
        "is_batch_friendly": True,
        "is_vegetarian": True,
        "is_vegan": True,
        "tags": "vegan,vegetarian",
        "ingredients": [
            {"name": "Картофель", "quantity": 900, "unit": "g"},
            {"name": "Капуста", "quantity": 400, "unit": "g"},
            {"name": "Морковь", "quantity": 150, "unit": "g"},
            {"name": "Лук", "quantity": 120, "unit": "g"},
            {"name": "Масло", "quantity": 20, "unit": "ml"}
        ],
        "instructions": "Нарежь овощи и туши до мягкости."
    },
    {
        "title": "Макароны с овощами и томатным соусом",
        "description": "Простая веганская паста с овощами.",
        "category": "main",
        "difficulty": "easy",
        "estimated_cost_rub": 300,
        "cooking_time_min": 30,
        "portions": 4,
        "protein_type": "vegan",
        "is_batch_friendly": True,
        "is_vegetarian": True,
        "is_vegan": True,
        "tags": "vegan,vegetarian,pasta",
        "ingredients": [
            {"name": "Макароны", "quantity": 450, "unit": "g"},
            {"name": "Овощная смесь", "quantity": 400, "unit": "g"},
            {"name": "Томатная паста", "quantity": 100, "unit": "g"},
            {"name": "Масло", "quantity": 20, "unit": "ml"}
        ],
        "instructions": "Отвари макароны. Обжарь овощи, добавь томатную пасту и смешай."
    },
    {
        "title": "Чечевица с рисом",
        "description": "Сытная чечевица с рисом.",
        "category": "main",
        "difficulty": "easy",
        "estimated_cost_rub": 310,
        "cooking_time_min": 40,
        "portions": 4,
        "protein_type": "vegan",
        "is_batch_friendly": True,
        "is_vegetarian": True,
        "is_vegan": True,
        "tags": "vegan,vegetarian,legumes",
        "ingredients": [
            {"name": "Чечевица", "quantity": 350, "unit": "g"},
            {"name": "Рис", "quantity": 250, "unit": "g"},
            {"name": "Лук", "quantity": 120, "unit": "g"},
            {"name": "Морковь", "quantity": 120, "unit": "g"},
            {"name": "Масло", "quantity": 20, "unit": "ml"}
        ],
        "instructions": "Отвари чечевицу и рис, соедини с обжаренными овощами."
    },
    {
        "title": "Фасоль с овощами",
        "description": "Тушёная фасоль с овощами.",
        "category": "main",
        "difficulty": "easy",
        "estimated_cost_rub": 330,
        "cooking_time_min": 35,
        "portions": 4,
        "protein_type": "vegan",
        "is_batch_friendly": True,
        "is_vegetarian": True,
        "is_vegan": True,
        "tags": "vegan,vegetarian,legumes",
        "ingredients": [
            {"name": "Фасоль", "quantity": 400, "unit": "g"},
            {"name": "Овощная смесь", "quantity": 400, "unit": "g"},
            {"name": "Лук", "quantity": 120, "unit": "g"},
            {"name": "Томатная паста", "quantity": 100, "unit": "g"},
            {"name": "Масло", "quantity": 20, "unit": "ml"}
        ],
        "instructions": "Туши фасоль с овощами и томатной пастой."
    },
    {
        "title": "Салат из капусты и моркови",
        "description": "Простой свежий салат.",
        "category": "salad",
        "difficulty": "easy",
        "estimated_cost_rub": 110,
        "cooking_time_min": 15,
        "portions": 4,
        "protein_type": "vegan",
        "is_batch_friendly": True,
        "is_vegetarian": True,
        "is_vegan": True,
        "tags": "vegan,vegetarian,salad",
        "ingredients": [
            {"name": "Капуста", "quantity": 500, "unit": "g"},
            {"name": "Морковь", "quantity": 200, "unit": "g"},
            {"name": "Масло", "quantity": 15, "unit": "ml"}
        ],
        "instructions": "Нашинкуй капусту, натри морковь, заправь."
    },
    {
        "title": "Салат огурец-помидор",
        "description": "Классический лёгкий салат.",
        "category": "salad",
        "difficulty": "easy",
        "estimated_cost_rub": 180,
        "cooking_time_min": 10,
        "portions": 4,
        "protein_type": "vegan",
        "is_batch_friendly": True,
        "is_vegetarian": True,
        "is_vegan": True,
        "tags": "vegan,vegetarian,salad",
        "ingredients": [
            {"name": "Огурец", "quantity": 300, "unit": "g"},
            {"name": "Помидор", "quantity": 400, "unit": "g"},
            {"name": "Масло", "quantity": 15, "unit": "ml"}
        ],
        "instructions": "Нарежь овощи, заправь."
    },
    {
        "title": "Винегрет",
        "description": "Свекольный салат с картофелем и огурцом.",
        "category": "salad",
        "difficulty": "easy",
        "estimated_cost_rub": 170,
        "cooking_time_min": 25,
        "portions": 4,
        "protein_type": "vegan",
        "is_batch_friendly": True,
        "is_vegetarian": True,
        "is_vegan": True,
        "tags": "vegan,vegetarian,salad",
        "ingredients": [
            {"name": "Свекла", "quantity": 300, "unit": "g"},
            {"name": "Картофель", "quantity": 250, "unit": "g"},
            {"name": "Морковь", "quantity": 150, "unit": "g"},
            {"name": "Огурец соленый", "quantity": 150, "unit": "g"},
            {"name": "Масло", "quantity": 15, "unit": "ml"}
        ],
        "instructions": "Отвари овощи, нарежь и смешай."
    },
    {
        "title": "Салат с фасолью и кукурузой",
        "description": "Сытный салат на пару дней.",
        "category": "salad",
        "difficulty": "easy",
        "estimated_cost_rub": 190,
        "cooking_time_min": 15,
        "portions": 4,
        "protein_type": "vegan",
        "is_batch_friendly": True,
        "is_vegetarian": True,
        "is_vegan": True,
        "tags": "vegan,vegetarian,salad,legumes",
        "ingredients": [
            {"name": "Фасоль", "quantity": 250, "unit": "g"},
            {"name": "Кукуруза", "quantity": 200, "unit": "g"},
            {"name": "Огурец", "quantity": 200, "unit": "g"},
            {"name": "Масло", "quantity": 15, "unit": "ml"}
        ],
        "instructions": "Смешай ингредиенты и заправь."
    },
    {
        "title": "Морковный салат с чесноком",
        "description": "Яркий бюджетный салат.",
        "category": "salad",
        "difficulty": "easy",
        "estimated_cost_rub": 90,
        "cooking_time_min": 10,
        "portions": 4,
        "protein_type": "vegan",
        "is_batch_friendly": True,
        "is_vegetarian": True,
        "is_vegan": True,
        "tags": "vegan,vegetarian,salad",
        "ingredients": [
            {"name": "Морковь", "quantity": 400, "unit": "g"},
            {"name": "Чеснок", "quantity": 20, "unit": "g"},
            {"name": "Масло", "quantity": 15, "unit": "ml"}
        ],
        "instructions": "Натри морковь, добавь чеснок и масло."
    },
    {
        "title": "Свекольный салат",
        "description": "Свекла с чесноком и маслом.",
        "category": "salad",
        "difficulty": "easy",
        "estimated_cost_rub": 100,
        "cooking_time_min": 15,
        "portions": 4,
        "protein_type": "vegan",
        "is_batch_friendly": True,
        "is_vegetarian": True,
        "is_vegan": True,
        "tags": "vegan,vegetarian,salad",
        "ingredients": [
            {"name": "Свекла", "quantity": 400, "unit": "g"},
            {"name": "Чеснок", "quantity": 20, "unit": "g"},
            {"name": "Масло", "quantity": 15, "unit": "ml"}
        ],
        "instructions": "Натри свеклу, добавь чеснок и масло."
    }
]

def seed_recipes(db):
    if db.query(Recipe).count() > 0:
        return

    for item in RECIPES:
        db.add(
            Recipe(
                title=item["title"],
                description=item["description"],
                category=item["category"],
                difficulty=item["difficulty"],
                estimated_cost_rub=item["estimated_cost_rub"],
                cooking_time_min=item["cooking_time_min"],
                portions=item["portions"],
                protein_type=item["protein_type"],
                is_batch_friendly=item["is_batch_friendly"],
                is_vegetarian=item["is_vegetarian"],
                is_vegan=item["is_vegan"],
                tags=item["tags"],
                ingredients_json=json.dumps(item["ingredients"], ensure_ascii=False),
                instructions=item["instructions"],
            )
        )

    db.commit()
