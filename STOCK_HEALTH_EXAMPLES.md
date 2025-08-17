# Stock Health Endpoint - Comprehensive Examples

## Overview

The enhanced `/orders/health/stock-check` endpoint provides administrators with comprehensive stock management insights, including all products with available stock, low stock alerts, and detailed inventory analytics.

## Endpoint Details

```http
GET /api/v1/orders/health/stock-check
Authorization: Bearer <admin_jwt_token>
```

## Query Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `category` | string | Filter by stock category | `?category=available` |
| `min_stock` | integer | Minimum stock quantity filter | `?min_stock=5` |
| `max_stock` | integer | Maximum stock quantity filter | `?max_stock=100` |

### Available Categories
- `available` - Products with any stock
- `low` - Products with low stock (≤10 units)
- `out_of_stock` - Products with zero stock
- `critical` - Products with critical stock (≤5 units)
- `high` - Products with high stock (>50 units)
- `medium` - Products with medium stock (11-50 units)

## Response Structure

### Basic Response (No Filters)
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T14:30:00Z",
  "message": "Stock management system is operational",
  "stock_summary": {
    "summary": {
      "total_products": 25,
      "products_with_stock": 20,
      "products_low_stock": 5,
      "products_out_of_stock": 5,
      "stock_health_percentage": 80.0
    },
    "stock_categories": {
      "available_stock": [...],
      "low_stock": [...],
      "out_of_stock": [...]
    },
    "stock_distribution": {
      "high_stock": [...],
      "medium_stock": [...],
      "critical_stock": [...]
    },
    "alerts": {
      "low_stock_alerts": 5,
      "out_of_stock_alerts": 5,
      "critical_stock_alerts": 3
    },
    "timestamp": "2024-01-15T14:30:00Z"
  },
  "filters_applied": {
    "category": null,
    "min_stock": null,
    "max_stock": null
  }
}
```

### Product Information Structure
```json
{
  "product_id": 1,
  "name": "Premium Widget",
  "stock_quantity": 15,
  "price": 29.99,
  "stock_value": 449.85
}
```

## Usage Examples

### 1. View All Products with Available Stock

```http
GET /api/v1/orders/health/stock-check?category=available
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T14:30:00Z",
  "message": "Stock management system is operational",
  "stock_summary": {
    "summary": {
      "total_products": 25,
      "products_with_stock": 20,
      "products_low_stock": 0,
      "products_out_of_stock": 0,
      "stock_health_percentage": 100.0
    },
    "stock_categories": {
      "available_stock": [
        {
          "product_id": 1,
          "name": "Premium Widget",
          "stock_quantity": 15,
          "price": 29.99,
          "stock_value": 449.85
        },
        {
          "product_id": 2,
          "name": "Basic Gadget",
          "stock_quantity": 45,
          "price": 19.99,
          "stock_value": 899.55
        }
      ],
      "low_stock": [],
      "out_of_stock": []
    },
    "stock_distribution": {
      "high_stock": [
        {
          "product_id": 2,
          "name": "Basic Gadget",
          "stock_quantity": 45,
          "price": 19.99,
          "stock_value": 899.55
        }
      ],
      "medium_stock": [
        {
          "product_id": 1,
          "name": "Premium Widget",
          "stock_quantity": 15,
          "price": 29.99,
          "stock_value": 449.85
        }
      ],
      "critical_stock": []
    },
    "alerts": {
      "low_stock_alerts": 0,
      "out_of_stock_alerts": 0,
      "critical_stock_alerts": 0
    }
  },
  "filters_applied": {
    "category": "available",
    "min_stock": null,
    "max_stock": null
  }
}
```

### 2. View Low Stock Products

```http
GET /api/v1/orders/health/stock-check?category=low
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T14:30:00Z",
  "message": "Stock management system is operational",
  "stock_summary": {
    "summary": {
      "total_products": 25,
      "products_with_stock": 5,
      "products_low_stock": 5,
      "products_out_of_stock": 0,
      "stock_health_percentage": 100.0
    },
    "stock_categories": {
      "available_stock": [],
      "low_stock": [
        {
          "product_id": 3,
          "name": "Rare Component",
          "stock_quantity": 8,
          "price": 99.99,
          "stock_value": 799.92
        },
        {
          "product_id": 4,
          "name": "Limited Edition",
          "stock_quantity": 3,
          "price": 149.99,
          "stock_value": 449.97
        }
      ],
      "out_of_stock": []
    },
    "stock_distribution": {
      "high_stock": [],
      "medium_stock": [],
      "critical_stock": [
        {
          "product_id": 4,
          "name": "Limited Edition",
          "stock_quantity": 3,
          "price": 149.99,
          "stock_value": 449.97
        }
      ]
    },
    "alerts": {
      "low_stock_alerts": 5,
      "out_of_stock_alerts": 0,
      "critical_stock_alerts": 1
    }
  },
  "filters_applied": {
    "category": "low",
    "min_stock": null,
    "max_stock": null
  }
}
```

### 3. Filter by Stock Quantity Range

```http
GET /api/v1/orders/health/stock-check?min_stock=10&max_stock=50
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T14:30:00Z",
  "message": "Stock management system is operational",
  "stock_summary": {
    "summary": {
      "total_products": 25,
      "products_with_stock": 8,
      "products_low_stock": 0,
      "products_out_of_stock": 0,
      "stock_health_percentage": 100.0
    },
    "stock_categories": {
      "available_stock": [
        {
          "product_id": 1,
          "name": "Premium Widget",
          "stock_quantity": 15,
          "price": 29.99,
          "stock_value": 449.85
        },
        {
          "product_id": 5,
          "name": "Standard Item",
          "stock_quantity": 25,
          "price": 15.99,
          "stock_value": 399.75
        }
      ],
      "low_stock": [],
      "out_of_stock": []
    },
    "stock_distribution": {
      "high_stock": [],
      "medium_stock": [
        {
          "product_id": 1,
          "name": "Premium Widget",
          "stock_quantity": 15,
          "price": 29.99,
          "stock_value": 449.85
        },
        {
          "product_id": 5,
          "name": "Standard Item",
          "stock_quantity": 25,
          "price": 15.99,
          "stock_value": 399.75
        }
      ],
      "critical_stock": []
    },
    "alerts": {
      "low_stock_alerts": 0,
      "out_of_stock_alerts": 0,
      "critical_stock_alerts": 0
    }
  },
  "filters_applied": {
    "category": null,
    "min_stock": 10,
    "max_stock": 50
  }
}
```

### 4. Combined Filters

```http
GET /api/v1/orders/health/stock-check?category=critical&min_stock=1
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T14:30:00Z",
  "message": "Stock management system is operational",
  "stock_summary": {
    "summary": {
      "total_products": 25,
      "products_with_stock": 3,
      "products_low_stock": 0,
      "products_out_of_stock": 0,
      "stock_health_percentage": 100.0
    },
    "stock_categories": {
      "available_stock": [],
      "low_stock": [],
      "out_of_stock": []
    },
    "stock_distribution": {
      "high_stock": [],
      "medium_stock": [],
      "critical_stock": [
        {
          "product_id": 4,
          "name": "Limited Edition",
          "stock_quantity": 3,
          "price": 149.99,
          "stock_value": 449.97
        },
        {
          "product_id": 6,
          "name": "Specialty Tool",
          "stock_quantity": 2,
          "price": 79.99,
          "stock_value": 159.98
        }
      ]
    },
    "alerts": {
      "low_stock_alerts": 0,
      "out_of_stock_alerts": 0,
      "critical_stock_alerts": 2
    }
  },
  "filters_applied": {
    "category": "critical",
    "min_stock": 1,
    "max_stock": null
  }
}
```

## Stock Thresholds

The system automatically categorizes products based on these thresholds:

| Category | Stock Range | Description |
|----------|-------------|-------------|
| **Critical** | 1-5 units | Immediate attention required |
| **Low** | 6-10 units | Reorder soon |
| **Medium** | 11-50 units | Normal stock levels |
| **High** | 51+ units | Well stocked |

## Business Intelligence Features

### 1. Stock Health Percentage
- Calculated as: `(products_with_stock / total_products) * 100`
- Provides quick overview of inventory health
- Helps identify when bulk restocking is needed

### 2. Stock Value Analysis
- Each product includes `stock_value` (price × quantity)
- Total stock value across all products
- Helps with inventory valuation and financial planning

### 3. Alert System
- **Low Stock Alerts**: Products needing reorder
- **Out of Stock Alerts**: Products completely unavailable
- **Critical Stock Alerts**: Products at risk of going out of stock

### 4. Distribution Analysis
- Categorizes products by stock levels
- Helps identify inventory patterns
- Supports strategic restocking decisions

## Use Cases

### Inventory Management
```bash
# Check overall stock health
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://localhost:8000/api/v1/orders/health/stock-check"

