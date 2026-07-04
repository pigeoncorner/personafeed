from typing import TypedDict


class Category(TypedDict):
    id: str
    emoji: str
    label: str
    hint: str
    base_topics: list[str]
    queries: list[str]


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
    },
}


def get_category(category_id: str) -> Category | None:
    return CATEGORIES.get(category_id)


def list_categories() -> list[Category]:
    return list(CATEGORIES.values())
