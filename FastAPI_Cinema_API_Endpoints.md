# 🎬 FastAPI Cinema API Endpoints

## **📌 Overview**
This API provides endpoints for accessing movies, sessions, users, orders, and ticket data.

---

## **🎥 Movies**
### **1. Get All Movies**
- **Endpoint:** `GET /api/movies/`
- **Description:** Returns a list of all available movies.
- **Response Example:**
```json
[
    {
        "id": 1,
        "title": "Inception",
        "original_name": "Inception",
        "description": "A mind-bending thriller",
        "age_limit": 16,
        "genres": ["Sci-Fi", "Thriller"],
        "poster_url": "/media/posters/inception.jpg"
    },
    {
        "id": 2,
        "title": "Interstellar",
        "original_name": "Interstellar",
        "description": "A journey beyond the stars",
        "age_limit": 12,
        "genres": ["Sci-Fi", "Drama"],
        "poster_url": "/media/posters/interstellar.jpg"
    }
]
```

---

## **🎟 Sessions**
### **2. Get All Sessions**
- **Endpoint:** `GET /api/sessions/`
- **Description:** Returns all available sessions sorted by date and time.
- **Response Example:**
```json
[
    {
        "id": 1,
        "movie": "Inception",
        "hall": "IMAX 1",
        "session_date": "2025-03-22",
        "start_time": "18:00",
        "end_time": "20:30",
        "ticket_price": 150
    },
    {
        "id": 2,
        "movie": "Interstellar",
        "hall": "IMAX 2",
        "session_date": "2025-03-23",
        "start_time": "20:00",
        "end_time": "22:40",
        "ticket_price": 180
    }
]
```

---

## **👤 Users**
### **3. Get All Users**
- **Endpoint:** `GET /api/users/`
- **Description:** Returns a list of all registered users.
- **Response Example:**
```json
[
    {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com"
    },
    {
        "id": 2,
        "username": "jane_smith",
        "email": "jane@example.com"
    }
]
```

### **4. Get User Details with Tickets**
- **Endpoint:** `GET /api/users/{user_id}/`
- **Description:** Returns user details, including their ticket history.
- **Response Example:**
```json
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "orders": [
        {
            "order_id": 5,
            "session": {
                "id": 1,
                "movie": "Inception",
                "session_date": "2025-03-22",
                "start_time": "18:00",
                "hall": "IMAX 1"
            },
            "tickets": [
                {"seat_number": 12, "status": "booked"},
                {"seat_number": 13, "status": "booked"}
            ],
            "total_price": 300,
            "status": "completed"
        }
    ]
}
```

---

## **📦 Orders**
### **5. Get Order Details**
- **Endpoint:** `GET /api/orders/{order_id}/`
- **Description:** Returns order details, including session and ticket information.
- **Response Example:**
```json
{
    "id": 5,
    "user_id": 1,
    "session": {
        "id": 1,
        "movie": "Inception",
        "session_date": "2025-03-22",
        "start_time": "18:00",
        "hall": "IMAX 1"
    },
    "tickets": [
        {"seat_number": 12, "status": "booked"},
        {"seat_number": 13, "status": "booked"}
    ],
    "total_price": 300,
    "status": "completed"
}
```

---

## **🔍 Filtering & Searching**
- **Filter movies by genre:** `GET /api/movies/?genre=Sci-Fi`
- **Filter sessions by date:** `GET /api/sessions/?date=2025-03-22`
- **Filter orders by user:** `GET /api/users/{user_id}/orders/`
- **Filter orders by session:** `GET /api/sessions/{session_id}/orders/`

---

## **📌 Notes**
- All date fields are in `YYYY-MM-DD` format.
- Time fields follow the `HH:MM` format.
- All amounts (prices) are in the local currency unit.
- Authentication might be required for user-specific data.

