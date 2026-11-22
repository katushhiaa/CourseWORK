# CourseWORK (Python + MongoDB)

Курсовий проєкт за 3-й курс університету. Вебзастосунок на Python із використанням бази даних MongoDB.

## Швидкий старт для розробників (Онбординг)

1. Клонуйте репозиторій:

   ```bash
   git clone [https://github.com/katushhiaa/CourseWORK.git](https://github.com/katushhiaa/CourseWORK.git)
   cd CourseWORK
   ```

2. Створіть та активуйте віртуальне середовище:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Для Linux/macOS
   .venv\Scripts\Activate     # Для Windows PowerShell
   ```

3. Встановіть залежності:

   ```bash
   pip install -r requirements.txt
   ```

4. Запустіть локальний сервер застосунку. Детальніше про роботу в команді — у [CONTRIBUTING](docs/developer/CONTRIBUTING.md) та [Базі знань](docs/index.md).

## Архітектурна документація

Детальний опис системи, інфраструктури та прийнятих рішень знаходяться у каталозі `docs/`:

- [System Design Document (SDD)](docs/architecture/sdd.md)
- [Infrastructure Specification Document (ISD)](docs/architecture/isd.md)
- [Architecture Decision Records (ADR)](docs/architecture/adr/0001-use-fastapi-or-flask-for-python.md) та [MongoDB ADR](docs/architecture/adr/0002-choose-mongodb-as-document-store.md)

## Матриця покриття аудиторій (Documentation Audience Coverage)

| Аудиторія | Ключові питання | Документ-відповідь | Статус |
| :--- | :--- | :--- | :--- |
| **Новачок** | Як запустити проєкт локально? Які системні вимоги? | `README.md` (Швидкий старт) | **Покрито** |
| **Розробник** | З якими компонентами взаємодіє мій модуль? Як влаштована архітектура? | [SDD](docs/architecture/sdd.md) (C4-діаграма та компоненти) | **Покрито** |
| **QA** | Де описані контракти поведінки для перевірок та API-ендпоінти? | [SDD](docs/architecture/sdd.md) (API-контракти) | **Покрито** |
| **DevOps** | Як розгорнути і відкотити реліз? Які стадії у CI/CD? | [ISD](docs/architecture/isd.md) (Топологія та конвеєри) | **Покрито** |
| **Бізнес** | Що система робить і для кого вона створена? | `README.md` (Призначення системи) | **Покрито** |

## Оновлення версії (Documentation Maintenance & Iteration)

У межах ітерації супроводу та керування життєвим циклом документації (Лабораторна робота №10) до системи було додано новий функціонал і синхронізовано архітектурні артефакти:

- **Новий функціонал:** Реалізовано новий модуль аналітики та відповідний API-ендпоінт (`POST /api/v1/analytics/generate`) для формування статистичних звітів.
- **Оновлення для користувачів та бізнесу:** Оновлено опис поведінки системи (усунено дрейф, стан **PASS**). Усі нові маршрути та контракти задокументовані в [SDD](docs/architecture/sdd.md).
- **Онбординг:** Нові розробники можуть користуватися стандартизованим шляхом запуску проєкту локально через [ISD](docs/architecture/isd.md) та швидкий старт вище.