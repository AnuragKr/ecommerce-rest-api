# Order Management System

## Overview

The Order Management System provides comprehensive CRUD operations for e-commerce orders with advanced features including stock validation, access control, and business rule enforcement.

## Key Features

### 🛡️ **Stock Management & Validation**
- **Pre-order Stock Check**: Validates product availability before order creation
- **Automatic Stock Updates**: Reduces stock quantities after successful orders
- **Real-time Validation**: Prevents orders when stock is insufficient
- **Detailed Stock Feedback**: Provides specific stock issues to users

### 🔐 **Access Control & Security**
- **User Isolation**: Customers can only view/manage their own orders
- **Admin Privileges**: Administrators can access and manage all orders
- **Role-based Permissions**: Different capabilities for customers vs. admins
- **Secure Endpoints**: All endpoints require authentication

### 📊 **Order Lifecycle Management**
- **Status Tracking**: pending → confirmed → shipped → delivered → cancelled
- **Admin Status Updates**: Only administrators can change order statuses
- **Order History**: Complete audit trail of order changes
- **Flexible Filtering**: Advanced search and filtering capabilities

## API Endpoints

### Customer Endpoints

#### Create Order
```http
POST /api/v1/orders/
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "shipping_address_line1": "123 Main St",
  "shipping_city": "New York",
  "shipping_state": "NY",
  "shipping_postal_code": "10001",
  "shipping_country": "USA",
  "order_items": [
    {
      "product_id": 1,
      "quantity": 2
    }
  ]
}
```

**Features:**
- ✅ Automatic stock validation
- ✅ Price calculation from current product prices
- ✅ Transaction safety with rollback on failure
- ✅ Automatic stock quantity reduction

#### View My Orders
```http
GET /api/v1/orders/my-orders?skip=0&limit=10
Authorization: Bearer <jwt_token>
```

#### View Specific Order
```http
GET /api/v1/orders/{order_id}
Authorization: Bearer <jwt_token>
```

#### Delete Order (Pending Only)
```http
DELETE /api/v1/orders/{order_id}
Authorization: Bearer <jwt_token>
```

**Restrictions:**
- Only pending orders can be deleted
- Users can only delete their own orders

#### Order Statistics
```http
GET /api/v1/orders/{order_id}/statistics
Authorization: Bearer <jwt_token>
```

### Admin Endpoints

#### List All Orders
```http
GET /api/v1/orders/?status=pending&user_id=123&min_amount=50.00
Authorization: Bearer <jwt_token>
```

**Filter Options:**
- `status`: Order status filter
- `user_id`: Filter by specific user
- `start_date` / `end_date`: Date range filtering
- `min_amount` / `max_amount`: Amount range filtering

#### Update Order Status
```http
PUT /api/v1/orders/{order_id}/status
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "status": "confirmed"
}
```

**Valid Statuses:**
- `pending` - Order placed, awaiting confirmation
- `confirmed` - Order confirmed by admin
- `shipped` - Order has been shipped
- `delivered` - Order delivered to customer
- `cancelled` - Order cancelled

#### Stock Health Check
```http
GET /api/v1/orders/health/stock-check
Authorization: Bearer <jwt_token>
```

## Business Rules & Edge Cases

### 🚫 **Order Prevention Scenarios**

#### Insufficient Stock
```json
{
  "detail": {
    "message": "Some products have insufficient stock",
    "stock_issues": [
      {
        "product_id": 1,
        "product_name": "Premium Widget",
        "requested": 5,
        "available": 2,
        "available": false,
        "error": "Insufficient stock. Available: 2, Requested: 5"
      }
    ]
  }
}
```

#### Invalid Order Data
- Empty order items list
- Zero or negative quantities
- Missing shipping information

### ✅ **Order Success Scenarios**

#### Stock Available
- All products have sufficient stock
- Order is created successfully
- Product stock is automatically reduced
- Order totals are calculated correctly

#### Access Control
- Users can only access their own orders
- Admins can access all orders
- Proper error messages for unauthorized access

## Database Schema

### Orders Table
```sql
CREATE TABLE sales.orders (
    order_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES sales.users(user_id),
    order_date TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    total_amount DECIMAL(10,2) NOT NULL,
    shipping_address_line1 VARCHAR(255) NOT NULL,
    shipping_address_line2 VARCHAR(255),
    shipping_city VARCHAR(100) NOT NULL,
    shipping_state VARCHAR(100) NOT NULL,
    shipping_postal_code VARCHAR(20) NOT NULL,
    shipping_country VARCHAR(100) NOT NULL
);
```

### Order Items Table
```sql
CREATE TABLE sales.order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES sales.orders(order_id),
    product_id INTEGER REFERENCES sales.products(product_id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL
);
```

