from fastapi import FastAPI, Response, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List

import uvicorn
from resources.adoptions.adoptions_resource import AdoptionsResource
from resources.adoptions.adoptions_data_service import AdoptionsDataService
from resources.adoptions.adoption_models import AdoptionCreate, AdoptionUpdate, AdoptionRspModel

import boto3
from botocore.exceptions import NoCredentialsError

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# ses
ses_client = boto3.client('ses', region_name='us-east-2')


# This function returns a DataService instance.
def get_adoption_data_service():
    config = {
        "data_directory": "./data/",
        "adoption_data_file": "adoptions.json"
    }
    ds = AdoptionsDataService(config)
    return ds


# This function returns a Resource instance, which will be used to handle API calls.
def get_adoption_resource():
    ds = get_adoption_data_service()
    config = {"data_service": ds}
    res = AdoptionsResource(config)
    return res


adoptions_resource = get_adoption_resource()


@app.get("/")
async def root():
    return RedirectResponse("/static/index.html")


@app.get("/adoptions", response_model=List[AdoptionRspModel])
async def get_adoptions():
    """Return a list of all adoption requests."""
    result = adoptions_resource.get_adoptions()
    return result


@app.get("/adoptions/{adoptionId}", response_model=AdoptionRspModel)
async def get_adoption_by_id(adoptionId: str):
    """Retrieve adoption details by ID."""
    adoption = adoptions_resource.get_adoption_by_id(adoptionId)
    if not adoption:
        raise HTTPException(status_code=404, detail="Adoption not found")
    return adoption


@app.post("/adoptions", response_model=AdoptionRspModel)
async def create_adoption(adoption: AdoptionCreate, adopter_email: str = None, shelter_email: str = None, pet_name: str = None):
    """Create a new adoption request."""
    new_adoption = adoptions_resource.create_adoption(adoption.model_dump())
    if adopter_email and shelter_email:
        send_email(
            [adopter_email, shelter_email],
            "Adoption Request Notice",
            f"<h1>Adoption Request</h1><p>{adopter_email} has requested to adopt {pet_name} from {shelter_email}</p>"
                   )

    return new_adoption


@app.put("/adoptions/{adoptionId}", response_model=AdoptionRspModel)
async def update_adoption_status(adoptionId: str, updated_data: AdoptionUpdate, adopter_email: str = None, shelter_email: str = None, pet_name: str = None):
    """Shelter updates adoption status."""
    updated_adoption = adoptions_resource.update_adoption_status(adoptionId, updated_data)
    if not updated_adoption:
        raise HTTPException(status_code=404, detail="Adoption not found")
    if adopter_email and shelter_email:
        send_email(
            [adopter_email, shelter_email],
            "Adoption Status Change Notice",
            f"<h1>Adoption Status Changed</h1><p>{adopter_email}'s adoption request to {pet_name} from {shelter_email} has been updated to {updated_data.status}</p>"
        )
    return updated_adoption


@app.delete("/adoptions/{adoptionId}")
async def delete_adoption(adoptionId: str, adopter_email: str = None, shelter_email: str = None, pet_name: str = None):
    """Delete an adoption request."""
    success = adoptions_resource.delete_adoption(adoptionId)
    if not success:
        raise HTTPException(status_code=404, detail="Adoption not found")
    if adopter_email and shelter_email:
        send_email(
            [adopter_email, shelter_email],
            "Adoption Deleted",
            f"<h1>Adoption Deleted</h1><p>{adopter_email}'s adoption request to {pet_name} from {shelter_email} has been deleted</p>"
        )
    return {"status": "Adoption deleted successfully"}


def send_email(to_addresses, subject, body):
    try:
        response = ses_client.send_email(
            Source='pet-adoption-6156@gmail.com',
            Destination={'ToAddresses': to_addresses},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Html': {'Data': body}}
            }
        )
        return response
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="Email credentials not available")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8011)
