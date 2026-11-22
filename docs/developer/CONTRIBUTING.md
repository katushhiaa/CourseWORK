---
owner: "@katushhiaa"
status: published
review_date: 2027-02-20
tags: [ops, developer]
---

# Як долучитися до розробки (CONTRIBUTING)

## Локальне середовище

1. Клонуй репозиторій `katushhiaa/CourseWORK` та перейди в директорію проєкту.
2. Створи та активуй віртуальне середовище Python (`.venv`).
3. Встанови залежності та інструменти документації (`mkdocs-material`, `mkdocs-mermaid2-plugin`, `mkdocs-git-revision-date-localized-plugin`).
4. Налаштуй змінні оточення (зокрема підключення до `MongoDB`) і запусти локальний сервер або застосунок.

## Стандарти коду та правило супроводу

* Дотримуйся чистої структури модулів у `app/` та перевірок якості коду (`SonarQube` / лінтери).
* Діє правило **«зміна коду = зміна документації»**: разом зі зміною коду або архітектури оновлюй відповідні файли в `docs/`:
  * [System Design Document (SDD)](../architecture/sdd.md)
  * [Infrastructure Specification (ISD)](../architecture/isd.md)
  * [Регламент підтримки](../developer/maintenance.md)