## Error Handling

### HTTP Status Codes
- **200**: Success
- **400**: Bad Request (insufficient stock, invalid data)
- **401**: Unauthorized (missing/invalid token)
- **403**: Forbidden (insufficient permissions)
- **404**: Not Found (order doesn't exist)
- **500**: Internal Server Error

### Error Response Format
```json
{
  "detail": "Error message description"
}
```

### Stock Error Response Format
```json
{
  "detail": {
    "message": "Some products have insufficient stock",
    "stock_issues": [
      {
        "product_id": 1,
        "product_name": "Product Name",
        "requested": 5,
        "available": 2,
        "available": false,
        "error": "Detailed error message"
      }
    ]
  }
}
```

## Security Features

### Authentication
- JWT token required for all endpoints
- Token validation on every request
- Automatic token expiration handling

### Authorization
- Role-based access control (customer/admin)
- User isolation (customers see only their orders)
- Admin privileges for system-wide operations

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection through proper output encoding

## Performance Considerations

### Database Optimization
- Proper indexing on frequently queried fields
- Efficient relationship loading with `selectinload`
- Pagination support for large result sets

### Caching Strategy
- Redis integration for session management
- Token blacklisting for logout functionality
- Potential for order result caching

## Monitoring & Logging

### Comprehensive Logging
- Order creation/deletion events
- Stock validation failures
- Access control violations
- Performance metrics

### Health Checks
- Database connectivity monitoring
- Stock system health status
- API endpoint availability

## Testing Scenarios

### Unit Tests
- Stock validation logic
- Order calculation accuracy
- Access control validation
- Error handling scenarios

### Integration Tests
- End-to-end order creation
- Stock update verification
- Database transaction integrity
- API response validation

### Edge Case Tests
- Insufficient stock scenarios
- Invalid order data handling
- Permission boundary testing
- Concurrent order processing

## Future Enhancements

### Planned Features
- **Order Notifications**: Email/SMS updates for status changes
- **Inventory Alerts**: Low stock notifications for admins
- **Order Analytics**: Advanced reporting and insights
- **Bulk Operations**: Mass order status updates
- **Order Templates**: Reusable order configurations

### Scalability Improvements
- **Async Processing**: Background job processing for large orders
- **Microservices**: Separate order service deployment
- **Event Sourcing**: Complete order event history
- **CQRS**: Separate read/write models for performance

## Usage Examples

### Creating an Order (Python)
```python
import requests

# Create order
order_data = {
    "shipping_address_line1": "123 Main St",
    "shipping_city": "New York",
    "shipping_state": "NY",
    "shipping_postal_code": "10001",
    "shipping_country": "USA",
    "order_items": [
        {"product_id": 1, "quantity": 2},
        {"product_id": 3, "quantity": 1}
    ]
}

response = requests.post(
    "http://localhost:8000/api/v1/orders/",
    json=order_data,
    headers={"Authorization": f"Bearer {token}"}
)

if response.status_code == 200:
    order = response.json()
    print(f"Order created with ID: {order['order_id']}")
else:
    print(f"Order creation failed: {response.json()}")
```

### Admin Order Management (Python)
```python
# List all pending orders
response = requests.get(
    "http://localhost:8000/api/v1/orders/?status=pending",
    headers={"Authorization": f"Bearer {admin_token}"}
)

# Update order status
response = requests.put(
    "http://localhost:8000/api/v1/orders/123/status",
    json={"status": "confirmed"},
    headers={"Authorization": f"Bearer {admin_token}"}
)
```

## Troubleshooting

### Common Issues

#### Order Creation Fails
1. Check product stock availability
2. Verify all required fields are provided
3. Ensure user authentication is valid
4. Check database connectivity

#### Stock Validation Errors
1. Verify product exists in database
2. Check current stock quantities
3. Ensure no concurrent orders affecting stock
4. Review stock update transaction logs

#### Permission Denied Errors
1. Verify user role (customer vs admin)
2. Check if user owns the order (for customers)
3. Ensure JWT token is valid and not expired
4. Verify token contains correct user information

### Debug Information
- Enable detailed logging in service layer
- Check database transaction logs
- Monitor Redis connection status
- Review API request/response logs

## Support & Maintenance

### Regular Maintenance
- Monitor order processing performance
- Review and optimize database queries
- Update stock validation logic as needed
- Backup order data regularly

### Monitoring Metrics
- Order creation success rate
- Stock validation failure rate
- API response times
- Database connection health
- Error rate by endpoint

This comprehensive order management system ensures robust, secure, and scalable order processing for your e-commerce platform.
