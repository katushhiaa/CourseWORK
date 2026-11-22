---
owner: "@katushhiaa"
status: published
review_date: 2027-02-20
tags: [architecture, ops]
---

# Infrastructure Specification Document (ISD)

## 1. Топологія розгортання
Система підтримує два основні середовища виконання:
- **Локальне середовище (Local Development):** Запуск через Python Virtual Environment (`.venv`) або локальний Docker Compose.
- **Контейнерне / Хмарне середовище (Production/Test):** Ізольовані Docker-контейнери для застосунку та MongoDB, оркестровані через CI/CD конвеєри.

## 2. Конфігурація середовищ та змінні (Environment Variables)
Для конфігурації використовуються такі змінні оточення (без секретів у репозиторії):
- `PORT` — порт запуску вебсервера (за замовчуванням `8000`).
- `MONGODB_URI` — рядок підключення до MongoDB (наприклад, `mongodb://localhost:27017`).
- `ENVIRONMENT` — режим роботи (`development`, `testing`, `production`).

## 3. CI/CD-конвеєр (GitHub Actions)
Згідно з налаштуваннями у `.github/workflows/`:
- **Стадії:** Лінтинг (перевірка стилю коду), запуск модульних тестів (`pytest`), перевірка якості через SonarQube Quality Gates.
- **Тригери:** Події `push` та `pull_request` у гілку `main`.

## 4. Моніторинг, резервне копіювання та метрики надійності (RTO / RPO)
- **Моніторинг:** Логування подій у консоль та інтеграція з SonarQube Cloud для відстеження технічного боргу.
- **RTO (Recovery Time Objective):** Допустимий час відновлення сервісу після збою — **до 2 годин**.
- **RPO (Recovery Point Objective):** Допустима втрата даних — **до 24 годин** (за рахунок щоденного резервного копіювання колекцій MongoDB).

Див. також [SDD](sdd.md) та [Регламент підтримки](../developer/maintenance.md).