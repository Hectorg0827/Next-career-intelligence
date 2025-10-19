# API Testing Examples

You can test the API using these curl commands or import into Postman/Thunder Client.

## Health Check

```bash
curl http://localhost:8000/api/health
```

## Job Title Autocomplete

```bash
curl "http://localhost:8000/api/jobs/suggest?q=software&limit=5"
```

## Career Analysis

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Software Developer",
    "skills": ["Python", "JavaScript", "SQL", "React"],
    "location": "United States",
    "years_experience": 5
  }'
```

## Test with Different Jobs

### Teacher
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Teacher",
    "skills": ["Curriculum Development", "Classroom Management", "Communication"],
    "location": "United States"
  }'
```

### Graphic Designer
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Graphic Designer",
    "skills": ["Adobe Creative Suite", "UI/UX Design", "Typography"],
    "location": "United States"
  }'
```

### Data Entry Clerk
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Data Entry Clerk",
    "skills": ["Typing", "Data Management", "Microsoft Excel"],
    "location": "United States"
  }'
```

### Nurse Practitioner
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Nurse Practitioner",
    "skills": ["Patient Care", "Diagnosis", "Medical Procedures"],
    "location": "United States"
  }'
```

### Marketing Manager
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Marketing Manager",
    "skills": ["Digital Marketing", "Strategy", "Analytics", "Team Leadership"],
    "location": "United States"
  }'
```

## Interactive API Documentation

Visit http://localhost:8000/docs for the interactive Swagger UI where you can:
- See all available endpoints
- Test API calls directly from the browser
- View request/response schemas
- Download OpenAPI specification
