from flask import Blueprint, request, abort, make_response
from ..db import db
from ..models.pet import Pet
from google import genai
from dotenv import load_dotenv


load_dotenv(override=True)
client = genai.Client()

bp = Blueprint("pets", __name__, url_prefix="/pets")

@bp.post("")
def create_pet():
    request_body = request.get_json()
    new_pet = Pet(
        animal_type=request_body.get("animal_type"),
        color=request_body.get("color"),
        personality=request_body.get("personality"),
        name=generate_pet_name(
            request_body.get("animal_type"),
            request_body.get("color"),
            request_body.get("personality")
        )
    )

    db.session.add(new_pet)
    db.session.commit()

    return new_pet.to_dict(), 201

    

@bp.get("")
def get_pets():
    pet_query = db.select(Pet)

    pets = db.session.scalars(pet_query)
    response = []

    for pet in pets:
        response.append(pet.to_dict())

    return response

@bp.get("/<pet_id>")
def get_single_pet(pet_id):
    pet = validate_model(Pet,pet_id)
    return pet.to_dict()

def validate_model(cls,id):
    try:
        id = int(id)
    except:
        response =  response = {"message": f"{cls.__name__} {id} invalid"}
        abort(make_response(response , 400))

    query = db.select(cls).where(cls.id == id)
    model = db.session.scalar(query)
    if model:
        return model

    response = {"message": f"{cls.__name__} {id} not found"}
    abort(make_response(response, 404))


def generate_pet_name(animal_type,color,personality):
    prompt = (
    f"Generate exactly ONE funny, unique, and creative pet name "
    f"for a {color} {animal_type} with a {personality} personality. "
    f"Return ONLY the name. Do not provide alternatives, "
    f"explanations, or additional text."
)
    
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,

    )
    print(response.text)
    return response.text.strip()