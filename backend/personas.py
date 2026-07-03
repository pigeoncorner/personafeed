from typing import TypedDict


class PersonaProfile(TypedDict):
    id: str
    name: str
    context: str
    topics: list[str]
    seed_queries: list[str]
    preferred_channels: list[str]
    preferred_publications: list[str]


PERSONAS: dict[str, PersonaProfile] = {
    "scientist": {
        "id": "scientist",
        "name": "Учёный-физик",
        "context": (
            "Учёный-физик — человек, чья жизнь вращается вокруг понимания фундаментальных "
            "законов природы. Он следит за препринтами на arXiv, читает Nature и Science, "
            "смотрит лекции MIT и каналы, объясняющие математику за физическими явлениями. "
            "Его интересуют методология, peer review и воспроизводимость результатов."
        ),
        "topics": [
            "quantum mechanics",
            "condensed matter physics",
            "peer review",
            "arxiv preprints",
            "scientific methodology",
            "particle physics",
        ],
        "seed_queries": [
            "3blue1brown fourier transform",
            "MIT physics lecture quantum mechanics",
            "arxiv condensed matter 2024",
            "Veritasium physics experiment",
        ],
        "preferred_channels": [
            "3Blue1Brown",
            "Veritasium",
            "MIT OpenCourseWare",
            "Sabine Hossenfelder",
        ],
        "preferred_publications": ["Nature", "Science", "arXiv", "Physical Review Letters"],
    },
    "teacher": {
        "id": "teacher",
        "name": "Учитель",
        "context": (
            "Учитель — человек, постоянно ищущий новые педагогические приёмы и качественные "
            "образовательные ресурсы. Он следит за методиками обучения, читает про учебные "
            "программы, смотрит обучающие каналы и читает Edutopia. Его волнуют вовлечённость "
            "учеников, инклюзивность и практические результаты образования."
        ),
        "topics": [
            "pedagogy",
            "curriculum design",
            "student engagement",
            "educational technology",
            "classroom management",
            "inclusive education",
        ],
        "seed_queries": [
            "Khan Academy teaching methodology",
            "TED-Ed classroom ideas 2024",
            "Crash Course pedagogy",
            "project based learning strategies",
        ],
        "preferred_channels": [
            "Khan Academy",
            "TED-Ed",
            "Crash Course",
            "Edutopia",
        ],
        "preferred_publications": ["Edutopia", "Education Week", "The Guardian Education"],
    },
    "founder": {
        "id": "founder",
        "name": "Стартап-фаундер",
        "context": (
            "Стартап-фаундер постоянно ищет product-market fit, изучает метрики роста "
            "и следит за трендами в венчурном мире. Он смотрит интервью YC-партнёров, читает "
            "First Round Review, слушает Lenny's Podcast. Его волнуют фандрайзинг, найм "
            "первой команды и построение культуры."
        ),
        "topics": [
            "product-market fit",
            "fundraising",
            "startup metrics",
            "go-to-market strategy",
            "venture capital",
            "hiring",
        ],
        "seed_queries": [
            "Y Combinator startup advice 2024",
            "a16z podcast founder interview",
            "Lenny Rachitsky product growth",
            "first round capital startup lessons",
        ],
        "preferred_channels": [
            "Y Combinator",
            "a16z",
            "Lenny's Podcast",
            "Lex Fridman",
        ],
        "preferred_publications": [
            "TechCrunch",
            "First Round Review",
            "Stratechery",
            "The Information",
        ],
    },
    "doctor": {
        "id": "doctor",
        "name": "Врач",
        "context": (
            "Врач следит за клиническими исследованиями, читает NEJM и Lancet, смотрит "
            "разборы клинических случаев. Его интересуют доказательная медицина, протоколы "
            "лечения и медицинское право. Он критически относится к популярным медицинским "
            "публикациям и доверяет только рецензируемым источникам."
        ),
        "topics": [
            "clinical trials",
            "evidence-based medicine",
            "medical protocols",
            "pharmacology",
            "patient outcomes",
            "medical ethics",
        ],
        "seed_queries": [
            "NEJM case records clinical",
            "MedCram medical education 2024",
            "Lancet research findings",
            "evidence based medicine BMJ",
        ],
        "preferred_channels": [
            "MedCram",
            "NEJM",
            "Medscape",
            "Osmosis",
        ],
        "preferred_publications": ["NEJM", "Lancet", "BMJ", "JAMA"],
    },
}


def get_static_profile(persona_id: str) -> PersonaProfile | None:
    return PERSONAS.get(persona_id)


def list_personas() -> list[dict]:
    return [
        {"id": p["id"], "name": p["name"], "context": p["context"]}
        for p in PERSONAS.values()
    ]
