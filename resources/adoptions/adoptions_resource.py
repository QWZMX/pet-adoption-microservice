from resources.abstract_base_resource import BaseResource
from resources.adoptions.adoption_models import AdoptionRspModel, AdoptionModel
from resources.rest_models import Link
from typing import List

class AdoptionsResource(BaseResource):
    #
    # Initial setup for the Adoption resource.
    #

    def __init__(self, config):
        super().__init__()
        self.data_service = config["data_service"]

    @staticmethod
    def _generate_links(a: dict) -> AdoptionRspModel:
        self_link = Link(**{
            "rel": "self",
            "href": "/adoptions/" + a['adoptionId']
        })
        pet_link = Link(**{
            "rel": "pet",
            "href": "/pets/" + a['petId']
        })
        adopter_link = Link(**{
            "rel": "adopter",
            "href": "/users/" + a['adopterId']
        })

        links = [
            self_link,
            pet_link,
            adopter_link
        ]
        rsp = AdoptionRspModel(**a, links=links)
        return rsp

    # GET /adoptions
    def get_adoptions(self, adoption_id: str = None, pet_id: str = None, adopter_id: str = None) -> List[AdoptionRspModel]:
        result = self.data_service.get_adoptions(adoption_id, pet_id, adopter_id)
        final_result = []

        for a in result:
            m = self._generate_links(a)
            final_result.append(m)

        return final_result

    # GET /adoptions/{adoptionId}
    def get_adoption_by_id(self, adoption_id: str) -> AdoptionRspModel:
        adoption = self.data_service.get_adoption_by_id(adoption_id)
        if not adoption:
            raise NotFoundError(f"Adoption with ID {adoption_id} not found")  # Assuming you've defined NotFoundError
        return self._generate_links(adoption)

    # POST /adoptions
    def create_adoption(self, data: dict) -> AdoptionRspModel:
        new_adoption = self.data_service.create_adoption(data)
        return self._generate_links(new_adoption)



    # PUT /adoptions/{adoptionId}
    def update_adoption_status(self, adoption_id: str, data: dict) -> AdoptionRspModel:
        updated_adoption = self.data_service.update_adoption_status(adoption_id, data)
        if not updated_adoption:
            raise NotFoundError(f"Adoption with ID {adoption_id} not found")
        return self._generate_links(updated_adoption)

    # DELETE /adoptions/{adoptionId}
    def delete_adoption(self, adoption_id: str):
        self.data_service.delete_adoption(adoption_id)
        return {}, 204  # Return a no-content response for successful delete
