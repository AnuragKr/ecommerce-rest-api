# 🛒 E-commerce REST API

A production-grade, scalable e-commerce REST API built with FastAPI, SQLAlchemy, and PostgreSQL. This API provides comprehensive functionality for product management, user authentication, order processing, and inventory management.

## 🚀 Features

### ✨ **Core Functionality**
- **User Management**: Registration, authentication, role-based access control
- **Product Catalog**: CRUD operations, stock management, search and filtering
- **Order Management**: Complete order lifecycle with stock validation
- **Inventory Control**: Real-time stock monitoring and alerts
- **Security**: JWT authentication, password hashing, access control

### 🛡️ **Advanced Features**
- **Stock Validation**: Prevents orders when stock is insufficient
- **Real-time Inventory**: Automatic stock updates and monitoring
- **Admin Dashboard**: Comprehensive inventory insights and analytics
- **API Documentation**: Interactive OpenAPI/Swagger documentation
- **Error Handling**: Comprehensive error handling with user-friendly messages

## 🏗️ Architecture

### **Layered Architecture**
```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                     │
├─────────────────────────────────────────────────────────────┤
│                  Service Layer (Business Logic)             │
├─────────────────────────────────────────────────────────────┤
│                Repository Layer (Data Access)               │
├─────────────────────────────────────────────────────────────┤
│                  Database Layer (PostgreSQL)                │
└─────────────────────────────────────────────────────────────┘
```

### **Technology Stack**
- **Backend Framework**: FastAPI (Python 3.8+)
- **Database**: PostgreSQL with async support
- **ORM**: SQLAlchemy + SQLModel
- **Authentication**: JWT tokens with Redis blacklisting
- **Documentation**: OpenAPI/Swagger + Scalar
- **Validation**: Pydantic models
- **Async Support**: Full async/await implementation

## 📁 Project Structure

```
ecommerce-rest-api/
├── app/
│   ├── api/                    # API endpoints and controllers
│   │   └── v1/
│   │       ├── product.py      # Product management endpoints
│   │       ├── user.py         # User management endpoints
│   │       └── order.py        # Order management endpoints
│   ├── core/                   # Core application configuration
│   │   ├── database.py         # Database connection and session management
│   │   ├── dependencies.py     # Dependency injection setup
│   │   ├── security.py         # Security and authentication
│   │   └── redis.py            # Redis connection for token management
│   ├── models/                 # Database models (SQLModel)
│   │   ├── user.py             # User database model
│   │   ├── product.py          # Product database model
│   │   └── order.py            # Order and order item models
│   ├── repositories/           # Data access layer
│   │   ├── user.py             # User data operations
│   │   ├── product.py          # Product data operations
│   │   └── order.py            # Order data operations
│   ├── schemas/                # Pydantic models for API
│   │   ├── user.py             # User request/response schemas
│   │   ├── product.py          # Product request/response schemas
│   │   └── order.py            # Order request/response schemas
│   ├── services/               # Business logic layer
│   │   ├── user.py             # User business logic
│   │   ├── product.py          # Product business logic
│   │   └── order.py            # Order business logic
│   ├── utils/                  # Utility functions
│   │   └── security.py         # Security utilities (JWT, password hashing)
│   ├── exceptions.py           # Custom exception classes
│   ├── config.py               # Application configuration
│   └── main.py                 # Application entry point
├── requirements.txt             # Python dependencies
├── README.md                   # This file
├── ORDER_SYSTEM_README.md      # Detailed order system documentation
├── STOCK_HEALTH_EXAMPLES.md    # Stock health endpoint examples
└── .env.example                # Environment variables template
```

## 🔄 Application Flow

### **1. User Authentication Flow**
```
User Registration → Password Hashing → Database Storage → JWT Token Generation
     ↓
User Login → Credential Validation → JWT Token Issuance → Token Storage in Redis
     ↓
API Requests → JWT Validation → Role-based Access Control → Resource Access
```

### **2. Product Management Flow**
```
Product Creation → Validation → Database Storage → Stock Initialization
     ↓
Product Updates → Business Rule Validation → Database Update → Stock Adjustment
     ↓
Product Retrieval → Filtering/Pagination → Response Serialization → Client Delivery
```

### **3. Order Processing Flow**
```
Order Creation → Stock Validation → Business Rule Checks → Order Creation
     ↓
Stock Update → Inventory Reduction → Order Confirmation → Response Delivery
     ↓
Order Management → Status Updates → Admin Controls → Customer Notifications
```

### **4. Stock Management Flow**
```
Stock Monitoring → Real-time Validation → Alert Generation → Admin Dashboard
     ↓
Inventory Analysis → Stock Categorization → Health Metrics → Business Insights
     ↓
Proactive Management → Reorder Triggers → Stock Optimization → Performance Metrics
```

## 🚀 Getting Started

### **Prerequisites**
- Python 3.8+
- PostgreSQL 12+
- Redis (optional, for token blacklisting)
- pip or poetry

### **Installation**

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ecommerce-rest-api.git
cd ecommerce-rest-api
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your database and security settings
```

5. **Database setup**
```bash
# Create PostgreSQL database
createdb ecommerce_db

# Run database migrations (if using Alembic)
alembic upgrade head
```

6. **Start the application**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```



## 📚 API Documentation

### **Interactive Documentation**
- **Swagger UI**: `http://localhost:8000/docs`
- **Scalar**: `http://localhost:8000/scalar`

### **API Endpoints Overview**

