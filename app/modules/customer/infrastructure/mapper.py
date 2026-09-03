from app.modules.customer.domain.entity import Customer
from app.modules.customer.infrastructure.model import CustomerModel


class CustomerMapper:

    @staticmethod
    def to_domain(model: CustomerModel) -> Customer:
        return Customer(
            id=model.id,
            owner_id=model.owner_id,
            name=model.name,
            phone=model.phone,
            notes=model.notes,
            points=model.points,
            visit_count=model.visit_count,
            total_spent=model.total_spent,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Customer) -> CustomerModel:
        return CustomerModel(
            id=entity.id,
            owner_id=entity.owner_id,
            name=entity.name,
            phone=entity.phone,
            notes=entity.notes,
            points=entity.points,
            visit_count=entity.visit_count,
            total_spent=entity.total_spent,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
