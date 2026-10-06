# Implement Standardized Global API Response Formatter

## Changelog & Recent Updates

### Implement Standardized Global API Response Formatter

Currently, our API endpoints return varying JSON structures depending on the route and whether it's a success or an error. To ensure a seamless integration with the frontend and to simplify debugging, we need to introduce a global api_response utility. All routes and global error handlers must be refactored to use this function.

The standard response structure must exactly match:

```
json
```

```
{
    "status_code": 200,
    "is_success": true,
    "message": "Descriptive message here",
    "data": { ... } // or [] or null
}

```


---

✅ Acceptance Criteria (AC)

**Acceptance Criteria:**
AC 1: Create Global Response Utility

• Given the backend codebase,
• When a new file for utilities is created (e.g., backend/app/utils/responses.py),
• Then it must contain the api_response(status_code: int, is_success: bool, message: str, data=None) function.
• And the function must strictly return a Flask jsonify object containing the keys status_code, is_success, message, and data, along with 
