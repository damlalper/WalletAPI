# Wallet API

A minimal but production-minded Wallet (expense tracker) REST service.

## Setup and Running

1. **Install dependencies:**
   ```bash
   uv pip install -e .
   ```

2. **Run the server:**
   ```bash
   uv run python -m app.main
   ```
   The API will be available at `http://127.0.0.1:8000`.

3. **Run tests:**
   ```bash
   uv run python -m pytest
   ```

## Database

The application uses a SQLite database file `app.db` which is created in the project root.

Tests use an in-memory SQLite database and do not affect `app.db`.

## Example `curl` Commands

**Create an expense:**
```bash
curl -X POST "http://127.0.0.1:8000/expenses" -H "Content-Type: application/json" -d \
'{
  "title": "Coffee",
  "amount": "3.50",
  "currency": "USD",
  "category": "Food",
  "note": "Cafe near office",
  "spent_at": "2025-10-15T09:30:00Z"
}'
```

**Get an expense by ID:**
```bash
curl http://127.0.0.1:8000/expenses/1
```

**List expenses:**
```bash
curl "http://127.0.0.1:8000/expenses?limit=10&category=Food"
```

**Update an expense:**
```bash
curl -X PATCH "http://127.0.0.1:8000/expenses/1" -H "Content-Type: application/json" -d '{"title": "Espresso"}'
```

**Delete an expense:**
```bash
curl -X DELETE http://127.0.0.1:8000/expenses/1
```

**Get a summary report:**
```bash
curl "http://127.0.0.1:8000/reports/summary?from=2025-10-01&to=2025-10-31&group_by=category"
```

**Export expenses to CSV:**
```bash
curl "http://127.0.0.1:8000/export?from=2025-10-01&to=2025-10-31&format=csv"
```
