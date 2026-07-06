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
        "label": "Наука и математика",
        "hint": "Физика, биология, химия, астрономия, математика",
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
        "label": "История",
        "hint": "Археология, древние цивилизации, военная история",
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
        "label": "Искусство и дизайн",
        "hint": "Живопись, иллюстрация, фотография, мода",
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
        "label": "Технологии и железо",
        "hint": "Инженерия, механика, компьютеры",
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
        "label": "Интернет и софт",
        "hint": "Программирование, веб-разработка, дизайн ПО",
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
        "label": "Природа и животные",
        "hint": "Экология, дикая природа, фермерство",
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
        "label": "Философия и жизнь",
        "hint": "Философия, убеждения, саморазвитие",
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
        "label": "Еда и кулинария",
        "hint": "Кухни мира, выпечка, нутрициология",
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
        "label": "Игры",
        "hint": "Видеоигры, консоли, настольные игры",
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
        "label": "Музыка и звук",
        "hint": "Музыканты, история музыки, звук",
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
        "label": "Здоровье",
        "hint": "Фитнес, психология, медицина",
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
        "label": "Бизнес и экономика",
        "hint": "Предпринимательство, деньги, рынки",
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
        "label": "Культура и общество",
        "hint": "Социология, путешествия, политика, семья",
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
        "label": "Образование",
        "hint": "Преподавание, обмен знаниями, школы",
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
        "label": "Литература",
        "hint": "Книги, писательство, издательское дело",
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
        "label": "Кино и сериалы",
        "hint": "Фильмы, сериалы, стриминг",
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
        "label": "Спорт",
        "hint": "Футбол, бодибилдинг и любые виды спорта",
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
        "label": "Дом и сад",
        "hint": "Интерьеры, садоводство, домашняя ферма",
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
        "label": "Развлечения",
        "hint": "Странное, смешное, сатирическое",
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
}


def get_category(category_id: str) -> Category | None:
    return CATEGORIES.get(category_id)


def list_categories() -> list[Category]:
    return list(CATEGORIES.values())
