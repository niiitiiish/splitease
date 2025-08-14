# =============================================================================
# IMPORTS AND CONFIGURATION
# =============================================================================
from fastapi import FastAPI, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models
from starlette.middleware.sessions import SessionMiddleware
import traceback
import os

# =============================================================================
# DATABASE SETUP
# =============================================================================
def setup_database():
    """Setup database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"⚠️  Database setup warning: {e}")

# =============================================================================
# FASTAPI APP CONFIGURATION
# =============================================================================
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup database on startup
@app.on_event("startup")
async def startup_event():
    setup_database()

# =============================================================================
# DATABASE UTILITY FUNCTIONS
# =============================================================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if user_id is None:
        return None
    return db.query(models.User).filter(models.User.id == user_id).first()

# =============================================================================
# LANDING PAGE ROUTES
# =============================================================================
@app.get("/", response_class=HTMLResponse)
def landing_page(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

# =============================================================================
# AUTHENTICATION ROUTES
# =============================================================================
@app.get("/register", response_class=HTMLResponse)
def show_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register", response_class=HTMLResponse)
async def register(request: Request, db: Session = Depends(get_db)):
    try:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        
        if not username or not password:
            msg = "Username and password are required."
            return templates.TemplateResponse("register.html", {"request": request, "msg": msg})
        
        existing_user = db.query(models.User).filter(models.User.username == username).first()
        if existing_user:
            msg = "Username already exists. Please choose another."
            return templates.TemplateResponse("register.html", {"request": request, "msg": msg})
        
        new_user = models.User(username=username, password=password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Check for invitations
        invitations = db.query(models.Invitation).filter(
            models.Invitation.email == username, 
            models.Invitation.accepted == False
        ).all()
        
        for invite in invitations:
            group = db.query(models.Group).filter(models.Group.id == invite.group_id).first()
            if group and new_user not in group.members:
                group.members.append(new_user)
                invite.accepted = True
        
        db.commit()
        msg = "Registration successful! You can now log in."
        return templates.TemplateResponse("register.html", {"request": request, "msg": msg})
    except Exception as e:
        db.rollback()
        msg = f"Registration failed: {str(e)}"
        return templates.TemplateResponse("register.html", {"request": request, "msg": msg})

@app.get("/login", response_class=HTMLResponse)
def show_login(request: Request, msg: str = None):
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})

@app.post("/login")
async def login(request: Request, db: Session = Depends(get_db), username: str = Form(...), password: str = Form(...)):
    try:
        user = db.query(models.User).filter(
            models.User.username == username, 
            models.User.password == password
        ).first()
        
        if user:
            request.session["user_id"] = user.id
            return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
        else:
            msg = "Invalid username or password"
            return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
    except Exception as e:
        msg = f"Database error: {str(e)}"
        return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
    
@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

# =============================================================================
# DASHBOARD ROUTES
# =============================================================================
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db), msg: str = None):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    try:
        # Get user's groups
        groups = user.groups if user.groups else []
        group_ids = [g.id for g in groups]
        
        # Attach latest expenses and settlements to each group
        for group in groups:
            group.expenses = db.query(models.Expense).filter(
                models.Expense.group_id == group.id
            ).order_by(models.Expense.id.desc()).limit(3).all()
            
            group.settlements = db.query(models.Settlement).filter(
                models.Settlement.group_id == group.id
            ).order_by(models.Settlement.timestamp.desc()).all()
        
        # Get user's recent expenses
        expenses = []
        if group_ids:
            expenses = db.query(models.Expense).filter(
                models.Expense.paid_by == user.id, 
                models.Expense.group_id.in_(group_ids)
            ).order_by(models.Expense.id.desc()).limit(10).all()
        
        # Get pending invitations
        invitations = db.query(models.Invitation).filter(
            models.Invitation.email == user.username, 
            models.Invitation.accepted == False
        ).all()
        
        # Calculate balances and settlements
        total_owed = 0.0
        total_lent = 0.0
        group_balances = {}
        
        for group in groups:
            members = group.members if group.members else []
            member_count = len(members)
            group_expenses = db.query(models.Expense).filter(
                models.Expense.group_id == group.id
            ).all()
            group_settlements = db.query(models.Settlement).filter(
                models.Settlement.group_id == group.id
            ).all()
            
            # Calculate per-member balances
            balances = {member.username: 0.0 for member in members}
            
            if member_count == 0:
                group_balances[group.id] = balances
                group.owes = []
                continue  # Skip division for empty groups
            
            # Calculate expense shares
            for expense in group_expenses:
                share = expense.amount / member_count
                for member in members:
                    if member.id == expense.paid_by:
                        balances[member.username] += expense.amount - share
                    else:
                        balances[member.username] -= share
            
            # Subtract settlements
            for settlement in group_settlements:
                payer = db.query(models.User).filter(models.User.id == settlement.payer_id).first()
                receiver = db.query(models.User).filter(models.User.id == settlement.receiver_id).first()
                if payer and receiver:
                    balances[payer.username] += settlement.amount
                    balances[receiver.username] -= settlement.amount
            
            group_balances[group.id] = balances
            
            # Calculate who owes whom
            owes = []
            temp_balances = balances.copy()
            debtors = [m for m in members if temp_balances[m.username] < 0]
            creditors = [m for m in members if temp_balances[m.username] > 0]
            
            for debtor in debtors:
                amount_to_pay = -temp_balances[debtor.username]
                for creditor in creditors:
                    if amount_to_pay == 0:
                        break
                    creditor_amount = temp_balances[creditor.username]
                    pay_amount = min(amount_to_pay, creditor_amount)
                    if pay_amount > 0:
                        owes.append({
                            "debtor": debtor,
                            "creditor": creditor,
                            "amount": round(pay_amount, 2)
                        })
                        temp_balances[creditor.username] -= pay_amount
                        amount_to_pay -= pay_amount
            
            group.owes = owes
            
            # Update total_owed and total_lent for the current user
            if user.username in balances:
                if balances[user.username] < 0:
                    total_owed += -balances[user.username]
                elif balances[user.username] > 0:
                    total_lent += balances[user.username]

        all_users = db.query(models.User).all()
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "username": user.username,
            "total_owed": round(total_owed, 2),
            "total_lent": round(total_lent, 2),
            "groups": groups,
            "expenses": expenses,
            "invitations": invitations,
            "all_users": all_users,
            "group_balances": group_balances,
            "msg": msg
        })
        
    except Exception as e:
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "username": user.username if user else "",
            "total_owed": 0.0,
            "total_lent": 0.0,
            "groups": [],
            "expenses": [],
            "invitations": [],
            "all_users": [],
            "group_balances": {},
            "msg": f"Internal error: {str(e)}"
        })

# =============================================================================
# GROUP MANAGEMENT ROUTES
# =============================================================================
@app.post("/dashboard/add-group")
async def add_group_dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    try:
        form = await request.form()
        group_name = form.get("group_name")
        
        if group_name:
            new_group = models.Group(name=group_name)
            new_group.members.append(user)
            db.add(new_group)
            db.commit()
    except Exception as e:
        db.rollback()
    
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

@app.post("/dashboard/delete-group")
async def delete_group_dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    try:
        form = await request.form()
        group_id = int(form.get("group_id"))
        group = db.query(models.Group).filter(models.Group.id == group_id).first()
        
        if group and user in group.members:
            # Delete related settlements first
            db.query(models.Settlement).filter(models.Settlement.group_id == group.id).delete()
            db.commit()
            db.delete(group)
            db.commit()
    except Exception as e:
        db.rollback()
    
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

# =============================================================================
# EXPENSE MANAGEMENT ROUTES
# =============================================================================
@app.post("/dashboard/add-expense")
async def add_expense_dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    try:
        form = await request.form()
        description = form.get("description")
        amount = form.get("amount")
        group_id = form.get("group_id")
        
        # Validate input
        if not description or not amount or not group_id:
            msg = "All fields, including reason for expense, are required."
            return await dashboard(request, db, msg=msg)
        
        amount = float(amount)
        group_id = int(group_id)
        
        new_expense = models.Expense(
            description=description,
            amount=amount,
            paid_by=user.id,
            group_id=group_id
        )
        db.add(new_expense)
        db.commit()
        msg = "Expense added successfully!"
        
    except ValueError:
        msg = "Invalid amount or group ID format."
        return await dashboard(request, db, msg=msg)
    except Exception as e:
        db.rollback()
        msg = f"Error adding expense: {str(e)}"
        return await dashboard(request, db, msg=msg)
    
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

# =============================================================================
# USER INVITATION ROUTES
# =============================================================================
@app.post("/dashboard/invite-user")
async def invite_user_dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    try:
        form = await request.form()
        group_id = int(form.get("group_id"))
        username = form.get("username")
        
        group = db.query(models.Group).filter(models.Group.id == group_id).first()
        invited_user = db.query(models.User).filter(models.User.username == username).first()
        
        if group:
            if invited_user:
                if invited_user not in group.members:
                    group.members.append(invited_user)
                    db.commit()
            
            existing_invite = db.query(models.Invitation).filter(
                models.Invitation.group_id == group_id, 
                models.Invitation.email == username, 
                models.Invitation.accepted == False
            ).first()
            
            if not existing_invite:
                new_invite = models.Invitation(group_id=group_id, email=username, accepted=False)
                db.add(new_invite)
                db.commit()
    except Exception as e:
        db.rollback()
    
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

@app.post("/dashboard/accept-invite")
async def accept_invite_dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    try:
        form = await request.form()
        invite_id = int(form.get("invite_id"))
        invite = db.query(models.Invitation).filter(
            models.Invitation.id == invite_id, 
            models.Invitation.email == user.username, 
            models.Invitation.accepted == False
        ).first()
        
        if invite:
            group = db.query(models.Group).filter(models.Group.id == invite.group_id).first()
            if group and user not in group.members:
                group.members.append(user)
            invite.accepted = True
            db.commit()
    except Exception as e:
        db.rollback()
    
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

# =============================================================================
# SETTLEMENT ROUTES
# =============================================================================
@app.post("/dashboard/settle-up")
async def settle_up(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    try:
        form = await request.form()
        group_id = int(form.get("group_id"))
        receiver_id = int(form.get("receiver_id"))
        amount = float(form.get("amount"))
        
        settlement = models.Settlement(
            group_id=group_id,
            payer_id=user.id,
            receiver_id=receiver_id,
            amount=amount
        )
        db.add(settlement)
        db.commit()
    except Exception as e:
        db.rollback()
    
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

# =============================================================================
# USER PROFILE ROUTES
# =============================================================================
@app.post("/update-upi")
async def update_upi(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    try:
        form = await request.form()
        upi_id = form.get("upi_id")
        if upi_id:
            user.upi_id = upi_id
            db.commit()
    except Exception as e:
        db.rollback()
    
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

# =============================================================================
# ERROR HANDLING
# =============================================================================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("Unhandled error:", exc)
    traceback.print_exc()
    return PlainTextResponse(str(exc), status_code=500)

# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
