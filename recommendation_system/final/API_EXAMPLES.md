# API Usage Examples

This document provides detailed examples of how to use the Recommendation System API using different tools.

## Table of Contents

- [cURL Examples](#curl-examples)
- [Python Requests Examples](#python-requests-examples)
- [Postman Collection](#postman-collection)
- [JavaScript/Fetch Examples](#javascriptfetch-examples)

## cURL Examples

### Health Check

```bash
curl -X GET http://localhost:8000/health
```

### Customer Product Recommendations

```bash
curl -X POST http://localhost:8000/recommend/customer \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 123,
    "top_k": 5
  }'
```

### Brand Owner Raw Material Recommendations

```bash
curl -X POST http://localhost:8000/recommend/raw_materials \
  -H "Content-Type: application/json" \
  -d '{
    "owner_id": 55,
    "top_k": 5
  }'
```

### Retrain Models

```bash
curl -X POST http://localhost:8000/retrain
```

## Python Requests Examples

### Installation

```bash
pip install requests
```

### Example Script

```python
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

# Health Check
def check_health():
    response = requests.get(f"{BASE_URL}/health")
    print("Health Check:", response.json())

# Get Customer Recommendations
def get_customer_recommendations(customer_id, top_k=5):
    payload = {
        "customer_id": customer_id,
        "top_k": top_k
    }
    
    response = requests.post(
        f"{BASE_URL}/recommend/customer",
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nRecommendations for Customer {customer_id}:")
        for i, rec in enumerate(data['recommendations'], 1):
            print(f"{i}. {rec['name']} - ${rec['price']:.2f} (Score: {rec['score']:.4f})")
    else:
        print(f"Error: {response.status_code} - {response.text}")

# Get Owner Recommendations
def get_owner_recommendations(owner_id, top_k=5):
    payload = {
        "owner_id": owner_id,
        "top_k": top_k
    }
    
    response = requests.post(
        f"{BASE_URL}/recommend/raw_materials",
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nRecommendations for Owner {owner_id}:")
        for i, rec in enumerate(data['recommendations'], 1):
            print(f"{i}. {rec['name']} - ${rec['unit_cost']:.2f} (Score: {rec['score']:.4f})")
            print(f"   Reason: {rec['reason']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

# Retrain Models
def retrain_models():
    response = requests.post(f"{BASE_URL}/retrain")
    
    if response.status_code == 200:
        data = response.json()
        print("\nRetrain Status:", data['status'])
        print("Message:", data['message'])
        print("Models Retrained:", data['models_retrained'])
    else:
        print(f"Error: {response.status_code} - {response.text}")

# Main execution
if __name__ == "__main__":
    # Check health
    check_health()
    
    # Get recommendations
    get_customer_recommendations(customer_id=1, top_k=5)
    get_owner_recommendations(owner_id=1, top_k=5)
    
    # Uncomment to retrain models
    # retrain_models()
```

## Postman Collection

### Import Instructions

1. Open Postman
2. Click "Import" button
3. Select "Raw text"
4. Paste the JSON below
5. Click "Import"

### Postman Collection JSON

```json
{
  "info": {
    "name": "Recommendation System API",
    "description": "API for customer product and brand owner raw material recommendations",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/health",
          "host": ["{{base_url}}"],
          "path": ["health"]
        }
      }
    },
    {
      "name": "Customer Recommendations",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"customer_id\": 123,\n  \"top_k\": 5\n}"
        },
        "url": {
          "raw": "{{base_url}}/recommend/customer",
          "host": ["{{base_url}}"],
          "path": ["recommend", "customer"]
        }
      }
    },
    {
      "name": "Owner Recommendations",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"owner_id\": 55,\n  \"top_k\": 5\n}"
        },
        "url": {
          "raw": "{{base_url}}/recommend/raw_materials",
          "host": ["{{base_url}}"],
          "path": ["recommend", "raw_materials"]
        }
      }
    },
    {
      "name": "Retrain Models",
      "request": {
        "method": "POST",
        "header": [],
        "url": {
          "raw": "{{base_url}}/retrain",
          "host": ["{{base_url}}"],
          "path": ["retrain"]
        }
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000",
      "type": "string"
    }
  ]
}
```

### Environment Variables

Create a Postman environment with:
- `base_url`: `http://localhost:8000` (or your deployed URL)

## JavaScript/Fetch Examples

### Customer Recommendations

```javascript
async function getCustomerRecommendations(customerId, topK = 5) {
  try {
    const response = await fetch('http://localhost:8000/recommend/customer', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        customer_id: customerId,
        top_k: topK
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('Recommendations:', data);
    return data;
  } catch (error) {
    console.error('Error:', error);
  }
}

// Usage
getCustomerRecommendations(123, 5);
```

### Owner Recommendations

```javascript
async function getOwnerRecommendations(ownerId, topK = 5) {
  try {
    const response = await fetch('http://localhost:8000/recommend/raw_materials', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        owner_id: ownerId,
        top_k: topK
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('Recommendations:', data);
    return data;
  } catch (error) {
    console.error('Error:', error);
  }
}

// Usage
getOwnerRecommendations(55, 5);
```

### Health Check

```javascript
async function checkHealth() {
  try {
    const response = await fetch('http://localhost:8000/health');
    const data = await response.json();
    console.log('Health Status:', data);
    return data;
  } catch (error) {
    console.error('Error:', error);
  }
}

// Usage
checkHealth();
```

## Response Examples

### Successful Customer Recommendation Response

```json
{
  "customer_id": 123,
  "recommendations": [
    {
      "product_id": 45,
      "name": "Smartphones Product 45",
      "category": "Electronics",
      "subcategory": "Smartphones",
      "price": 899.99,
      "score": 0.8542
    },
    {
      "product_id": 78,
      "name": "Laptops Product 78",
      "category": "Electronics",
      "subcategory": "Laptops",
      "price": 1299.99,
      "score": 0.7823
    }
  ],
  "total_recommendations": 2
}
```

### Successful Owner Recommendation Response

```json
{
  "owner_id": 55,
  "recommendations": [
    {
      "material_id": 12,
      "name": "Cotton Grade 12",
      "category": "Textiles",
      "unit_cost": 15.50,
      "score": 0.7234,
      "reason": "Similar to Polyester Grade 8"
    },
    {
      "material_id": 34,
      "name": "Cardboard Grade 34",
      "category": "Packaging",
      "unit_cost": 2.30,
      "score": 0.6891,
      "reason": "Based on production trends"
    }
  ],
  "total_recommendations": 2
}
```

### Error Response

```json
{
  "error": "Model not loaded",
  "detail": "Customer recommendation model not available. Please train the model first."
}
```

## Rate Limiting

Currently, there are no rate limits. For production deployment, consider implementing rate limiting using:
- FastAPI middleware
- Nginx rate limiting
- API Gateway (AWS, Azure, GCP)

## Authentication

The current implementation does not include authentication. For production, consider adding:
- API keys
- OAuth 2.0
- JWT tokens

Example with API key:

```python
headers = {
    "Content-Type": "application/json",
    "X-API-Key": "your-api-key-here"
}

response = requests.post(url, json=payload, headers=headers)
```

## Best Practices

1. **Error Handling**: Always check response status codes
2. **Timeouts**: Set appropriate timeouts for requests
3. **Retries**: Implement retry logic for transient failures
4. **Logging**: Log all API calls for debugging
5. **Validation**: Validate input data before sending requests

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure the server is running
   - Check the port number
   - Verify firewall settings

2. **Model Not Loaded**
   - Train the models first using training scripts
   - Check model file paths in configuration

3. **Invalid Customer/Owner ID**
   - Ensure IDs exist in the dataset
   - Check ID ranges (1-1000 for customers, 1-100 for owners)

4. **Timeout Errors**
   - Increase request timeout
   - Check server resources
   - Consider model optimization

## Support

For issues or questions:
- Check the [README](README.md)
- Review API documentation at `/docs`
- Open an issue on GitHub
