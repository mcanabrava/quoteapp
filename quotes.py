import sys
sys.path.append("..")

from starlette import status
from starlette.responses import RedirectResponse

from fastapi import Depends, APIRouter, Request, Form
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from .auth import get_current_user

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter(
    prefix="/quotes",
    tags=["quotes"],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/", response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    quotes = db.query(models.Quotes).filter(models.Quotes.owner_id == user.get("id")).all()

    return templates.TemplateResponse("home.html", {"request": request, "quotes": quotes, "user": user})


@router.get("/add-quote", response_class=HTMLResponse)
async def add_new_quote(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("add-quote.html", {"request": request, "user": user})


@router.post("/add-quote", response_class=HTMLResponse)
async def create_quote(request: Request,
                       movie: str = Form(...),
                       movie_character: str = Form(...),
                       quote: str = Form(...),
                       rating: int = Form(...),
                       db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    quote_model = models.Quotes()
    quote_model.movie = movie
    quote_model.movie_character = movie_character
    quote_model.quote = quote
    quote_model.rating = rating
    quote_model.complete = False
    quote_model.owner_id = user.get("id")

    db.add(quote_model)
    db.commit()

    return RedirectResponse(url="/quotes", status_code=status.HTTP_302_FOUND)


@router.get("/edit-quote/{quote_id}", response_class=HTMLResponse)
async def edit_quote(request: Request, quote_id: int, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    quote = db.query(models.Quotes).filter(models.Quotes.id == quote_id).first()

    return templates.TemplateResponse("edit-quote.html", {"request": request, "quote": quote, "user": user})


@router.post("/edit-quote/{quote_id}", response_class=HTMLResponse)
async def edit_quote_commit(request: Request,
                            quote_id: int,
                            movie: str = Form(...),
                            movie_character: str = Form(...),
                            quote: str = Form(...),
                            rating: int = Form(...),
                            db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    quote_model = db.query(models.Quotes).filter(models.Quotes.id == quote_id).first()

    quote_model.movie = movie
    quote_model.movie_character = movie_character
    quote_model.quote = quote
    quote_model.rating = rating

    db.add(quote_model)
    db.commit()

    return RedirectResponse(url="/quotes", status_code=status.HTTP_302_FOUND)


@router.get("/delete/{quote_id}")
async def delete_quote(request: Request, quote_id: int, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    quote_model = db.query(models.Quotes).filter(models.Quotes.id == quote_id)\
        .filter(models.Quotes.owner_id == user.get("id")).first()

    if quote_model is None:
        return RedirectResponse(url="/quotes", status_code=status.HTTP_302_FOUND)

    db.query(models.Quotes).filter(models.Quotes.id == quote_id).delete()

    db.commit()

    return RedirectResponse(url="/quotes", status_code=status.HTTP_302_FOUND)


@router.get("/complete/{quote_id}", response_class=HTMLResponse)
async def complete_quote(request: Request, quote_id: int, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    quote = db.query(models.Quotes).filter(models.Quotes.id == quote_id).first()

    quote.complete = not quote.complete

    db.add(quote)
    db.commit()

    return RedirectResponse(url="/quotes", status_code=status.HTTP_302_FOUND)
