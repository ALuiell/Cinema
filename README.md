# Cinema Ticket Booking System

## 📌 About the Project
This project is a web-based cinema ticket booking system built with Django. The system allows users to browse movies, check available sessions, book tickets, and complete online payments via Stripe.

---

## 📂 Project Structure

- `cinema/` - Main project configuration.
- `cinema_app/` - Core application containing business logic.
  - `models.py` - Database models.
  - `views.py` - Controllers handling page rendering and user interactions.
  - `services.py` - Business logic for movies, sessions, orders, and payments.
  - `webhooks.py` - Handles Stripe webhook events.
- `templates/` - HTML templates for rendering pages.
- `static/` - Static files such as CSS, JS, and images.
- `media/` - User-uploaded content such as movie posters.

---

## 🛠️ Technology Stack

- **Django** - Core framework for backend development.
- **Django ORM** - Database handling.
- **PostgreSQL / MySQL / SQLite** - Database storage.
  - **Local development**: Uses SQLite by default.
  - **Docker environment**: Uses PostgreSQL.
  - **Production**: Uses MySQL.
- **Redis** - Used for background task management.
- **Django Background Tasks** - Used for handling asynchronous background tasks.
- **Celery (prepared settings)** - Configured but not actively used in deployment.
- **Django REST Framework** - Provides a RESTful API for the application.
- **Stripe API** - Payment processing.
- **Bootstrap 5** - Frontend framework for UI.

---

## 🚀 Features

### 🎬 **Movies**
- View a list of available movies.
- Filter movies by genre, age restriction, and search by title or description.
- Detailed movie descriptions with posters.

### 🎟 **Sessions**
- View available screening sessions.
- Filter sessions by date and movie.
- Check available seats in a session.

### 🛒 **Ticket Booking and Orders**
- Select seats and book tickets for a session.
- View booking history in the user profile.
- Check order status.

### 💳 **Payment Processing (Stripe Integration)**
- Secure online payments through Stripe.
- Automatic order status update after payment.
- Webhook handling for payment verification.

### 👤 **User Management**
- Register, login, and manage accounts.
- Password reset and profile settings.
- View past ticket purchases and orders.

### 🔧 **Admin Panel**
- Manage movies, sessions, and bookings.
- Monitor user orders and transactions.
### 📡 **REST API**
- JSON API for movies, sessions, and orders under `/api/`.
- Authentication handled by Djoser with JWT tokens.

### 🤖 **Telegram Integration**
- Users can link their Telegram account from the profile page.
- Visit `/telegram/link/` while logged in to receive a deep link to the bot.
- Confirm the link by `POST`ing `code` and `tg_id` to `/api/telegram/link/confirm/`.
- Set the bot name via the `TELEGRAM_BOT_NAME` environment variable.

---

## 🛠️ Installation and Setup

### 1️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Apply Migrations
```bash
python manage.py migrate
```

### 3️⃣ Create a Superuser
```bash
python manage.py createsuperuser
```

### 4️⃣ Run the Development Server
```bash
python manage.py runserver
```

### 5️⃣ Environment Variables
Create a `.env` file in the project root and define at least the following variables:

```
SECRET_KEY=your_secret_key
DEBUG=True
TELEGRAM_BOT_NAME=your_bot_name
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```
These variables are loaded by `decouple.config` in `cinema/settings.py`.

### 6️⃣ Access the Web Application
- Open `http://127.0.0.1:8000/` to browse movies and book tickets.
- Open `http://127.0.0.1:8000/admin/` to access the admin panel.

### 🚢 Run with Docker Compose
This project includes a `docker-compose.yml` for local development. Build and start all services with:
```bash
docker-compose up --build
```
The stack includes PostgreSQL, Redis, and Celery workers.

---

## 📌 Future Improvements
- [ ] Implement FastAPI-based API for improved performance.
- [ ] Improve search functionality for movies and sessions.
- [ ] Add email notifications for ticket purchases.
- [ ] Optimize UI for a better booking experience.
- [ ] Integrate a Telegram bot for session updates and account verification.

---

## 🤝 Contributing
Feel free to submit issues and pull requests. Contributions are welcome!

