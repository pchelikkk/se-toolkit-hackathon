import { useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

const translations = {
  ru: {
    appName: "BudgetBites",
    login: "Вход",
    register: "Регистрация",
    email: "Почта",
    password: "Пароль",
    logout: "Выйти",
    menuMain: "Главная",
    menuHistory: "История",
    menuFavorites: "Избранное",
    menuAccount: "Аккаунт",
    budget: "Бюджет (₽)",
    days: "Дней",
    mealMode: "Режим питания",
    filters: "Фильтры",
    pantry: "Что уже есть дома",
    addProduct: "Добавить продукт",
    remove: "Удалить",
    quantity: "Кол-во",
    note: "Комментарий к плану",
    notePlaceholder:
      "Например: хочу больше курицы, меньше тяжёлых блюд, люблю рис, не хочу очень долго готовить",
    pricesTitle: "Справочные цены",
    pricesSubtitle:
      "Ниже указаны ориентировочные цены, используемые для расчёта. При необходимости скорректируйте значения с учётом актуальных цен в вашем магазине.",
    updatedAt: "Дата обновления цен",
    generate: "Сформировать план",
    generating: "Формируем персональный план питания",
    generatingSub:
      "Мы подбираем batch-блюда, проверяем бюджет и учитываем ваши фильтры. Это может занять несколько секунд.",
    plan: "План",
    batchDishes: "Batch-блюда",
    schedule: "План по дням",
    missing: "Чего не хватает",
    regenerate: "Пересобрать план",
    replace: "Заменить",
    favoriteAdd: "В избранное",
    favoriteRemove: "Убрать из избранного",
    historyTitle: "История",
    favoritesTitle: "Избранное",
    accountTitle: "Аккаунт",
    accountText:
      "Здесь можно управлять учётной записью, а также перейти в историю и избранное.",
    goHistory: "Открыть историю",
    goFavorites: "Открыть избранное",
    goMain: "На главный экран",
    noMissing: "Все нужные продукты уже есть дома.",
    loading: "Загрузка...",
    officialHeader:
      "Планирование питания с учётом бюджета, запасов дома и пользовательских предпочтений.",
    authSubtitle:
      "Создайте учётную запись или войдите, чтобы сохранять планы, историю и избранное.",
    commentAgent: "Комментарий агента",
    commentUser: "Комментарий пользователя",
    createdAt: "Создано",
    noData: "Пока ничего нет.",
    invalid: "Произошла ошибка.",
    filtersNoPork: "Без свинины",
    filtersNoBeef: "Без говядины",
    filtersVegetarian: "Вегетарианское",
    filtersVegan: "Веганское",
    authSwitchLogin: "Уже есть аккаунт? Войти",
    authSwitchRegister: "Нет аккаунта? Зарегистрироваться",
    product: "Продукт",
    unit: "Ед.",
    mainCategory: "основное",
    saladCategory: "салат",
    day: "День",
    portions: "порц.",
    minutes: "мин",
  },
  en: {
    appName: "BudgetBites",
    login: "Sign in",
    register: "Create account",
    email: "Email",
    password: "Password",
    logout: "Log out",
    menuMain: "Dashboard",
    menuHistory: "History",
    menuFavorites: "Favorites",
    menuAccount: "Account",
    budget: "Budget (₽)",
    days: "Days",
    mealMode: "Meal mode",
    filters: "Filters",
    pantry: "Available at home",
    addProduct: "Add product",
    remove: "Remove",
    quantity: "Qty",
    note: "Plan comment",
    notePlaceholder:
      "For example: more chicken, fewer heavy meals, I like rice, I do not want very long cooking time",
    pricesTitle: "Reference prices",
    pricesSubtitle:
      "The reference prices below are used for calculation purposes. Please review and adjust them if needed to reflect current prices in your local store.",
    updatedAt: "Price update date",
    generate: "Generate plan",
    generating: "Generating your personalized meal plan",
    generatingSub:
      "We are selecting batch-friendly dishes, checking the budget, and applying your filters. This may take a few seconds.",
    plan: "Plan",
    batchDishes: "Batch dishes",
    schedule: "Schedule",
    missing: "Missing ingredients",
    regenerate: "Regenerate plan",
    replace: "Replace",
    favoriteAdd: "Add to favorites",
    favoriteRemove: "Remove from favorites",
    historyTitle: "History",
    favoritesTitle: "Favorites",
    accountTitle: "Account",
    accountText:
      "Manage your account and quickly navigate to history or favorites.",
    goHistory: "Open history",
    goFavorites: "Open favorites",
    goMain: "Go to dashboard",
    noMissing: "You already have all required ingredients at home.",
    loading: "Loading...",
    officialHeader:
      "Meal planning based on budget, pantry items already available at home, and user preferences.",
    authSubtitle:
      "Create an account or sign in to save meal plans, history, and favorites.",
    commentAgent: "Assistant note",
    commentUser: "User note",
    createdAt: "Created",
    noData: "Nothing here yet.",
    invalid: "Something went wrong.",
    filtersNoPork: "No pork",
    filtersNoBeef: "No beef",
    filtersVegetarian: "Vegetarian",
    filtersVegan: "Vegan",
    authSwitchLogin: "Already have an account? Sign in",
    authSwitchRegister: "No account yet? Create one",
    product: "Product",
    unit: "Unit",
    mainCategory: "main",
    saladCategory: "salad",
    day: "Day",
    portions: "portions",
    minutes: "min",
  },
};

const recipeTitleMap = {
  "Курица с рисом": "Chicken with Rice",
  "Гречка с курицей": "Buckwheat with Chicken",
  "Курица с картофельным пюре": "Chicken with Mashed Potatoes",
  "Макароны с курицей и овощами": "Pasta with Chicken and Vegetables",
  "Ризотто с курицей": "Chicken Risotto",
  "Гуляш из говядины с картофелем": "Beef Goulash with Potatoes",
  "Тушёная говядина с гречкой": "Stewed Beef with Buckwheat",
  "Рис с говядиной и овощами": "Rice with Beef and Vegetables",
  "Свинина с картофелем": "Pork with Potatoes",
  "Рис со свининой и морковью": "Rice with Pork and Carrots",
  "Макароны со свиным гуляшом": "Pasta with Pork Goulash",
  "Макароны с домашним фаршем": "Pasta with Mixed Mince",
  "Болоньезе": "Bolognese",
  "Тефтели с рисом": "Meatballs with Rice",
  "Котлеты с картофельным пюре": "Cutlets with Mashed Potatoes",
  "Ленивые голубцы": "Lazy Cabbage Rolls",
  "Фаршированные перцы": "Stuffed Peppers",
  "Гречка с фаршем": "Buckwheat with Mince",
  "Ризотто с грибами": "Mushroom Risotto",
  "Рис с овощами": "Rice with Vegetables",
  "Гречка с грибами": "Buckwheat with Mushrooms",
  "Овощное рагу с картофелем": "Vegetable Stew with Potatoes",
  "Макароны с овощами и томатным соусом": "Pasta with Vegetables and Tomato Sauce",
  "Чечевица с рисом": "Lentils with Rice",
  "Фасоль с овощами": "Beans with Vegetables",
  "Салат из капусты и моркови": "Cabbage and Carrot Salad",
  "Салат огурец-помидор": "Cucumber and Tomato Salad",
  "Винегрет": "Vinaigrette Salad",
  "Салат с фасолью и кукурузой": "Bean and Corn Salad",
  "Морковный салат с чесноком": "Carrot Salad with Garlic",
  "Свекольный салат": "Beet Salad",
};

const recipeDescriptionMap = {
  "Домашняя курица с рисом и луком.": "Homestyle chicken with rice and onion.",
  "Гречка с кусочками курицы и луком.": "Buckwheat with chicken pieces and onion.",
  "Курица с мягким картофельным пюре.": "Chicken with soft mashed potatoes.",
  "Паста с курицей и овощной смесью.": "Pasta with chicken and mixed vegetables.",
  "Простое сливочное ризотто с курицей.": "Simple creamy risotto with chicken.",
  "Тушёная говядина с картофелем и овощами.": "Stewed beef with potatoes and vegetables.",
  "Говядина в подливе с гречкой.": "Beef in gravy with buckwheat.",
  "Сытный рис с говядиной и овощами.": "Hearty rice with beef and vegetables.",
  "Жареная свинина с картофелем и луком.": "Fried pork with potatoes and onion.",
  "Сытный рис со свининой, морковью и луком.": "Hearty rice with pork, carrots, and onion.",
  "Макароны с быстрым гуляшом из свинины.": "Pasta with quick pork goulash.",
  "Паста с домашним фаршем и томатной основой.": "Pasta with mixed mince and tomato base.",
  "Паста болоньезе с говяжьим фаршем.": "Bolognese pasta with beef mince.",
  "Тефтели из фарша с рисом и подливой.": "Minced meatballs with rice and gravy.",
  "Классические котлеты с пюре.": "Classic cutlets with mashed potatoes.",
  "Фарш, рис и капуста в одной большой сковороде.": "Mince, rice, and cabbage in one large pan.",
  "Перцы с фаршем и рисом.": "Peppers stuffed with mince and rice.",
  "Гречка с обжаренным фаршем и луком.": "Buckwheat with fried mince and onion.",
  "Простое грибное ризотто.": "Simple mushroom risotto.",
  "Рис с овощами на одной сковороде.": "Rice with vegetables in one pan.",
  "Гречка с грибами и луком.": "Buckwheat with mushrooms and onion.",
  "Тушёные овощи с картофелем.": "Stewed vegetables with potatoes.",
  "Простая веганская паста с овощами.": "Simple vegan pasta with vegetables.",
  "Сытная чечевица с рисом.": "Hearty lentils with rice.",
  "Тушёная фасоль с овощами.": "Stewed beans with vegetables.",
  "Простой свежий салат.": "Simple fresh salad.",
  "Классический лёгкий салат.": "Classic light salad.",
  "Свекольный салат с картофелем и огурцом.": "Beet salad with potatoes and pickles.",
  "Сытный салат на пару дней.": "A hearty salad for a few days.",
  "Яркий бюджетный салат.": "A bright budget-friendly salad.",
  "Свекла с чесноком и маслом.": "Beetroot with garlic and oil.",
};

const ingredientMap = {
  "Куриное филе": "Chicken fillet",
  "Рис": "Rice",
  "Лук": "Onion",
  "Масло": "Oil",
  "Гречка": "Buckwheat",
  "Картофель": "Potatoes",
  "Сметана": "Sour cream",
  "Овощная смесь": "Mixed vegetables",
  "Говядина": "Beef",
  "Морковь": "Carrot",
  "Томатная паста": "Tomato paste",
  "Свинина": "Pork",
  "Домашний фарш": "Mixed mince",
  "Говяжий фарш": "Beef mince",
  "Капуста": "Cabbage",
  "Болгарский перец": "Bell pepper",
  "Шампиньоны": "Champignons",
  "Чечевица": "Lentils",
  "Фасоль": "Beans",
  "Свекла": "Beetroot",
  "Огурец": "Cucumber",
  "Помидор": "Tomato",
  "Огурец соленый": "Pickled cucumber",
  "Кукуруза": "Corn",
  "Чеснок": "Garlic",
  "Макароны": "Pasta",
};

function parseResponse(response) {
  return response.text().then((text) => {
    if (!text) return {};
    try {
      return JSON.parse(text);
    } catch {
      return { detail: text };
    }
  });
}

function getErrorMessage(data, fallback) {
  if (!data) return fallback;

  if (typeof data === "string") return data;

  if (typeof data.detail === "string") return data.detail;

  if (Array.isArray(data.detail)) {
    return data.detail
      .map((item) => {
        if (typeof item === "string") return item;
        if (item?.msg && item?.loc) {
          const where = Array.isArray(item.loc) ? item.loc.join(" -> ") : String(item.loc);
          return `${where}: ${item.msg}`;
        }
        if (item?.msg) return item.msg;
        return JSON.stringify(item);
      })
      .join("; ");
  }

  if (typeof data.detail === "object") {
    try {
      return JSON.stringify(data.detail);
    } catch {
      return fallback;
    }
  }

  try {
    return JSON.stringify(data);
  } catch {
    return fallback;
  }
}

function translateValue(lang, value, map) {
  if (lang === "ru") return value;
  return map[value] || value;
}

function translateRecipe(lang, recipe) {
  if (lang === "ru") return recipe;
  return {
    ...recipe,
    title: recipeTitleMap[recipe.title] || recipe.title,
    description: recipeDescriptionMap[recipe.description] || recipe.description,
    category: recipe.category === "salad" ? "salad" : "main",
    ingredients: recipe.ingredients
      ? recipe.ingredients.map((item) => ({
          ...item,
          name: ingredientMap[item.name] || item.name,
        }))
      : recipe.ingredients,
  };
}

function translateMissingIngredient(lang, item) {
  if (lang === "ru") return item;
  return {
    ...item,
    name: ingredientMap[item.name] || item.name,
  };
}

function translatePantryLabel(lang, name) {
  return lang === "ru" ? name : ingredientMap[name] || name;
}

function translateUnitLabel(lang, unitLabel) {
  if (lang === "ru") return unitLabel;

  const mapping = {
    "₽/кг": "RUB/kg",
    "₽/л": "RUB/L",
    "₽/шт": "RUB/pc",
  };

  return mapping[unitLabel] || unitLabel;
}

function translateSummary(lang, summary) {
  if (lang === "ru" || !summary) return summary;
  return summary
    .split(", ")
    .map((part) => recipeTitleMap[part] || part)
    .join(", ");
}

export default function App() {
  const [lang, setLang] = useState(localStorage.getItem("bb_lang") || "en");
  const t = translations[lang];

  const [token, setToken] = useState(localStorage.getItem("bb_token") || "");
  const [currentUser, setCurrentUser] = useState(null);
  const [authMode, setAuthMode] = useState("login");
  const [authEmail, setAuthEmail] = useState("");
  const [authPassword, setAuthPassword] = useState("");

  const [meta, setMeta] = useState(null);
  const [budgetRub, setBudgetRub] = useState(1800);
  const [days, setDays] = useState(4);
  const [mealMode, setMealMode] = useState("2");
  const [excludedTags, setExcludedTags] = useState([]);
  const [pantrySelections, setPantrySelections] = useState([{ name: "", quantity: "", unit: "g" }]);
  const [priceOverrides, setPriceOverrides] = useState({});
  const [userNote, setUserNote] = useState("");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [activeTab, setActiveTab] = useState("main");

  const [loading, setLoading] = useState(false);
  const [secondaryLoading, setSecondaryLoading] = useState(false);
  const [bootLoading, setBootLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    localStorage.setItem("bb_lang", lang);
  }, [lang]);

  const toggleLang = () => {
    setLang((prev) => (prev === "en" ? "ru" : "en"));
  };

  useEffect(() => {
    localStorage.setItem("bb_token", token || "");
  }, [token]);

  const filtersMap = {
    contains_pork: t.filtersNoPork,
    contains_beef: t.filtersNoBeef,
    vegetarian_only: t.filtersVegetarian,
    vegan_only: t.filtersVegan,
  };

  const authedFetch = async (path, options = {}) => {
    const headers = {
      ...(options.headers || {}),
    };

    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    return fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
    });
  };

  const loadMeta = async () => {
    const response = await fetch(`${API_BASE}/api/meta`);
    const data = await parseResponse(response);
    if (!response.ok) throw new Error(data.detail || "Meta load failed.");
    setMeta(data);

    const defaults = {};
    for (const item of data.price_catalog) {
      defaults[item.name] = item.default_price;
    }
    setPriceOverrides(defaults);
  };

  const loadHistory = async () => {
    const response = await authedFetch(`/api/meal-plans/history`);
    const data = await parseResponse(response);
    if (!response.ok) throw new Error(data.detail || "History load failed.");
    setHistory(data);
  };

  const loadFavorites = async () => {
    const response = await authedFetch(`/api/meal-plans/favorites`);
    const data = await parseResponse(response);
    if (!response.ok) throw new Error(data.detail || "Favorites load failed.");
    setFavorites(data);
  };

  const loadMe = async () => {
    const response = await authedFetch(`/api/auth/me`);
    const data = await parseResponse(response);
    if (!response.ok) throw new Error(data.detail || "Auth session failed.");
    setCurrentUser(data);
  };

  useEffect(() => {
    const boot = async () => {
      setBootLoading(true);
      setError("");
      try {
        await loadMeta();
        if (token) {
          await loadMe();
          await Promise.all([loadHistory(), loadFavorites()]);
        }
      } catch (err) {
        if (token) {
          setToken("");
          setCurrentUser(null);
        }
      } finally {
        setBootLoading(false);
      }
    };

    boot();
  }, []);

  const refreshPrivateData = async () => {
    await Promise.all([loadHistory(), loadFavorites()]);
  };

  const handleAuth = async (event) => {
    event.preventDefault();
    setSecondaryLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE}/api/auth/${authMode}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: authEmail,
          password: authPassword,
        }),
      });

      const data = await parseResponse(response);
      if (!response.ok) throw new Error(getErrorMessage(data, t.invalid));

      setToken(data.access_token);
      setCurrentUser(data.user);
      setAuthPassword("");
      await Promise.all([loadHistoryWithToken(data.access_token), loadFavoritesWithToken(data.access_token), loadMeta()]);
      setActiveTab("main");
    } catch (err) {
      setError(err.message || t.invalid);
    } finally {
      setSecondaryLoading(false);
    }
  };

  const loadHistoryWithToken = async (customToken) => {
    const response = await fetch(`${API_BASE}/api/meal-plans/history`, {
      headers: { Authorization: `Bearer ${customToken}` },
    });
    const data = await parseResponse(response);
    if (!response.ok) throw new Error(data.detail || "History load failed.");
    setHistory(data);
  };

  const loadFavoritesWithToken = async (customToken) => {
    const response = await fetch(`${API_BASE}/api/meal-plans/favorites`, {
      headers: { Authorization: `Bearer ${customToken}` },
    });
    const data = await parseResponse(response);
    if (!response.ok) throw new Error(data.detail || "Favorites load failed.");
    setFavorites(data);
  };

  const logout = () => {
    setToken("");
    setCurrentUser(null);
    setHistory([]);
    setFavorites([]);
    setResult(null);
    setActiveTab("main");
  };

  const toggleFilter = (filterValue) => {
    setExcludedTags((current) => {
      let next = current.includes(filterValue)
        ? current.filter((item) => item !== filterValue)
        : [...current, filterValue];

      if (filterValue === "vegan_only" && !current.includes(filterValue)) {
        next = next.filter((item) => item !== "vegetarian_only");
      }
      if (filterValue === "vegetarian_only" && !current.includes(filterValue)) {
        next = next.filter((item) => item !== "vegan_only");
      }

      return next;
    });
  };

  const getDefaultUnitForName = (name) => {
    const found = meta?.pantry_options?.find((item) => item.name === name);
    return found?.default_unit || "g";
  };

  const updatePantryName = (index, value) => {
    setPantrySelections((current) =>
      current.map((item, i) =>
        i === index
          ? { ...item, name: value, unit: value ? getDefaultUnitForName(value) : item.unit }
          : item
      )
    );
  };

  const updatePantryField = (index, field, value) => {
    setPantrySelections((current) =>
      current.map((item, i) => (i === index ? { ...item, [field]: value } : item))
    );
  };

  const addPantryRow = () => {
    setPantrySelections((current) => [...current, { name: "", quantity: "", unit: "g" }]);
  };

  const removePantryRow = (index) => {
    setPantrySelections((current) => {
      const next = current.filter((_, i) => i !== index);
      return next.length ? next : [{ name: "", quantity: "", unit: "g" }];
    });
  };

  const updatePrice = (name, value) => {
    setPriceOverrides((current) => ({
      ...current,
      [name]: value === "" ? "" : Number(value),
    }));
  };

  const generatePlan = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");

    const pantryItems = pantrySelections
      .filter((item) => item.name && Number(item.quantity) > 0)
      .map((item) => ({
        name: item.name,
        quantity: Number(item.quantity),
        unit: item.unit,
      }));

    try {
      const response = await authedFetch(`/api/meal-plans/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          budget_rub: Number(budgetRub),
          days: Number(days),
          meal_mode: mealMode,
          excluded_tags: excludedTags,
          pantry_items: pantryItems,
          price_overrides: priceOverrides,
          user_note: userNote,
        }),
      });

      const data = await parseResponse(response);
      if (!response.ok) throw new Error(getErrorMessage(data, t.invalid));
      setResult(data);
      setActiveTab("main");
      await refreshPrivateData();
    } catch (err) {
      setError(err.message || t.invalid);
    } finally {
      setLoading(false);
    }
  };

  const loadPlan = async (mealPlanId, targetTab = "main") => {
    setSecondaryLoading(true);
    setError("");
    try {
      const response = await authedFetch(`/api/meal-plans/${mealPlanId}`);
      const data = await parseResponse(response);
      if (!response.ok) throw new Error(getErrorMessage(data, t.invalid));
      setResult(data);
      setActiveTab(targetTab);
    } catch (err) {
      setError(err.message || t.invalid);
    } finally {
      setSecondaryLoading(false);
    }
  };

  const toggleFavorite = async () => {
    if (!result) return;
    setSecondaryLoading(true);
    setError("");
    try {
      const response = await authedFetch(`/api/meal-plans/${result.meal_plan_id}/favorite`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_favorite: !result.is_favorite }),
      });
      const data = await parseResponse(response);
      if (!response.ok) throw new Error(getErrorMessage(data, t.invalid));
      setResult((current) => ({ ...current, is_favorite: data.is_favorite }));
      await refreshPrivateData();
    } catch (err) {
      setError(err.message || t.invalid);
    } finally {
      setSecondaryLoading(false);
    }
  };

  const regeneratePlan = async () => {
    if (!result) return;
    setSecondaryLoading(true);
    setError("");
    try {
      const response = await authedFetch(`/api/meal-plans/${result.meal_plan_id}/regenerate`, {
        method: "POST",
      });
      const data = await parseResponse(response);
      if (!response.ok) throw new Error(getErrorMessage(data, t.invalid));
      setResult(data);
      await refreshPrivateData();
    } catch (err) {
      setError(err.message || t.invalid);
    } finally {
      setSecondaryLoading(false);
    }
  };

  const replaceBatch = async (batchNumber) => {
    if (!result) return;
    setSecondaryLoading(true);
    setError("");
    try {
      const response = await authedFetch(`/api/meal-plans/${result.meal_plan_id}/replace-batch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ batch_number: batchNumber }),
      });
      const data = await parseResponse(response);
      if (!response.ok) throw new Error(getErrorMessage(data, t.invalid));
      setResult(data);
      await refreshPrivateData();
    } catch (err) {
      setError(err.message || t.invalid);
    } finally {
      setSecondaryLoading(false);
    }
  };

  const renderPlanDetails = () => {
    if (!result) {
      return <div className="empty-state">{t.noData}</div>;
    }

    return (
      <>
        <div className="card">
          <div className="row">
            <div>
              <h2>
                {t.plan} #{result.meal_plan_id}
              </h2>
              <p className="muted">
                {result.total_cost_rub} ₽ • {result.days} • {lang === "ru"
                  ? result.meal_mode_label
                  : result.meal_mode_label
                      .replace("салат", "salad")
                      .replace(" + ", " + ")}
              </p>
            </div>
            <div className="actions">
              <button type="button" onClick={toggleFavorite} disabled={secondaryLoading}>
                {result.is_favorite ? t.favoriteRemove : t.favoriteAdd}
              </button>
              <button type="button" onClick={regeneratePlan} disabled={secondaryLoading}>
                {t.regenerate}
              </button>
            </div>
          </div>
          <p><strong>{t.commentAgent}:</strong> {result.reasoning || "—"}</p>
          {result.user_note ? <p><strong>{t.commentUser}:</strong> {result.user_note}</p> : null}
        </div>

        <div className="card">
          <h2>{t.batchDishes}</h2>
          <div className="batch-list">
            {result.batches.map((batch) => {
              const recipe = translateRecipe(lang, batch.recipe);
              return (
                <div key={batch.batch_number} className="batch-item">
                  <div className="row">
                    <h3>Batch {batch.batch_number}</h3>
                    <button type="button" onClick={() => replaceBatch(batch.batch_number)} disabled={secondaryLoading}>
                      {t.replace}
                    </button>
                  </div>
                  <p><strong>{recipe.title}</strong></p>
                  <p>{recipe.description}</p>
                  <p>
                    {recipe.category === "salad" ? t.saladCategory : t.mainCategory}
                    {" • "}
                    {recipe.portions} {t.portions}
                    {" • "}
                    {recipe.estimated_cost_rub} ₽
                  </p>
                  <p>{recipe.cooking_time_min} {t.minutes} • {recipe.protein_type}</p>
                </div>
              );
            })}
          </div>
        </div>

        <div className="card">
          <h2>{t.schedule}</h2>
          <div className="schedule-list">
            {result.schedule.map((day) => (
              <div key={day.day_number} className="schedule-item">
                <h3>{t.day} {day.day_number}</h3>
                <ul>
                  {day.meals.map((meal, idx) => {
                    const translatedMeal = translateRecipe(lang, meal);
                    return (
                      <li key={`${day.day_number}-${meal.id}-${idx}`}>
                        {translatedMeal.title}{" "}
                        <span className="muted">
                          ({translatedMeal.category === "salad" ? t.saladCategory : t.mainCategory})
                        </span>
                      </li>
                    );
                  })}
                </ul>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h2>{t.missing}</h2>
          {result.missing_ingredients.length === 0 ? (
            <p>{t.noMissing}</p>
          ) : (
            <ul>
              {result.missing_ingredients.map((item, index) => {
                const translated = translateMissingIngredient(lang, item);
                return (
                  <li key={`${item.name}-${item.unit}-${index}`}>
                    {translated.name} — {translated.quantity} {item.unit}
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      </>
    );
  };

  const renderListCards = (items, title) => (
    <div className="card">
      <h2>{title}</h2>
      {items.length === 0 ? (
        <div className="empty-state">{t.noData}</div>
      ) : (
        <div className="history-list page-list">
          {items.map((item) => (
            <button
              key={item.meal_plan_id}
              className="history-item"
              onClick={() => loadPlan(item.meal_plan_id, "main")}
              disabled={secondaryLoading}
            >
              <div className="history-title">
                #{item.meal_plan_id} {item.is_favorite ? "★" : ""}
              </div>
              <div className="history-sub">
                {item.total_cost_rub} ₽ • {item.days} • {lang === "ru"
                  ? item.meal_mode_label
                  : item.meal_mode_label.replace("салат", "salad")}
              </div>
              <div className="history-sub">{translateSummary(lang, item.summary) || "—"}</div>
              <div className="history-sub">
                {t.createdAt}: {new Date(item.created_at).toLocaleString()}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );

  const renderAccount = () => (
    <div className="card">
      <h2>{t.accountTitle}</h2>
      <p><strong>{t.email}:</strong> {currentUser?.email}</p>
      <p className="muted">{t.accountText}</p>
      <div className="actions">
        <button type="button" onClick={() => setActiveTab("history")}>{t.goHistory}</button>
        <button type="button" onClick={() => setActiveTab("favorites")}>{t.goFavorites}</button>
        <button type="button" onClick={() => setActiveTab("main")}>{t.goMain}</button>
        <button type="button" onClick={logout}>{t.logout}</button>
      </div>
    </div>
  );

  if (bootLoading) {
    return <div className="page"><div className="card">{t.loading}</div></div>;
  }

  if (!token || !currentUser) {
    return (
      <div className="auth-page">
        <div className="auth-topbar">
          <div className="lang-switch">
            <span className={lang === "en" ? "lang-label active" : "lang-label"}>🇬🇧 EN</span>
            <label className="switch">
              <input type="checkbox" checked={lang === "ru"} onChange={toggleLang} />
              <span className="switch-slider"></span>
            </label>
            <span className={lang === "ru" ? "lang-label active" : "lang-label"}>🇷🇺 RU</span>
          </div>
        </div>
        <div className="auth-card">
          <div className="auth-brand">
            <h1>{t.appName}</h1>
            <p className="muted">{t.authSubtitle}</p>
          </div>

          {error ? <div className="card error compact-error">{error}</div> : null}

          <form onSubmit={handleAuth}>
            <label>
              {t.email}
              <input type="email" value={authEmail} onChange={(e) => setAuthEmail(e.target.value)} required />
            </label>

            <label>
              {t.password}
              <input type="password" value={authPassword} onChange={(e) => setAuthPassword(e.target.value)} required />
            </label>

            <button type="submit" disabled={secondaryLoading}>
              {secondaryLoading ? t.loading : authMode === "login" ? t.login : t.register}
            </button>
          </form>

          <button
            type="button"
            className="link-button"
            onClick={() => setAuthMode(authMode === "login" ? "register" : "login")}
          >
            {authMode === "login" ? t.authSwitchRegister : t.authSwitchLogin}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      {loading ? (
        <div className="loading-overlay">
          <div className="loading-card">
            <div className="spinner" />
            <h2>{t.generating}</h2>
            <p>{t.generatingSub}</p>
          </div>
        </div>
      ) : null}

      <div className="topbar">
        <div>
          <h1 className="topbar-title">{t.appName}</h1>
          <p className="topbar-subtitle">{t.officialHeader}</p>
        </div>

        <div className="topbar-actions">
          <div className="lang-switch">
            <span className={lang === "en" ? "lang-label active" : "lang-label"}>🇬🇧 EN</span>
            <label className="switch">
              <input type="checkbox" checked={lang === "ru"} onChange={toggleLang} />
              <span className="switch-slider"></span>
            </label>
            <span className={lang === "ru" ? "lang-label active" : "lang-label"}>🇷🇺 RU</span>
          </div>
          <button onClick={logout}>{t.logout}</button>
        </div>
      </div>

      <div className="layout app-layout">
        <aside className="nav-sidebar card">
          <div className="nav-user">
            <div className="nav-user-email">{currentUser.email}</div>
          </div>

          <nav className="nav-menu">
            <button className={activeTab === "main" ? "nav-item active" : "nav-item"} onClick={() => setActiveTab("main")}>
              {t.menuMain}
            </button>
            <button className={activeTab === "history" ? "nav-item active" : "nav-item"} onClick={() => setActiveTab("history")}>
              {t.menuHistory}
            </button>
            <button className={activeTab === "favorites" ? "nav-item active" : "nav-item"} onClick={() => setActiveTab("favorites")}>
              {t.menuFavorites}
            </button>
            <button className={activeTab === "account" ? "nav-item active" : "nav-item"} onClick={() => setActiveTab("account")}>
              {t.menuAccount}
            </button>
          </nav>
        </aside>

        <main className="main">
          {activeTab === "main" ? (
            <>
              <div className="card">
                <form onSubmit={generatePlan}>
                  <div className="grid">
                    <label>
                      {t.budget}
                      <input
                        type="number"
                        min="0"
                        step="1"
                        value={budgetRub}
                        onChange={(e) => setBudgetRub(e.target.value)}
                      />
                    </label>

                    <label>
                      {t.days}
                      <input
                        type="number"
                        min="1"
                        max="7"
                        value={days}
                        onChange={(e) => setDays(e.target.value)}
                      />
                    </label>

                    <label>
                      {t.mealMode}
                      <select value={mealMode} onChange={(e) => setMealMode(e.target.value)}>
                        {meta.meal_modes.map((mode) => (
                          <option key={mode.value} value={mode.value}>
                            {lang === "ru"
                              ? mode.label
                              : {
                                  "1": "1",
                                  "1 + салат": "1 + salad",
                                  "2": "2",
                                  "2 + салат": "2 + salad",
                                  "3": "3",
                                  "3 + салат": "3 + salad",
                                }[mode.label] || mode.label}
                          </option>
                        ))}
                      </select>
                    </label>
                  </div>

                  <div className="card inner-card">
                    <h3>{t.filters}</h3>
                    <div className="filters">
                      {meta.filters.map((option) => (
                        <label key={option.value} className="checkbox">
                          <input
                            type="checkbox"
                            checked={excludedTags.includes(option.value)}
                            onChange={() => toggleFilter(option.value)}
                          />
                          {filtersMap[option.value]}
                        </label>
                      ))}
                    </div>
                  </div>

                  <div className="card inner-card">
                    <h3>{t.pantry}</h3>
                    <div className="pantry-list">
                      {pantrySelections.map((item, index) => (
                        <div key={index} className="pantry-row">
                          <select value={item.name} onChange={(e) => updatePantryName(index, e.target.value)}>
                            <option value="">{t.product}</option>
                            {meta.pantry_options.map((option) => (
                              <option key={option.name} value={option.name}>
                                {translatePantryLabel(lang, option.name)}
                              </option>
                            ))}
                          </select>

                          <input
                            type="number"
                            min="0"
                            step="1"
                            placeholder={t.quantity}
                            value={item.quantity}
                            onChange={(e) => updatePantryField(index, "quantity", e.target.value)}
                          />

                          <select value={item.unit} onChange={(e) => updatePantryField(index, "unit", e.target.value)}>
                            <option value="g">g</option>
                            <option value="kg">kg</option>
                            <option value="ml">ml</option>
                            <option value="l">l</option>
                            <option value="pc">{lang === "ru" ? "шт" : "pc"}</option>
                          </select>

                          <button type="button" onClick={() => removePantryRow(index)}>
                            {t.remove}
                          </button>
                        </div>
                      ))}
                      <button type="button" onClick={addPantryRow}>
                        {t.addProduct}
                      </button>
                    </div>
                  </div>

                  <div className="card inner-card">
                    <h3>{t.note}</h3>
                    <textarea
                      rows="3"
                      value={userNote}
                      onChange={(e) => setUserNote(e.target.value)}
                      placeholder={t.notePlaceholder}
                    />
                  </div>

                  <div className="card inner-card">
                    <h3>{t.pricesTitle}</h3>
                    <p className="muted">
                      {t.pricesSubtitle}
                    </p>
                    <p className="muted">
                      {t.updatedAt}: {meta.price_updated_at}
                    </p>
                    <div className="price-grid">
                      {meta.price_catalog.map((item) => (
                        <label key={item.name}>
                          {translatePantryLabel(lang, item.name)} ({translateUnitLabel(lang, item.unit_label)})
                          <input
                            type="number"
                            min="0"
                            step="1"
                            value={priceOverrides[item.name] ?? item.default_price}
                            onChange={(e) => updatePrice(item.name, e.target.value)}
                          />
                        </label>
                      ))}
                    </div>
                  </div>

                  <button type="submit" disabled={loading}>
                    {t.generate}
                  </button>
                </form>
              </div>

              {error ? <div className="card error">{error}</div> : null}

              {renderPlanDetails()}
            </>
          ) : null}

          {activeTab === "history" ? renderListCards(history, t.historyTitle) : null}
          {activeTab === "favorites" ? renderListCards(favorites, t.favoritesTitle) : null}
          {activeTab === "account" ? renderAccount() : null}
        </main>
      </div>
    </div>
  );
}
