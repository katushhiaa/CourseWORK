---
owner: "@katushhiaa"
status: published
review_date: 2027-02-20
tags: [ops]
---

# Регламент підтримки документації (Documentation Maintenance Regime)

## 1. Головне правило супроводу
>
> **«Зміна коду = зміна документації»**
Жодне злиття (Merge) оновлень чи нового функціоналу до магістральної гілки `main` не проходить без обов'язкового перегляду та оновлення відповідних артефактів у каталозі `docs/` та файлу `README.md`.

## 2. Таблиця власників та циклів перегляду

| Документ / Артефакт | Власник (Owner) | Цикл перегляду | Дата останнього перегляду |
| :--- | :--- | :--- | :--- |
| **`README.md`** | Lead Developer (@katushhiaa) | Кожні 30 днів | 2026-11-22 |
| **`docs/architecture/sdd.md`** | System Architect (@katushhiaa) | Кожні 90 днів | 2026-11-22 |
| **`docs/architecture/isd.md`** | DevOps Engineer (@katushhiaa) | Кожні 90 днів | 2026-11-22 |
| **`docs/architecture/adr/*`** | Tech Lead (@katushhiaa) | При прийнятті рішень / раз на 180 днів | 2026-11-22 |

Деталі розробки — у [CONTRIBUTING](CONTRIBUTING.md).
