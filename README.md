# Coderr Backend

This repository contains the backend services for the Coderr application. It is built using modern technologies to provide a robust and scalable API for the frontend and other clients.

## Features

- RESTful API endpoints for user and project management
- Authentication and authorization using JWT
- Integration with a PostgreSQL database
- Comprehensive logging and error handling
- Docker support for easy deployment
- File upload support for user profiles and offers (media handling)
- Pagination, filtering, and searching for efficient data access

## Getting Started

### Prerequisites

- Python 3.11+
- Django 4.x
- Django REST Framework
- PostgreSQL database
- Docker (optional, for containerized deployment)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/coderr-backend.git
   cd coderr-backend
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv env
   source env/bin/activate  # Linux/macOS
   env\Scripts\activate     # Windows
   ```

3. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:

   Create a `.env` file in the root directory and add the following:

   ```env
   SECRET_KEY=your_django_secret_key
   DEBUG=True
   DATABASE_URL=postgresql://user:password@localhost:5432/coderr
   ```

5. Run database migrations:

   ```bash
   python manage.py migrate
   ```

6. Create a superuser (optional, for admin access):

   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server:

   ```bash
   python manage.py runserver
   ```

### Media and File Uploads

- Media files are served from `/media/` during development.
- Uploads for user profile pictures and offer images are saved in the `media/` directory.
- Ensure `MEDIA_ROOT` and `MEDIA_URL` are configured in `settings.py` as follows:

  ```python
  MEDIA_URL = '/media/'
  MEDIA_ROOT = BASE_DIR / 'media'
  ```

- In the main `urls.py`, add static serving for media files:

  ```python
  from django.conf import settings
  from django.conf.urls.static import static

  if settings.DEBUG:
      urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
  ```

### API Documentation

- API is RESTful and built using Django REST Framework.
- Supports JWT authentication.
- API documentation is accessible at `/api-docs/` when the server is running.

### Testing

- Run automated tests with:

  ```bash
  python manage.py test
  ```

### Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

### License

This project is licensed under the MIT License.
