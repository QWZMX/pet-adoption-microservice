from resources.abstract_base_data_service import BaseDataService
import json

class AdoptionsDataService(BaseDataService):


    def __init__(self, config: dict):
        super().__init__()

        # Assuming you have a specific directory and file for adoptions
        self.data_dir = config["data_directory"]
        self.data_file = config["adoption_data_file"]
        self.adoptions = []

        self._load()

    def _get_data_file_name(self):
        return f"{self.data_dir}/{self.data_file}"

    def _load(self):
        fn = self._get_data_file_name()
        with open(fn, "r") as in_file:
            self.adoptions = json.load(in_file)

    def _save(self):
        fn = self._get_data_file_name()
        with open(fn, "w") as out_file:
            json.dump(self.adoptions, out_file)

    def get_adoptions(self, adoptionId: str = None, petId: str = None, adopterId: str = None) -> list:
        result = []

        for a in self.adoptions:
            if (adoptionId is None or (a.get("adoptionId", None) == adoptionId)) and \
               (petId is None or (a.get("petId", None) == petId)) and \
               (adopterId is None or (a.get("adopterId", None) == adopterId)):
                result.append(a)

        return result

    def create_adoption(self, data: dict) -> dict:
        new_adoption = {
            "adoptionId": f"aid_{len(self.adoptions) + 1}",  # Just a simple auto-increment for example
            "petId": data["petId"],
            "adopterId": data["adopterId"],
            "status": "pending",
            "createdAt": "2023-10-18",  # This should be dynamic, based on current date
            "updatedAt": "2023-10-18"   # This should be dynamic, based on current date
        }

        self.adoptions.append(new_adoption)
        self._save()

        return new_adoption

    def update_adoption_status(self, adoptionId: str, data: dict) -> dict:
        """
        Update an existing adoption based on the provided adoptionId and data.
        :param adoptionId: The ID of the adoption to update.
        :param data: A dictionary containing the fields to update.
        :return: The updated adoption record.
        """
        for adoption in self.adoptions:
            if adoption["adoptionId"] == adoptionId:
                # This should be dynamic, based on current date
                adoption["updatedAt"] = "2023-10-18"
                
                # Only allowing status update for now. You can expand this to update other fields as needed.
                if "status" in data:
                    adoption["status"] = data["status"]
                
                self._save()
                return adoption
        return None  # Returns None if no matching adoptionId was found

    def delete_adoption(self, adoptionId: str) -> bool:
        """
        Delete an adoption based on the provided adoptionId.
        :param adoptionId: The ID of the adoption to delete.
        :return: True if the deletion was successful, False otherwise.
        """
        for index, adoption in enumerate(self.adoptions):
            if adoption["adoptionId"] == adoptionId:
                del self.adoptions[index]
                self._save()
                return True
        return False

    def get_adoption_by_id(self, adoptionId: str) -> dict:
        """
        Retrieve a specific adoption based on the provided adoptionId.
        :param adoptionId: The ID of the adoption to retrieve.
        :return: The adoption record if found, None otherwise.
        """
        for adoption in self.adoptions:
            if adoption["adoptionId"] == adoptionId:
                return adoption
        return None  # Returns None if no matching adoptionId was found