# Find products needing immediate attention
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://localhost:8000/api/v1/orders/health/stock-check?category=critical"

# Identify products for bulk restocking
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://localhost:8000/api/v1/orders/health/stock-check?min_stock=50"
```

### Financial Planning
```bash
# Calculate total inventory value
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://localhost:8000/api/v1/orders/health/stock-check" | \
  jq '.stock_summary.stock_categories.available_stock | map(.stock_value) | add'
```

### Supplier Management
```bash
# Find products to reorder
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://localhost:8000/api/v1/orders/health/stock-check?category=low"
```

## Error Handling

### Insufficient Permissions
```json
{
  "detail": "Admin privileges required to view all orders"
}
```

### System Errors
```json
{
  "status": "unhealthy",
  "timestamp": "2024-01-15T14:30:00Z",
  "error": "Database connection failed",
  "message": "Failed to retrieve stock health information"
}
```

## Performance Considerations

- **Efficient Queries**: Single database query for all product information
- **In-Memory Processing**: Stock categorization done in application layer
- **Flexible Filtering**: Client-side filtering reduces server load
- **Caching Potential**: Stock data can be cached for frequent access

## Monitoring & Alerts

### Automated Monitoring
- Set up regular health checks
- Monitor stock health percentage trends
- Track critical stock alerts over time

### Integration Possibilities
- Connect to inventory management systems
- Integrate with supplier ordering systems
- Set up automated reorder triggers
- Send notifications for critical stock levels

This enhanced stock health endpoint provides administrators with comprehensive inventory insights, enabling better decision-making and proactive inventory management.
