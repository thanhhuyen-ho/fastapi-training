import json
from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel, Field
from model import Book
from starlette.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse

app = FastAPI()
@app.get("/books/{book_id}")

def read_book(book_id: int):
    return {"book_id": book_id,
            "title": "The Great Gatsby", 
            "author": "F. Scott Fitzgerald"
            }
    
@app.get("/authors/{author_id}")
def read_author(author_id: int):
    return {"author_id": author_id,
            "name": "Ernest Hemingway", 
            }
    
@app.get("/books")
async def read_books(year: int = None):
    if year:
        return { "year": year, 
                 "book": ["Book 1", "Book 2"] 
                }
    return {"book": ["All books"]}

@app.post("/books")
async def create_book(book: Book):
    return book

class Book(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    author: str = Field(..., min_length=1, max_length=50)
    year: int = Field(..., gt=1900, lt=2100)
    
class BookResponse(BaseModel):
    title: str
    author: str
    
@app.get("/allbooks")
async def get_all_books() -> list[BookResponse]:
    return [
        {
            "id": 1,
            "title": "1984",
            "author": "George Orwell"
        },
        {
            "id": 1,
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald"
        }
    ]
    
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": f"Oops! something went wrong"},
    )
    
@app.get("/error_endpoint")
async def raise_exception():
    raise(HTTPException(status_code=400))

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request:Request, exc:RequestValidationError):
    return PlainTextResponse("This is a plain text response:"
                             f" \n{json.dumps(exc.errors(),indent=2,)}",
                             status_code=status.HTTP_400_BAD_REQUEST)