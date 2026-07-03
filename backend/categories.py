from typing import TypedDict


class Category(TypedDict):
    id: str
    emoji: str
    label: str
    hint: str
    base_topics: list[str]


CATEGORIES: dict[str, Category] = {
    "science": {
        "id": "science",
        "emoji": "🔬",
        "label": "Наука и математика",
        "hint": "Физика, биология, химия, астрономия, математика",
        "base_topics": ["science research", "physics discovery"],
    },
    "history": {
        "id": "history",
        "emoji": "🏛️",
        "label": "История",
        "hint": "Археология, древние цивилизации, военная история",
        "base_topics": ["history", "archaeology"],
    },
    "art": {
        "id": "art",
        "emoji": "🎨",
        "label": "Искусство и дизайн",
        "hint": "Живопись, иллюстрация, фотография, мода",
        "base_topics": ["art", "design"],
    },
    "tech": {
        "id": "tech",
        "emoji": "⚙️",
        "label": "Технологии и железо",
        "hint": "Инженерия, механика, компьютеры",
        "base_topics": ["engineering", "technology"],
    },
    "software": {
        "id": "software",
        "emoji": "💻",
        "label": "Интернет и софт",
        "hint": "Программирование, веб-разработка, дизайн ПО",
        "base_topics": ["software development", "programming"],
    },
    "nature": {
        "id": "nature",
        "emoji": "🌿",
        "label": "Природа и животные",
        "hint": "Экология, дикая природа, фермерство",
        "base_topics": ["wildlife", "ecology"],
    },
    "philosophy": {
        "id": "philosophy",
        "emoji": "🧠",
        "label": "Философия и жизнь",
        "hint": "Философия, убеждения, саморазвитие",
        "base_topics": ["philosophy", "self improvement"],
    },
    "food": {
        "id": "food",
        "emoji": "🍜",
        "label": "Еда и кулинария",
        "hint": "Кухни мира, выпечка, нутрициология",
        "base_topics": ["cooking", "food culture"],
    },
    "games": {
        "id": "games",
        "emoji": "🎮",
        "label": "Игры",
        "hint": "Видеоигры, консоли, настольные игры",
        "base_topics": ["video games", "board games"],
    },
    "music": {
        "id": "music",
        "emoji": "🎵",
        "label": "Музыка и звук",
        "hint": "Музыканты, история музыки, звук",
        "base_topics": ["music", "music history"],
    },
    "health": {
        "id": "health",
        "emoji": "🩺",
        "label": "Здоровье",
        "hint": "Фитнес, психология, медицина",
        "base_topics": ["health", "psychology"],
    },
    "business": {
        "id": "business",
        "emoji": "💼",
        "label": "Бизнес и экономика",
        "hint": "Предпринимательство, деньги, рынки",
        "base_topics": ["business", "economics"],
    },
    "culture": {
        "id": "culture",
        "emoji": "🌍",
        "label": "Культура и общество",
        "hint": "Социология, путешествия, политика, семья",
        "base_topics": ["society", "travel"],
    },
    "education": {
        "id": "education",
        "emoji": "📚",
        "label": "Образование",
        "hint": "Преподавание, обмен знаниями, школы",
        "base_topics": ["education", "learning"],
    },
    "literature": {
        "id": "literature",
        "emoji": "📖",
        "label": "Литература",
        "hint": "Книги, писательство, издательское дело",
        "base_topics": ["books", "literature"],
    },
    "movies": {
        "id": "movies",
        "emoji": "🎬",
        "label": "Кино и сериалы",
        "hint": "Фильмы, сериалы, стриминг",
        "base_topics": ["movies", "tv series"],
    },
    "sports": {
        "id": "sports",
        "emoji": "⚽",
        "label": "Спорт",
        "hint": "Футбол, бодибилдинг и любые виды спорта",
        "base_topics": ["sports"],
    },
    "home": {
        "id": "home",
        "emoji": "🏡",
        "label": "Дом и сад",
        "hint": "Интерьеры, садоводство, домашняя ферма",
        "base_topics": ["home improvement", "gardening"],
    },
    "fun": {
        "id": "fun",
        "emoji": "🤪",
        "label": "Развлечения",
        "hint": "Странное, смешное, сатирическое",
        "base_topics": ["weird funny", "satire"],
    },
}


def get_category(category_id: str) -> Category | None:
    return CATEGORIES.get(category_id)


def list_categories() -> list[Category]:
    return list(CATEGORIES.values())
