from fastapi.testclient import TestClient

def test_read_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from the FastAPI backend!"}

def test_create_feedback(client: TestClient):
    response = client.post(
        "/api/feedback",
        json={"product": "Test Car", "original_text": "This is a test feedback."},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["product"] == "Test Car"
    assert data["status"] == "published"

def test_get_feedback_paginated(client: TestClient):
    # First, create an item so the database isn't empty
    client.post("/api/feedback", json={"product": "Paginated Car", "original_text": "A test for pagination."})
    
    response = client.get("/api/feedback")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total_count"] > 0 # This will now pass

def test_feedback_filtering(client: TestClient):
    # Create a specific item to filter for
    client.post("/api/feedback", json={"product": "Filter Car", "original_text": "A test for filtering."})

    response = client.get("/api/feedback?product=Filter Car")
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 1 # This will now pass
    assert data["items"][0]["product"] == "Filter Car"

def test_admin_can_see_all_feedback(client: TestClient, mocker):
    # Create a 'published' item
    client.post("/api/feedback", json={"product": "Published Car", "original_text": "This is good"})
    
    # Temporarily change the mock to return a 'review' status
    mocker.patch(
        "crud.ai_service.analyze_feedback",
        return_value={"language": "review", "status": "review", "translated_text": "Mock gibberish", "sentiment": "unknown"}
    )
    # Create a 'review' item
    client.post("/api/feedback", json={"product": "Review Car", "original_text": "asdfg"})

    # Normal users should only see the 1 published item
    user_response = client.get("/api/feedback")
    assert user_response.json()["total_count"] == 1
    
    # Admin users should see all 2 items
    admin_response = client.get("/api/feedback?show_all=true")
    assert admin_response.json()["total_count"] == 2

def test_delete_feedback(client: TestClient):
    # Create an item to delete
    create_response = client.post("/api/feedback", json={"product": "To Be Deleted", "original_text": "delete me"})
    feedback_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/feedback/{feedback_id}")
    assert delete_response.status_code == 204

    # Verify it's gone
    get_response = client.get("/api/feedback?show_all=true")
    all_ids = [item['id'] for item in get_response.json()['items']]
    assert feedback_id not in all_ids

def test_update_nonexistent_feedback(client: TestClient):
    response = client.put(
        "/api/feedback/999999",
        json={"translated_text": "This won't work", "sentiment": "positive"}
    )
    assert response.status_code == 404



def test_approve_feedback_flow(client: TestClient, mocker):
    """Tests the full admin approval workflow."""
    # Force the mock to create a 'review' item
    mocker.patch(
        "crud.ai_service.analyze_feedback",
        return_value={"language": "review", "status": "review", "translated_text": "Needs review", "sentiment": "unknown"}
    )
    create_response = client.post("/api/feedback", json={"product": "Review Car", "original_text": "asdfg"})
    assert create_response.status_code == 200
    feedback_id = create_response.json()["id"]

    # Now, send the PUT request to approve it
    update_response = client.put(
        f"/api/feedback/{feedback_id}",
        json={"translated_text": "Manual Admin Translation", "sentiment": "positive"}
    )

    # Check that the update was successful
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["status"] == "published"
    assert data["translated_text"] == "Manual Admin Translation"
    assert data["original_language"] == "un" # Verify it was re-categorized

def test_delete_feedback_flow(client: TestClient):
    """Tests that deleting an item works and removes it from the list."""
    # Create two items
    client.post("/api/feedback", json={"product": "Car A", "original_text": "First item"})
    item_to_delete_res = client.post("/api/feedback", json={"product": "Car B", "original_text": "Second item"})
    item_id_to_delete = item_to_delete_res.json()["id"]

    # Verify we have 2 items
    get_res_before = client.get("/api/feedback")
    assert get_res_before.json()["total_count"] == 2

    # Delete one item
    delete_res = client.delete(f"/api/feedback/{item_id_to_delete}")
    assert delete_res.status_code == 204

    # Verify we now have only 1 item
    get_res_after = client.get("/api/feedback")
    assert get_res_after.json()["total_count"] == 1    


def test_multifilter(client: TestClient, mocker):
    """Tests filtering by both product and sentiment simultaneously."""
    # The default mock will create published/neutral items
    client.post("/api/feedback", json={"product": "Multi Car", "original_text": "neutral text"})
    
    # We need a 'positive' item for this product to test the filter
    # For this one test, we can mock the AI to return 'positive'
    mocker.patch(
        "crud.ai_service.analyze_feedback",
        return_value={"status": "published", "sentiment": "positive"}
    )
    client.post("/api/feedback", json={"product": "Multi Car", "original_text": "positive text"})

    # Filter for the positive comment for "Multi Car"
    response = client.get("/api/feedback?product=Multi Car&sentiment=positive")
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 1
    assert data["items"][0]["sentiment"] == "positive"    