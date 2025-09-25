from fastapi import APIRouter, Request, Depends, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

router = APIRouter()

# Point templates to frontend folder
templates = Jinja2Templates(directory="frontend")

@router.get("/")
async def index_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@router.get("/about")
async def about_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@router.get("/contact")
async def contact_page(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

@router.get("/features")
async def dashboard_page(request: Request):
    return templates.TemplateResponse("features.html", {"request": request})

@router.get("/pricing")
async def dashboard_page(request: Request):
    return templates.TemplateResponse("pricing.html", {"request": request})

@router.get("/how-it-works")
async def dashboard_page(request: Request):
    return templates.TemplateResponse("how-it-works.html", {"request": request})
@router.get("/templates")
async def dashboard_page(request: Request):
    return templates.TemplateResponse("templates.html", {"request": request})
@router.get("/demo")
async def dashboard_page(request: Request):
    return templates.TemplateResponse("demo.html", {"request": request})
@router.get("/privacy")
async def dashboard_page(request: Request):
    return templates.TemplateResponse("privacy.html", {"request": request})
@router.get("/terms")
async def dashboard_page(request: Request):
    return templates.TemplateResponse("terms.html", {"request": request})