#### **Authentication & Users**
```
POST /api/v1/users/           # User registration
POST /api/v1/users/login      # User authentication
GET  /api/v1/users/logout     # User logout
GET  /api/v1/users/{id}       # Get user profile
PUT  /api/v1/users/{id}       # Update user profile
GET  /api/v1/users/           # List users (admin only)
```

#### **Product Management**
```
POST   /api/v1/products/      # Create product
GET    /api/v1/products/      # List products with filtering
GET    /api/v1/products/{id}  # Get product details
PUT    /api/v1/products/{id}  # Update product
DELETE /api/v1/products/{id}  # Delete product
```

#### **Order Management**
```
POST   /api/v1/orders/                    # Create order
GET    /api/v1/orders/                    # List all orders (admin only)
GET    /api/v1/orders/my-orders           # Get user's orders
GET    /api/v1/orders/{id}                # Get order details
PUT    /api/v1/orders/{id}/status         # Update order status (admin)
DELETE /api/v1/orders/{id}                # Delete order
GET    /api/v1/orders/health/stock-check  # Stock health monitoring
```

## 🔐 Security Features

### **Authentication & Authorization**
- **JWT Token-based Authentication**
- **Role-based Access Control** (Customer/Admin)
- **Password Hashing** with bcrypt
- **Token Blacklisting** for logout functionality
- **Secure Password Validation**

### **Data Protection**
- **Input Validation** with Pydantic
- **SQL Injection Prevention**
- **XSS Protection**
- **Environment Variable Security**

## 📊 Business Logic

### **Order Processing Rules**
- **Stock Validation**: Orders cannot be placed without sufficient stock
- **Automatic Stock Updates**: Inventory is reduced after successful orders
- **Transaction Safety**: Rollback on failure ensures data consistency
- **Access Control**: Users can only manage their own orders

### **Inventory Management**
- **Real-time Stock Monitoring**: Live inventory tracking
- **Stock Categorization**: Critical, low, medium, and high stock levels
- **Automated Alerts**: Low stock and out-of-stock notifications
- **Stock Health Metrics**: Comprehensive inventory analytics

### **User Management**
- **Email Uniqueness**: Prevents duplicate user accounts
- **Role-based Permissions**: Different capabilities for customers and admins
- **Profile Management**: Secure user data updates
- **Session Management**: Secure token handling

## 🧪 Testing

### **Running Tests**
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

### **Test Structure**
```
tests/
├── test_api/          # API endpoint tests
├── test_services/     # Business logic tests
├── test_repositories/ # Data access tests
└── conftest.py        # Test configuration
```

## 🚀 Deployment

### **Production Deployment**
```bash
# Install production dependencies
pip install -r requirements.txt

# Set production environment variables
export ENVIRONMENT=production

# Start with production server
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### **Docker Deployment**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Environment Considerations**
- **Database**: Use connection pooling and read replicas
- **Caching**: Implement Redis for session and data caching
- **Monitoring**: Add logging, metrics, and health checks
- **Security**: Use HTTPS, rate limiting, and API keys

## 📈 Performance & Scalability

### **Optimization Features**
- **Async/Await**: Full asynchronous implementation
- **Connection Pooling**: Efficient database connection management
- **Lazy Loading**: Optimized relationship loading
- **Pagination**: Efficient large dataset handling

### **Scalability Considerations**
- **Horizontal Scaling**: Stateless application design
- **Database Sharding**: Support for multiple database instances
- **Caching Strategy**: Redis-based caching implementation
- **Load Balancing**: Ready for load balancer deployment

## 🔧 Configuration & Customization

### **Database Configuration**
- **Connection Pooling**: Configurable pool size and overflow
- **Schema Management**: Organized business data in sales schema
- **Migration Support**: Alembic integration ready

### **Security Configuration**
- **JWT Settings**: Configurable secret and algorithm
- **Password Policies**: Configurable hashing algorithms
- **Session Management**: Configurable token expiration

## 🤝 Contributing

### **Development Setup**
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Commit your changes: `git commit -m 'Add amazing feature'`
5. Push to the branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

### **Code Standards**
- **Type Hints**: Use Python type hints throughout
- **Documentation**: Follow docstring conventions
- **Testing**: Maintain high test coverage
- **Linting**: Use flake8 and black for code formatting

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### **Documentation**
- **API Documentation**: Available at `/docs` endpoint
- **Code Documentation**: Comprehensive docstrings throughout
- **README Files**: Detailed guides for each major component

### **Issues & Questions**
- **GitHub Issues**: Report bugs and request features
- **Discussions**: Ask questions and share ideas
- **Wiki**: Additional documentation and guides

## 🎯 Roadmap

### **Planned Features**
- **Payment Integration**: Stripe, PayPal integration
- **Email Notifications**: Order updates and marketing emails
- **Advanced Analytics**: Business intelligence dashboard
- **Mobile API**: Mobile-optimized endpoints
- **Webhook Support**: Real-time event notifications

### **Infrastructure Improvements**
- **Microservices**: Service decomposition
- **Event Sourcing**: Complete audit trail
- **CQRS**: Separate read/write models
- **GraphQL**: Alternative to REST API

---

## 🚀 Quick Start Example

```bash
# Clone and setup
git clone https://github.com/yourusername/ecommerce-rest-api.git
cd ecommerce-rest-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start the server
uvicorn app.main:app --reload

# Visit http://localhost:8000/docs for interactive API documentation
```

---

**Built with ❤️ using FastAPI, SQLAlchemy, and PostgreSQL**

For detailed documentation on specific components, see:
- [Order System Documentation](ORDER_SYSTEM_README.md)
- [Stock Health Examples](STOCK_HEALTH_EXAMPLES.md)
