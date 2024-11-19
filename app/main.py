from app import models
from app.routes import admin_routes, auth_routes, party_routes, user_routes
from fastapi import FastAPI
from app.database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.route("/")
def welcome():
    return {"message": "Please visit localhost:8000/docs to view the Swagger docs."}

app.include_router(admin_routes.router, prefix="/admin", tags=["Admin"])
app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
app.include_router(user_routes.router, prefix="/user", tags=["Authentication"])
app.include_router(party_routes.router, prefix="/parties", tags=["Parties"])
