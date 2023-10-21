from __future__ import annotations
from pydantic import BaseModel
from typing import List
from typing import Optional

from resources.rest_models import Link


class AdoptionModel(BaseModel):
    adoptionId: Optional[str]
    petId: str
    adopterId: str
    status: Optional[str] = "pending"
    createdAt: Optional[str]
    updatedAt: Optional[str]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "adoptionId": "aid_0001",
                    "petId": "pid_0001",
                    "adopterId": "uid_0001",
                    "status": "pending",
                    "createdAt": "2023-10-18",
                    "updatedAt": "",
                }
            ]
        }
    }


class AdoptionRspModel(AdoptionModel):
    links: List[Link] = None