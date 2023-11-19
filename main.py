import json

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
sns_client = boto3.client('sns', region_name='us-east-2')
# sns
topic_arn = 'arn:aws:sns:us-east-2:392034398817:pet-adoption-email'


def publish_sns_message(action, data):
    message = json.dumps({'action': action, 'data': data})
    sns_client.publish(
        TopicArn=topic_arn,
        Message=message,
        MessageAttributes={
            'Action': {
                'DataType': 'String',
                'StringValue': action
            }
        }
    )


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
    try:
        adoption_data = {
            'adoption_id': new_adoption.adoptionId,
            'status': new_adoption.status,
            'adopter_email': adopter_email,
            'shelter_email': shelter_email,
            'pet_name': pet_name
        }
        publish_sns_message('CREATE', adoption_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return new_adoption


@app.put("/adoptions/{adoptionId}", response_model=AdoptionRspModel)
async def update_adoption_status(adoption_id: str, updated_data: AdoptionUpdate, adopter_email: str = None, shelter_email: str = None, pet_name: str = None):
    """Shelter updates adoption status."""
    updated_adoption = adoptions_resource.update_adoption_status(adoption_id, updated_data)
    if not updated_adoption:
        raise HTTPException(status_code=404, detail="Adoption not found")

    try:
        adoption_data = {
            'adoption_id': adoption_id,
            'status': updated_data.status,
            'adopter_email': adopter_email,
            'shelter_email': shelter_email,
            'pet_name': pet_name
        }
        publish_sns_message('UPDATE', adoption_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return updated_adoption


@app.delete("/adoptions/{adoptionId}")
async def delete_adoption(adoption_id: str, adopter_email: str = None, shelter_email: str = None, pet_name: str = None):
    """Delete an adoption request."""
    success = adoptions_resource.delete_adoption(adoption_id)
    if not success:
        raise HTTPException(status_code=404, detail="Adoption not found")
    try:
        delete_data = {
            'adoption_id': adoption_id,
            'adopter_email': adopter_email,
            'shelter_email': shelter_email,
            'pet_name': pet_name,
            'status': "deleted"
        }
        publish_sns_message('DELETE', delete_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"status": "Adoption deleted successfully"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8011)
