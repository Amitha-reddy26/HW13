# HW13 — FastAPI Authentication + Calculator 

This application provides:
- A FastAPI backend with user registration, login, JWT authentication, and calculator operations.
- A simple HTML front-end for interacting with the API.
- Full end-to-end testing using Playwright.
- Docker containerization with a published Docker Hub image.

---


# Running the App

### **Start FastAPI locally**
```bash
uvicorn main:app --reload
```
Visit 
http://127.0.0.1:8000/docs

Server runs at:
ttp://127.0.0.1:8000
http://127.0.0.1:8000/docs (Swagger API)

---

## Running the tests
``` bash
pytest
```

--- 

# Running the Front-end

### The front-end files are located in the templates/ folder:
templates/index.html
templates/register.html
templates/login.html

### To test the UI:

Start the backend:
uvicorn main:app --reload

Open in browser:
http://127.0.0.1:8000/
http://127.0.0.1:8000/register
http://127.0.0.1:8000/login

### These pages communicate with the backend using JavaScript fetch().



--- 
# Running the Playwright Tests

``` bash
npx playwright test
```


## Dockerhub link

https://hub.docker.com/repository/docker/ab2609/hw13/general
