import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///bank.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Index"""
    rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    username = rows[0]["username"]
    cash = rows[0]["cash"]
    return render_template("index.html", username=username, cash=cash)        


@app.route("/gotoindex", methods=["GET", "POST"])
@login_required
def gotoindex():
    """Show Home"""
    
    if request.method == "GET":
        rows = db.execute("SELECT * FROM users")
        if rows[0]["user_pin"] == 0:
            return redirect("/create_pin")
        
        return render_template("users_index.html")
    
    elif request.method == "POST":
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        if not check_password_hash(rows[0]["user_pin"], request.form.get("pin")):
            return apology("Wrong PIN", 400)
    
        return redirect("/")
    
    else:
        return apology("TODO", 400)


@app.route("/create_pin", methods=["GET", "POST"])
def create_pin():
    """Create PIN for new users"""
    
    if request.method == "GET":
        return render_template("new_users_index.html")
    
    else:
        # Check if PIN and confirm PIN are provided
        if not request.form.get("pin") or not request.form.get("confirm_pin"): 
            return apology("Create new PIN", 400)
        
        # Validate PIN length
        pin = request.form.get("pin")
        if len(pin) != 6:
            return apology("Invalid PIN, must be 6 characters", 400)
        
        # Check if the PIN is numeric
        if not pin.isnumeric():
            return apology("Must be numeric", 400)
        
        # Check if PINs match
        if pin != request.form.get("confirm_pin"):
            return apology("Unmatched", 400)
        
        print(session["user_id"])
        try:
            # Hash the PIN as a string
            hash = generate_password_hash(pin)
            db.execute("UPDATE users SET user_pin = ? WHERE id = ?", hash, session["user_id"])
       
        except Exception as e:
            return apology(f"Database error: {e}", 500)
       
        return redirect("/login")
            

@app.route("/login", methods=["GET", "POST"])
def login():
    """User Login"""
    # Forget any user_id
    session.clear()
    
    if request.method == "GET":
        rows = db.execute("SELECT * FROM moderators")
        user_rows = db.execute("SELECT * FROM users")
        if len(rows) == 0:
            return render_template("newMod.html") 
        
        if len(user_rows) == 0:
            return render_template("register.html")
        
        return render_template("login.html")
    
    else:
        if not request.form.get("username"):
            return apology("Invalid Username", 400)
    
        if not request.form.get("password"):
            return apology("Invalid Password")
    
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("Account doesn't exist", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        print(session["user_id"])

        # Redirect user to home page
        return redirect("/")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
            

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    
    if request.method == "GET":
        rows = db.execute("SELECT * FROM moderators")

        if len(rows) == 0:
            return render_template("newMod.html") 
        
        return render_template("register.html")
    
    else:
        # Get username and password from the form
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirm_password")

        # Validate username
        if not username:
            return apology("Username is required", 400)
        
        elif len(username) < 6:
            return apology("Username must be at least 6 characters long", 400)

        # Validate password
        if not password:
            return apology("Password is required", 400)
        
        elif len(password) < 8:
            return apology("Password must be at least 8 characters long", 400)

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) > 0:
            return apology("Username already exist", 400)

        if password != confirmation:
            return apology("Invalid Password", 200)
        
        hash = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
        
        return redirect("/login")
    

@app.route("/moderator", methods=["GET", "POST"])
def moderator():
    """Log in Moderator"""

    session.clear()

    if request.method == "GET":
        rows = db.execute("SELECT * FROM moderators")

        if len(rows) == 0:
            return redirect("/newMod")

        return render_template("moderator.html")

    else:
        if not request.form.get("username"):
            return apology("Invalid Username", 400)
    
        if not request.form.get("password"):
            return apology("Invalid Password", 400)
    
        # Query database for username
        rows = db.execute("SELECT * FROM moderators WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")
        

@app.route("/newMod", methods=["GET", "POST"])
def newMod():
    """Create Moderator Account"""
    
    if request.method == "GET":
        return render_template("newMod.html")
    
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        if not username:
            return apology("Invalid Username", 400)
        
        elif len(username) < 6:
            return apology("Invalid Username", 400)

        if not password and not confirm_password:
            return apology("Invalid Password", 400)
        
        elif len(password) < 8:
            return apology("Invalid Password", 400)

        rows = db.execute("SELECT * FROM moderators WHERE username = ?", username)
        
        if len(rows) > 0:
            return apology("Username already exist", 400)

        if password != confirm_password:
            return apology("Passwords do not match", 400)
                
        hash = generate_password_hash(password)
        db.execute("INSERT INTO moderators (username, hash) VALUES (?, ?)", username, hash)
        
        return redirect("/moderator")
    
    
