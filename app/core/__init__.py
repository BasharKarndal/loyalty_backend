"""
Core cross-cutting infrastructure.

Contains configuration, async database, security (JWT),
exception handling, API response envelope, logging, and middleware.

Business rules do NOT belong here — put them in ``app.modules``.
"""
