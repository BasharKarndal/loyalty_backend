"""
Business modules (bounded contexts).

Current roadmap
---------------
1. Identity            — User, Role, Permission (+ auth / assignments)
2. Clinic Management   — Department, Room, Doctor
3. Patient Management  — Patient
4. Visit Management    — Visit, VisitType, Queue, Barcode
5. Medical Record      — MedicalRecord, VitalSigns
6. Prescription        — Prescription, PrescriptionItem
7. Laboratory          — LabTest, LabOrder
8. Radiology           — RadiologyType, RadiologyOrder, RadiologyReport
9. Attachments         — file attachments

Module skeleton (mandatory for every new module)
------------------------------------------------
modules/<module_name>/
  domain/
    entity.py
    repository.py      # ABC
    unit_of_work.py    # ABC (when needed)
  application/
    commands/
    queries/
    dto/
    handlers/
      command_handlers/
      query_handlers/
  infrastructure/
    model.py
    mapper.py
    repository.py
    unit_of_work.py
  presentation/
    router.py
    responses.py

Rules
-----
- Domain has zero imports from FastAPI / SQLAlchemy.
- Application depends only on domain interfaces.
- Infrastructure implements domain interfaces.
- Presentation talks to application handlers only.
- Register each module router in ``app.shared.routers``.
"""