@app.route("/deposit", methods=["GET", "POST"])
def deposit():
    """User deposit"""
    
    if request.method == "GET":
        return render_template("deposit.html")
    
    else:
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        user_cash = rows[0]["cash"]
        amount = float(request.form.get("depositAmount"))
        
        if amount < 500:
            return apology("Minimum of $500", 400)
        
        if amount > user_cash or amount > 999999999:
            return apology("Not enough cash", 400)
    
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", amount, session["user_id"])
        db.execute("INSERT INTO transactions (account_id, transaction_type, amount, from_or_to) VALUES (?, ?, ?, ?)", session["user_id"], "Deposited", amount, rows[0]["username"])
        
        return redirect("/deposit")
    

@app.route("/withdraw", methods=["GET", "POST"])
def withdraw():
    """User Withdraw"""
    
    if request.method == "GET":
        return render_template("withdraw.html")
    
    else:
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        user_cash = rows[0]["cash"]
        amount = float(request.form.get("withdrawAmount"))
        
        expected_user_cash = user_cash - amount
        
        if expected_user_cash < 100:
            return apology("Invalid amount", 400)
        
        if amount > user_cash:
            return apology("Not enough cash", 400)
    
        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", amount, session["user_id"])
        db.execute("INSERT INTO transactions (account_id, transaction_type, amount, from_or_to) VALUES (?, ?, ?, ?)", session["user_id"], "Withdrawn", amount, rows[0]["username"])
        
        return redirect("/withdraw")


@app.route("/transfer", methods=["GET", "POST"])
def transfer():
    """User Transfer"""
    
    if request.method == "GET":
        return render_template("transfer.html")

    else:
        recipient_name = request.form.get("recipient")
        
        rows = db.execute("SELECT * FROM users WHERE username = ?", recipient_name)
        if len(rows) > 0:
            amount = float(request.form.get("transferAmount"))
            
            # USER 
            user_row = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
            user_cash = user_row[0]["cash"]
            username = user_row[0]["username"]
            
            # if user cash is < 100
            expected_users_cash = user_cash - amount
            
            if expected_users_cash < 100:
                return apology("Invalid amount", 400)
            
            # if user amount is > 999999999 or < 500
            if amount > 999999999 or amount < 500:
                return apology("Invalid amount", 400)
            
            
            # RECIPIENT 
            recipient_cash = rows[0]["cash"]
            expected_recipients_cash = recipient_cash + amount
            
            if expected_recipients_cash > 999999999:
                return apology(f"Invalid Amount, send lower than {amount}", 400)
                        
            # Update users's money            
            db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", amount, session["user_id"])
            db.execute("INSERT INTO transactions (account_id, transaction_type, amount, from_or_to) VALUES (?, ?, ?, ?)", session["user_id"], "Transferred", amount, recipient_name)
            
            # Update recipient's cash
            recipient_id = rows[0]["id"]
            db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", amount, recipient_id)
            db.execute("INSERT INTO transactions (account_id, transaction_type, amount, from_or_to) VALUES (?, ?, ?, ?)", recipient_id, "Received", amount, username)
            
            return redirect("/transfer")
        return apology("Error Code", 404)

@app.route("/history")
def history():
    """Transaction History"""
    history = db.execute("SELECT * FROM transactions WHERE account_id = ?", session["user_id"])

    return render_template("history.html", transactions=history)
    

@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change Password"""
    
    if request.method == "GET":
        return render_template("change_password.html")
    else:
        rows = db.execute("SELECT hash FROM users WHERE id = ?", session["user_id"])
        user_pass = rows[0]['hash']

        current_pass = request.form.get("current_password")
        new_pass = request.form.get("new_password")
        confirm_pass = request.form.get("confirm_password")

        if not current_pass:
            flash("Enter Password!")
            return redirect(url_for('change_password'))

        if not new_pass:
            flash("Enter New Password!")
            return redirect(url_for('change_password'))
        
        if new_pass != confirm_pass:
            flash("Password unmatched!")
            return redirect(url_for('change_password'))

        if check_password_hash(user_pass, current_pass):
            new_user_pass = generate_password_hash(new_pass)
            db.execute("UPDATE users SET hash = ? WHERE id = ?", new_user_pass, session["user_id"])

            flash("Password Changed!")
            return redirect(url_for('change_password'))

        flash("Incorrect Password!")
        return redirect(url_for('change_password'))
    

if __name__ == '__main__':
    app.run(debug=True)
