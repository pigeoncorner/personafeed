from typing import TypedDict


class Category(TypedDict):
    id: str
    emoji: str
    label: str
    hint: str
    base_topics: list[str]
    queries: list[str]
    queries_ru: list[str]


CATEGORIES: dict[str, Category] = {
    "science": {
        "id": "science",
        "emoji": "🔬",
        "label": "Science & Math",
        "hint": "Physics, biology, chemistry, astronomy, maths",
        "base_topics": ["science research", "physics discovery"],
        "queries": [
            "physics explained paradox",
            "biology research breakthrough",
            "math proof beautiful",
            "astronomy discovery explained",
        ],
        "queries_ru": [
            "научпоп физика объяснение",
            "математика красивое доказательство",
            "астрономия открытия космос",
        ],
    },
    "history": {
        "id": "history",
        "emoji": "🏛️",
        "label": "History",
        "hint": "Archaeology, ancient civilisations, military history",
        "base_topics": ["history", "archaeology"],
        "queries": [
            "ancient civilization mystery documentary",
            "archaeology dig discovery",
            "forgotten history explained",
            "medieval history untold",
        ],
        "queries_ru": [
            "история древних цивилизаций документальный",
            "археологические находки",
            "неизвестные страницы истории",
        ],
    },
    "art": {
        "id": "art",
        "emoji": "🎨",
        "label": "Art & Design",
        "hint": "Painting, illustration, photography, fashion",
        "base_topics": ["art", "design"],
        "queries": [
            "artist process timelapse painting",
            "art history hidden masterpiece",
            "illustration technique secrets",
            "graphic design breakdown",
        ],
        "queries_ru": [
            "история живописи разбор картины",
            "процесс художника таймлапс",
            "дизайн разбор",
        ],
    },
    "tech": {
        "id": "tech",
        "emoji": "⚙️",
        "label": "Technology & Hardware",
        "hint": "Engineering, mechanics, computers",
        "base_topics": ["engineering", "technology"],
        "queries": [
            "engineering how it works teardown",
            "mechanical engineering explained",
            "hardware deep dive",
            "how machines are made factory",
        ],
        "queries_ru": [
            "как это устроено инженерия",
            "как делают на заводе производство",
            "разбор техники железо",
        ],
    },
    "software": {
        "id": "software",
        "emoji": "💻",
        "label": "Internet & Software",
        "hint": "Programming, web development, software design",
        "base_topics": ["software development", "programming"],
        "queries": [
            "software architecture explained",
            "programming concept deep dive",
            "open source project story",
            "developer interview workflow",
        ],
        "queries_ru": [
            "программирование разбор архитектуры",
            "история создания программы",
            "веб-разработка практика",
        ],
    },
    "nature": {
        "id": "nature",
        "emoji": "🌿",
        "label": "Nature & Animals",
        "hint": "Ecology, wildlife, farming",
        "base_topics": ["wildlife", "ecology"],
        "queries": [
            "wildlife behavior surprising documentary",
            "ecology system explained",
            "rare animal encounter",
            "nature expedition remote",
        ],
        "queries_ru": [
            "дикая природа документальный",
            "удивительные животные",
            "экспедиция природа",
        ],
    },
    "philosophy": {
        "id": "philosophy",
        "emoji": "🧠",
        "label": "Philosophy & Life",
        "hint": "Philosophy, beliefs, self-improvement",
        "base_topics": ["philosophy", "self improvement"],
        "queries": [
            "philosophy thought experiment explained",
            "stoicism practice real life",
            "ethics dilemma debate",
            "ancient wisdom modern life",
        ],
        "queries_ru": [
            "философия просто о сложном",
            "стоицизм практика жизни",
            "мысленный эксперимент философия",
        ],
    },
    "food": {
        "id": "food",
        "emoji": "🍜",
        "label": "Food & Cooking",
        "hint": "World cuisines, baking, nutrition",
        "base_topics": ["cooking", "food culture"],
        "queries": [
            "cooking technique explained science",
            "world street food documentary",
            "fermentation food culture",
            "chef secret recipe breakdown",
        ],
        "queries_ru": [
            "кухни мира уличная еда",
            "наука кулинарии техника",
            "рецепт от шефа разбор",
        ],
    },
    "games": {
        "id": "games",
        "emoji": "🎮",
        "label": "Games",
        "hint": "Video games, consoles, board games",
        "base_topics": ["video games", "board games"],
        "queries": [
            "game design analysis deep dive",
            "video game history untold",
            "indie game dev story",
            "board game strategy explained",
        ],
        "queries_ru": [
            "разбор геймдизайна",
            "история видеоигр",
            "инди разработка игр",
        ],
    },
    "music": {
        "id": "music",
        "emoji": "🎵",
        "label": "Music & Sound",
        "hint": "Musicians, music history, audio",
        "base_topics": ["music", "music history"],
        "queries": [
            "music theory explained visually",
            "music history forgotten genre",
            "sound design behind the track",
            "instrument technique secrets",
        ],
        "queries_ru": [
            "теория музыки объяснение",
            "история музыкального жанра",
            "как устроен звук саунд-дизайн",
        ],
    },
    "health": {
        "id": "health",
        "emoji": "🩺",
        "label": "Health",
        "hint": "Fitness, psychology, medicine",
        "base_topics": ["health", "psychology"],
        "queries": [
            "sports science training explained",
            "psychology research surprising finding",
            "medical research breakthrough",
            "human body how it works",
        ],
        "queries_ru": [
            "научный подход тренировки",
            "психология исследования",
            "как работает организм человека",
        ],
    },
    "business": {
        "id": "business",
        "emoji": "💼",
        "label": "Business & Economics",
        "hint": "Entrepreneurship, money, markets",
        "base_topics": ["business", "economics"],
        "queries": [
            "startup failure story lessons",
            "economics explained history",
            "business model breakdown",
            "entrepreneur niche market",
        ],
        "queries_ru": [
            "история бизнеса разбор",
            "экономика простыми словами",
            "предприниматель история провала",
        ],
    },
    "culture": {
        "id": "culture",
        "emoji": "🌍",
        "label": "Culture & Society",
        "hint": "Sociology, traditions, politics, family",
        "base_topics": ["society", "travel"],
        "queries": [
            "culture documentary hidden tradition",
            "travel remote community",
            "sociology experiment explained",
            "social phenomenon analysis",
        ],
        "queries_ru": [
            "традиции народов мира документальный",
            "путешествие отдалённые места",
            "социология эксперименты",
        ],
    },
    "education": {
        "id": "education",
        "emoji": "📚",
        "label": "Education",
        "hint": "Teaching, knowledge sharing, schools",
        "base_topics": ["education", "learning"],
        "queries": [
            "learning science how memory works",
            "teaching method innovative",
            "education system reform documentary",
            "study technique evidence based",
        ],
        "queries_ru": [
            "как учиться эффективно наука",
            "методики преподавания",
            "как работает память обучение",
        ],
    },
    "literature": {
        "id": "literature",
        "emoji": "📖",
        "label": "Literature",
        "hint": "Books, writing, publishing",
        "base_topics": ["books", "literature"],
        "queries": [
            "book analysis deep dive",
            "writing craft storytelling technique",
            "literary history forgotten author",
            "author interview creative process",
        ],
        "queries_ru": [
            "разбор книги анализ",
            "писательское мастерство",
            "забытые писатели история литературы",
        ],
    },
    "movies": {
        "id": "movies",
        "emoji": "🎬",
        "label": "Film & Series",
        "hint": "Movies, TV shows, streaming",
        "base_topics": ["movies", "tv series"],
        "queries": [
            "film analysis cinematography explained",
            "cinema history pioneering technique",
            "movie making behind the scenes",
            "director interview filmmaking craft",
        ],
        "queries_ru": [
            "разбор фильма кинематография",
            "история кино",
            "как снимают кино закулисье",
        ],
    },
    "sports": {
        "id": "sports",
        "emoji": "⚽",
        "label": "Sports",
        "hint": "Football, bodybuilding, any sport",
        "base_topics": ["sports"],
        "queries": [
            "sports science athlete biomechanics",
            "sports history untold story",
            "training method elite athlete",
            "extreme sport documentary",
        ],
        "queries_ru": [
            "спортивная наука биомеханика",
            "история спорта великие моменты",
            "тренировки профессиональных атлетов",
        ],
    },
    "home": {
        "id": "home",
        "emoji": "🏡",
        "label": "Home & Garden",
        "hint": "Interiors, gardening, homesteading",
        "base_topics": ["home improvement", "gardening"],
        "queries": [
            "home renovation transformation",
            "interior design principles explained",
            "gardening technique organic",
            "DIY home project woodworking",
        ],
        "queries_ru": [
            "ремонт своими руками до и после",
            "дизайн интерьера разбор",
            "сад огород советы",
        ],
    },
    "fun": {
        "id": "fun",
        "emoji": "🤪",
        "label": "Entertainment",
        "hint": "Weird, funny, satirical",
        "base_topics": ["weird funny", "satire"],
        "queries": [
            "weird science experiment",
            "unexpected world record",
            "absurd history fact explained",
            "comedy sketch analysis",
        ],
        "queries_ru": [
            "странные эксперименты",
            "абсурдные факты истории",
            "смешные изобретения",
        ],
    },
    "travel": {
        "id": "travel",
        "emoji": "✈️",
        "label": "Travel & Places",
        "hint": "Walking tours, hidden gems, local life",
        "base_topics": ["travel", "walking tour"],
        "queries": [
            "walking tour hidden gems city",
            "travel documentary remote places",
            "local street life culture",
        ],
        "queries_ru": [
            "путешествия по России влог",
            "городские прогулки интересные места",
            "необычные места мира",
        ],
    },
}


def get_category(category_id: str) -> Category | None:
    return CATEGORIES.get(category_id)


def list_categories() -> list[Category]:
    return list(CATEGORIES.values())
