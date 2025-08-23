from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Import all the necessary components from our other files
import models, schemas, crud
from database import engine, get_db
from typing import List
# This line creates the database tables.
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add the CORS middleware
origins = ["http://localhost:3000"] 
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the endpoint to create new feedback
@app.post("/api/feedback", response_model=schemas.Feedback)
def submit_feedback(feedback: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    return crud.create_feedback(db=db, feedback=feedback)

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Hello from the FastAPI backend!"}


@app.get("/api/feedback", response_model=schemas.PaginatedFeedbackResponse)
def get_feedback(
    product: str | None = None, 
    sentiment: str | None = None, 
    original_language: str | None = None,
    show_all: bool = False,
    page: int = 1, # Default to page 1
    page_size: int = 5, # Default to 5 items per page
    db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size
    limit = page_size
    return crud.get_all_feedback(
        db=db, 
        product=product, 
        sentiment=sentiment, 
        original_language=original_language, 
        show_all=show_all, 
        skip=skip, 
        limit=limit
    )




# Define the endpoint to get feedback statistics
@app.get("/api/stats", response_model=schemas.StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    return crud.get_sentiment_stats(db=db)    


@app.delete("/api/feedback/{feedback_id}", status_code=204)
def remove_feedback(feedback_id: int, db: Session = Depends(get_db)):
    crud.delete_feedback(db=db, feedback_id=feedback_id)
    # No need to return anything for a delete operation
    return    


@app.put("/api/feedback/{feedback_id}", response_model=schemas.Feedback)
def approve_feedback(feedback_id: int, feedback_data: schemas.FeedbackUpdate, db: Session = Depends(get_db)):
    updated_feedback = crud.update_feedback(db=db, feedback_id=feedback_id, feedback_data=feedback_data)
    if updated_feedback is None:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return updated_feedback    