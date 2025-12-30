def test_client_does_not_found_specific_ticket(
    test_client,
):
    request = test_client.get("/ticket/1")
    assert request.status_code == 404
    assert request.json() == {
        "detail": "Ticket not found"
    }


def test_client_create_ticket(
    test_client,
):
    request = test_client.post(
        "/ticket",
        json={
            "price": 100.0,
            "show": "The Rolling Stones Concert",
            "user": "John Doe",
        },
    )
    assert request.status_code == 200
    assert request.json() == {"ticket_id": 1}


def test_client_update_ticket_price(
    test_client, add_special_ticket
):
    request = test_client.put(
        "/ticket/1234/price/250.0"
    )
    assert request.status_code == 200
    assert request.json() == {"detail": "Ticket updated"}


def test_client_delete_ticket(
    test_client, add_special_ticket
):
    request = test_client.delete("/ticket/1234")
    assert request.status_code == 200
    assert request.json() == {
        "detail": "Ticket removed"
    }
    request = test_client.get("/ticket/1234")
    assert request.status_code == 404
    assert request.json() == {
        "detail": "Ticket not found"
    }

def test_client_create_event(test_client):
    request = test_client.post(
        "/event",
        params={
            "event_name": "The Rolling Stones Concert",
            "ticket_number": 10,
        },
    )
    assert request.status_code == 200
    assert request.json() == {"event_id": 1}

