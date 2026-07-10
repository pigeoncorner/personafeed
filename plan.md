# План: ребрендинг frontend — StumbleFeed (EN)

## Задача

Переработать текущий frontend:
- лого из `favicon.zip` (в корне репо: favicon.svg, .ico, png-набор, site.webmanifest);
- название в шапке → **StumbleFeed**, tagline — **Escape your algorithm**;
- ниже — слоган **«Step outside your infobubble, every day. Watch what you choose,
  not what the algorithm chooses for you»**;
- весь интерфейс перевести с русского на английский;
- убрать из шапки чипы категорий («Все», 🏛️ История, … ⚙) → один элемент
  «Settings» с широкой стрелкой вниз; по клику вниз раскрывается панель
  с плитками категорий (20 шт.);
- над плитками текст: **«Choose from 20 topics and get a shuffled grid of videos
  from YouTube without any algorithm»**;
- добавить 20-ю категорию — **✈️ Travel & Places** (согласовать с пользователем);
- кнопку «Удиви меня» → **Get New Feed**, разместить вверху по центру;
  тоггл YouTube / VK·RuTube — вправо.

**Допущения (из-за опечаток в постановке):**
1. «every d» = «every day».
2. «without any aligning» = «without any algorithm» (сквозная идея продукта).
3. Tagline — в шапке рядом с лого; слоган — строкой под шапкой (виден и на
   онбординге, и над лентой).
4. Клик по плитке в раскрытой панели переключает выбор категории и перезагружает
   ленту (заменяет и онбординг, и фильтр-чипы). Отдельный экран онбординга
   больше не нужен: при первом входе панель раскрыта, при выбранных
   категориях — свёрнута.

## Шаги реализации

### 1. Фавиконки и лого
- Распаковать `favicon.zip` → `frontend/` (favicon.svg, favicon.ico,
  favicon-96x96.png, apple-touch-icon.png, web-app-manifest-*, site.webmanifest).
- `index.html <head>`: `<link rel="icon" ...>` (svg + ico + png),
  `apple-touch-icon`, `manifest`.
- В шапке заменить `▶` на `<img src="favicon.svg">` (высота ~28px).
- Проверить, что `main.py` (StaticFiles) раздаёт новые файлы; поправить пути
  в `site.webmanifest` при необходимости.

→ верификация: фавиконка в табе браузера, лого в шапке.

### 2. Шапка — `index.html`, `style.css`
- Слева: лого + «StumbleFeed» + tagline «Escape your algorithm»
  (мелким серым рядом/под названием).
- Центр: кнопка **Get New Feed** (бывшая «Удиви меня»).
- Справа: тоггл источника YouTube / VK·RuTube.
- Под шапкой строка-слоган: «Step outside your infobubble, every day.
  Watch what you choose, not what the algorithm chooses for you».
- `<html lang="en">`, `<title>StumbleFeed — Escape your algorithm</title>`.

### 3. Категории: сворачиваемая панель вместо чипов и онбординга — `index.html`, `app.js`, `style.css`
- Удалить `#chips-row` (чипы «Все»/категории/⚙) и секцию `#onboarding`.
- Новый элемент под шапкой: кнопка-строка «⚙ Settings ⌄» (широкая стрелка вниз
  во всю ширину / по центру). Клик — раскрытие/сворачивание панели.
- В панели: текст «Choose from 20 topics and get a shuffled grid of videos from
  YouTube without any algorithm» + сетка из 20 плиток (реюз стилей
  `.category-card`). Клик по плитке = toggle выбора → сохранение в
  localStorage → `loadGrid()`.
- Первый вход (нет выбранных категорий): панель раскрыта автоматически;
  лента грузится после выбора хотя бы одной категории.
- Минимум 1 категория: снятие последней — блокируется или показывает подсказку.

### 4. 20-я категория — `backend/categories.py`
- Добавить **✈️ Travel & Places**: 3 EN-запроса (walking tour hidden gems /
  travel documentary remote places / local street life city) + 3 RU-запроса
  (для VK·RuTube оставить русские: «путешествия по россии», «городские
  прогулки влог», «необычные места мира»).

### 5. Перевод интерфейса на английский
- `backend/categories.py`: `label` и `hint` всех 20 категорий → английский
  (labels отдаются в UI через `/categories` и `category_label` в карточках).
- `frontend/app.js`:
  - `formatViews` → «1.2M views / 12K views»;
  - `formatTimeAgo` → «3 days ago» (убрать русские плюральные формы);
  - тексты ошибок, `SOURCE_LABELS` — без изменений (имена собственные).
- `frontend/index.html`: панель фильтров (Filters, presets: 🌱 Rising,
  👑 Niche Leaders, 💬 Discussions, 🎯 Viral, ✖ Reset; селекты Period / Views /
  Comments / Duration / Channels / Sort и их options), title-подсказки.
- RU-запросы `queries_ru` не трогаем — это данные для VK·RuTube, не интерфейс.

### 6. Документация
- README: скриншот/название обновить (если упоминается PersonaFeed в UI-контексте).

## Unit-тесты

- [ ] `/categories` возвращает 20 категорий, у всех по 3 `queries` и 3 `queries_ru`
- [ ] новая категория `travel`: валидная структура (id/emoji/label/hint/queries)
- [ ] `/grid` с `categories: ["travel"]` не падает (мок пула)
- [ ] существующие тесты обновлены под 20 категорий (`test_feed.py::test_get_categories` — `len >= 15` уже проходит) и остаются зелёными
- [ ] labels категорий — английские (нет кириллицы в `label`/`hint`)

## Верификация (ручная)

1. Фавиконка и лого отображаются, таб — «StumbleFeed — Escape your algorithm».
2. Шапка: лого+название слева, Get New Feed по центру, тоггл справа, слоган под шапкой.
3. Стрелка раскрывает панель с 20 плитками и текстом; выбор плиток меняет ленту.
4. Первый вход — панель раскрыта; повторный — свёрнута, лента грузится сразу.
5. Ни одной русской строки в UI (кроме контента видео).
