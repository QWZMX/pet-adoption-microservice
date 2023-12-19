import graphene
from typing import List, Optional
from .adoption_models import AdoptionRspModel


class LinkType(graphene.ObjectType):
    href = graphene.String()
    rel = graphene.String()
    type = graphene.String()


class AdoptionType(graphene.ObjectType):
    adoption_id = graphene.String()
    pet_id = graphene.String()
    adopter_id = graphene.String()
    status = graphene.String()
    created_at = graphene.String()
    updated_at = graphene.String()
    links = graphene.List(LinkType)

    @staticmethod
    def resolve_from_model(model: AdoptionRspModel):
        return AdoptionType(
            adoption_id=model.adoptionId,
            pet_id=model.petId,
            adopter_id=model.adopterId,
            status=model.status,
            created_at=model.createdAt,
            updated_at=model.updatedAt,
            links=[LinkType(href=link.href, rel=link.rel) for link in model.links]
        )

'''
example query:

[get all]
query {
  adoptions {
    adoptionId
    petId
    adopterId
    status
    createdAt
    updatedAt
    links {
      href
      rel
    }
  }
}

[get by id]
query {
  adoptions(adoptionId: "aid_1") {
    adoptionId
    petId
    adopterId
    status
    createdAt
    updatedAt
    links {
      href
      rel
    }
  }
}

'''
