# app/shared/mapper.py

from typing import Type, TypeVar

from pydantic import BaseModel

ModelType = TypeVar("ModelType")
DtoType = TypeVar("DtoType", bound=BaseModel)


class BaseMapper:

    @staticmethod
    def to_dto(
        model: ModelType,
        dto: Type[DtoType],
    ) -> DtoType:
        return dto.model_validate(
            model,
            from_attributes=True,
        )

    @staticmethod
    def to_dto_list(
        models: list[ModelType],
        dto: Type[DtoType],
    ) -> list[DtoType]:

        return [
            dto.model_validate(
                model,
                from_attributes=True,
            )
            for model in models
        ]