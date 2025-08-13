## RESTful E-commerce API
This project is a secure, scalable RESTful API for an e-commerce platform, built to showcase a production-grade backend. It's designed with a strong emphasis on security, code quality, and performance.

## Key Features
+ **RESTful Design:** Implements full CRUD operations for Products, Categories, Orders, and Customers, adhering to REST principles.

+ **Secure Authentication & Authorization:** Utilizes OAuth 2.0 with JWTs to secure endpoints. It implements role-based access control for admin and normal_user, with granular permissions defined by scopes (e.g., write:orders, read:products).

+ **Business Logic:** Enforces critical business rules, such as inventory validation during order creation and automatic inventory updates.

+ **Efficiency:** Includes pagination and filtering on key GET endpoints to handle large datasets effectively.

+ **Monitoring:** Exposes a Prometheus-compatible /metrics endpoint for real-time API monitoring.

+ **Documentation & Testing:** Provides OpenAPI (Swagger UI) for interactive documentation and includes a comprehensive test suite (unit & integration) covering critical paths.

## Getting Started
1. Clone the repository:

```bash
Bash

git clone https://github.com/[your_username]/[your_repository_name].git
cd [your_repository_name]
```
2. Setup environment:
```bash
Bash

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
3. Configuration: Create a .env file from .env.example to set up your database and secrets.

4. Run migrations and start the server:
```bash
Bash

# Example commands for your chosen framework
alembic upgrade head
uvicorn main:app --reload
```
The API is live at http://127.0.0.1:8000.

## Authentication
The API uses OAuth 2.0. To access protected endpoints, you must first obtain a JWT by authenticating with a valid client ID and secret.

+ Interactive Docs: The Swagger UI at http://127.0.0.1:8000/docs provides a UI for authentication and testing.

## Testing
To run the complete test suite:
```bash
Bash

pytest
```
