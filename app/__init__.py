"""
Clinic Manager — Application package.

Architecture
------------
Clean Architecture + Modular (bounded contexts).

Layers (inside each module under ``app.modules.<name>``):

1. domain          — entities, repository interfaces, unit-of-work interfaces
2. application     — commands, queries, DTOs, handlers (use-cases)
3. infrastructure  — SQLAlchemy models, mappers, repository & UoW implementations
4. presentation    — FastAPI routers, response schemas

Cross-cutting concerns live in ``app.core`` (config, DB, security, responses).
Shared helpers live in ``app.shared``.
"""
