from sqlalchemy.orm import Session
import models, schemas
import ai_service
from sqlalchemy import func

def create_feedback(db: Session, feedback: schemas.FeedbackCreate):
    analysis = ai_service.analyze_feedback(feedback.original_text)

    feedback_status = 'review' if analysis.get("language") == "review" else 'published'

    db_feedback = models.Feedback(
        original_text=feedback.original_text,
        product=feedback.product,
        original_language=analysis.get("language"),
        translated_text=analysis.get("translated_text"),
        sentiment=analysis.get("sentiment"),
        status=feedback_status,
        # If status is 'review', also mark that it was reviewed
        was_reviewed=(feedback_status == 'review') # <-- ADD THIS
    )

    db.add(db_feedback)
    db.commit() 
    db.refresh(db_feedback)

    return db_feedback


def get_all_feedback(db: Session, product: str | None = None, sentiment: str | None = None, original_language: str | None = None, show_all: bool = False, skip: int = 0, limit: int = 10):
    known_codes = ['en', 'fr', 'es', 'de', 'ja', 'zh', 'ru', 'ar', 'pt', 'it']

    query = db.query(models.Feedback) 

    if not show_all:
        query = query.filter(models.Feedback.status == 'published')

    if product:
        query = query.filter(models.Feedback.product == product)
    if sentiment:
        query = query.filter(models.Feedback.sentiment == sentiment)

    if original_language:
        if original_language == "Others":
            query = query.filter(models.Feedback.original_language.notin_(known_codes + ['review']))
        else:
            query = query.filter(models.Feedback.original_language == original_language)

    # Get the total count of items that match the filters BEFORE applying pagination
    total_count = query.count()

    # Apply pagination and ordering
    items = query.order_by(models.Feedback.created_at.desc()).offset(skip).limit(limit).all()

    return {"total_count": total_count, "items": items}


def get_sentiment_stats(db: Session):
    # Query the count of each sentiment, grouped by sentiment
    stats_query = db.query(
        models.Feedback.sentiment, 
        func.count(models.Feedback.id)
    ).group_by(models.Feedback.sentiment).all()

    # Convert the query result into a dictionary
    stats = {sentiment: count for sentiment, count in stats_query}

    # Ensure all sentiment categories are present
    positive_count = stats.get('positive', 0)
    negative_count = stats.get('negative', 0)
    neutral_count = stats.get('neutral', 0)
    total_count = positive_count + negative_count + neutral_count

    # Prepare the final response object
    response = {
        "positive_count": positive_count,
        "negative_count": negative_count,
        "neutral_count": neutral_count,
        "total_count": total_count,
        "positive_percentage": (positive_count / total_count * 100) if total_count > 0 else 0,
        "negative_percentage": (negative_count / total_count * 100) if total_count > 0 else 0,
        "neutral_percentage": (neutral_count / total_count * 100) if total_count > 0 else 0,
    }
    return response


def delete_feedback(db: Session, feedback_id: int):
    # Find the feedback item by its ID
    db_feedback = db.query(models.Feedback).filter(models.Feedback.id == feedback_id).first()
    if db_feedback:
        # If it exists, delete it and commit the change
        db.delete(db_feedback)
        db.commit()
    return db_feedback


def update_feedback(db: Session, feedback_id: int, feedback_data: schemas.FeedbackUpdate):
    db_feedback = db.query(models.Feedback).filter(models.Feedback.id == feedback_id).first()
    if db_feedback:
        db_feedback.translated_text = feedback_data.translated_text
        db_feedback.sentiment = feedback_data.sentiment
        db_feedback.status = 'published'
        db_feedback.original_language = 'un'
        db.commit()
        db.refresh(db_feedback)
    return db_feedback