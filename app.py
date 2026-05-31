import os

from cs50 import SQL
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv

from helpers import login_required, format_currency, greet

# Configure application
app = Flask(__name__)
load_dotenv()
app.secret_key = os.environ.get("SECRET_KEY")

# Custom filter
app.jinja_env.filters['format_currency'] = format_currency
app.jinja_env.filters['greet'] = greet

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///expense.db")


types = ["Income", "Expense"]

expense_categories = ["Food(groceries, Dining-out)", "Transportation(car payment, fuel, repairs, public transit)", "Housing(mortgage/rent, property taxes, maintenance)", "Entertainment & hobbies",
              "Utilities(electricity, water, internet, airtime)", "Insurance(Health, auto, home/renters, life)", "Education", "Family", "Health & Wellness(gym, medical, dental)", "Micsellaneous", "Debt payment", "Savings"]
income_categories = ["Salary", "Gift", "Freelance", "Business", "Investment"]

symbols = {"USD": "$", "EUR": "€", "JPY": "¥", "GBP": "£", "AUD": "A$", "CAD": "C$", "CHF": "₣", "CNY": "¥", "HKD": "HK$", "NZD": "NZ$", "NGN": "₦"}

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



@app.route("/")
@login_required
def dashboard():

    # query for user's currency and username
    currency_username = db.execute("SELECT currency, username FROM users WHERE id = ?", session["user_id"])
    user_currency = currency_username[0]["currency"]

    # Capitalize first letter of username
    username = currency_username[0]["username"]
    username = username.capitalize()

    # query for total income
    total_income = db.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM transactions WHERE type = ? AND user_id = ?", "Income", session["user_id"])

    # query for total expense
    total_expense = db.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM transactions WHERE type = ? AND user_id = ?", "Expense", session["user_id"])

    # calcuate remaining balance and format
    net_balance = total_income[0]["total"] - total_expense[0]["total"]

    # query for last 5 transactions
    recent_transactions = db.execute(
        "SELECT * FROM transactions WHERE user_id = ? ORDER BY created_at DESC LIMIT 5", session["user_id"])

    # query for spending by categories
    category_data = db.execute(
        "SELECT category, COALESCE(SUM(amount), 0) AS total FROM transactions WHERE user_id = ? AND type = 'Expense' GROUP BY category ORDER BY total DESC", session["user_id"])

    # query for monthly expense
    monthly_expense = db.execute(
        "SELECT strftime('%Y-%m', created_at) AS month, SUM(amount) AS total FROM transactions WHERE user_id = ? AND type ='Expense' GROUP BY month", session["user_id"])

    # query for monthly expense
    monthly_income = db.execute(
        "SELECT strftime('%Y-%m', created_at) AS month, SUM(amount) AS total FROM transactions WHERE user_id = ? AND type = 'Income' GROUP BY month", session["user_id"])

    # query for transaction count to know if any transaction have been made
    transaction_count = db.execute("SELECT COUNT(*) AS count FROM transactions WHERE user_id = ?", session["user_id"])

    # get the current hour of the day
    time = datetime.now().hour


    return render_template("dashboard.html",
                            total_income=total_income[0]["total"],
                            total_expense=total_expense[0]["total"],
                            net_balance=net_balance,
                            recent_transaction=recent_transactions,
                            monthly_expense=monthly_expense,
                            category_data=category_data,
                            monthly_income=monthly_income,
                            user_currency=user_currency,
                            time=time,
                            transaction_count=transaction_count,
                            username=username)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # user came via a form
    if request.method == "POST":

        # Grap user's input
        # confirm username was inputed
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirmation")
        if not username or not password or not confirm_password:
            flash("Error: Please fill out all fields to continue", "danger")
            return render_template("register.html")

        # make username case insensitive
        username = username.lower().strip()

        # Check if username doesn't exist before saving info to database
        user = db.execute("SELECT username FROM users WHERE username = ?", username)
        if user:
            flash("Username Already Exist", "danger")
            return render_template("register.html")

        # Check if the two need passwords matches
        if password != confirm_password:
            flash("Error: Password do not Match", "danger")
            return render_template("register.html")

        # Hash password and save all details if user pass all check
        hashed_password = generate_password_hash(password)

        db.execute("INSERT INTO users (username, hash) VALUES (?,?)", username, hashed_password)

        # save user's id to the session
        id = db.execute("SELECT id FROM users WHERE username = ?", username)
        session["user_id"] = id[0]["id"]

        # successful banner
        flash("Successful login")
        return redirect("/")
    else:
        # user came via URL
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure username  and password was submitted
        if not username or not password:
            flash("Error: Must provide username and password", "danger")
            return render_template("login.html")

        # make username not case sensitive
        username = username.lower().strip()

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], password
        ):
            flash("Error: invalid username and/or password", "danger")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash("Login Successful", "success")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:

        # check if any argument was passed to the url
        status = request.args.get("status")
        if status == "Password_changed":
            flash("Password changed successfully. Please login with new password", "success")
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    flash("Logged Out", "success")
    return redirect("/")


@app.route("/add_expense", methods=["POST", "GET"])
@login_required
def add_expense():
    """Add expense"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # grab user's input
        transaction_type = request.form.get("type")
        description = request.form.get("description")
        category = request.form.get("category")
        amount = request.form.get("amount")

        # validate transaction type
        if not transaction_type or transaction_type not in types:
            flash("Error: Invalid transaction Type", "danger")
            return render_template("add_expense.html", types=types, expense_categories=expense_categories)

        # validate the amount
        if not amount:
            flash("Error: Empty amount", "danger")
            return render_template("add_expense.html", types=types, expense_categories=expense_categories)
        amount = float(amount)
        if amount <= 0:
            flash("Error:Invalid amount", "danger")
            return render_template("add_expense.html", types=types, expense_categories=expense_categories)

        # check if user selected a category
        if not category:
            flash("Input a category", "danger")
            return render_template("add_expense.html", types=types, expense_categories=expense_categories)

        # validate the selected category
        if category not in expense_categories:
            flash("Invalid Category", "danger")
            return render_template("add_expense.html", types=types, expense_categories=expense_categories)

        # Save user's input to database if it passed all checks
        db.execute("INSERT INTO transactions (user_id, type, amount, category, description) VALUES (?, ?, ?, ?, ?)",
                   session["user_id"], transaction_type, amount, category, description)
        flash("Expense added successfully", "success")
        return redirect("/history")

    # render  add expense form page if a user came via URL
    return render_template("add_expense.html", types=types, expense_categories=expense_categories)


@app.route("/add_income", methods=["POST", "GET"])
@login_required
def add_income():
    """Add Income"""

     # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # grab all user's input
        transaction_type = request.form.get("type")
        description = request.form.get("description")
        category = request.form.get("category")
        amount = request.form.get("amount")

        # validate transaction type
        if not transaction_type or transaction_type not in types:
            flash("Error: Invalid transaction Type", "danger")
            return render_template("add_income.html", income_categories=income_categories)

        # validate the amount
        if not amount:
            flash("Error: Empty amount", "danger")
            return render_template("add_income.html", income_categories=income_categories)
        amount = float(amount)
        if amount <= 0:
            flash("Error:Invalid amount", "danger")
            return render_template("add_income.html", income_categories=income_categories)


        # check if user selected a category
        if not category:
            flash("Input a category", "danger")
            return render_template("add_income.html", income_categories=income_categories)

        # validate the selected category
        if category not in income_categories:
            flash("Invalid Category", "danger")
            return render_template("add_income.html", income_categories=income_categories)

        # Save user's input to database if it passed all checks
        db.execute("INSERT INTO transactions (user_id, type, amount, category, description) VALUES (?, ?, ?, ?, ?)",
                   session["user_id"], transaction_type, amount, category, description)
        flash("Income added successfully", "success")
        return redirect("/history")

    # render add income form page if a user came via URL
    return render_template("add_income.html", types=types, income_categories=income_categories)




@app.route("/history")
@login_required
def history():
    """Show transaction history"""

    # query for user's currency
    currency = db.execute("SELECT currency FROM users WHERE id = ?", session["user_id"])
    user_currency = currency[0]["currency"]

    # get user's filter input
    transaction_filter = request.args.get("filter")

    # validate user input a valid word
    if transaction_filter and transaction_filter != "":

        # query for all user's transaction using user's filter input and its ID
        all_transactions = db.execute("SELECT * FROM transactions WHERE type = ? AND user_id = ?", transaction_filter, session["user_id"])

        # return filter result to user
        return render_template("history.html", all_transactions=all_transactions, user_currency=user_currency)

    else:

        # query for all user's transaaction
        all_transactions = db.execute(
            "SELECT * FROM transactions WHERE user_id = ? ORDER BY created_at DESC", session["user_id"])

    # return all transaction to user
    return render_template("history.html", all_transactions=all_transactions, user_currency=user_currency)


@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    """Edit or Delete a transaction"""

    # Get the specific transaction user wants to edit
    transaction = db.execute(
        "SELECT * FROM transactions WHERE id = ? AND user_id = ?", id, session["user_id"])

    # Check if transaction exist
    if not transaction:
        flash("Error: transaction not found", "danger")
        return redirect("/history")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # grab all user's input
        transaction_type = request.form.get("type")
        description = request.form.get("description")
        category = request.form.get("category")
        amount = request.form.get("amount")

        # validate the amount
        # validate the amount
        if not amount:
            flash("Error: Empty amount", "danger")
            return render_template("edit.html", transaction=transaction[0], income_categories=income_categories, expense_categories=expense_categories)
        amount = float(amount)
        if amount <= 0:
            flash("Error:Invalid amount", "danger")
            return render_template("edit.html", transaction=transaction[0], income_categories=income_categories, expense_categories=expense_categories)

        # check if user selected a category
        if not category:
            flash("Error: Input a category", "danger")
            return render_template("edit.html", transaction=transaction[0], income_categories=income_categories, expense_categories=expense_categories)

        # validate transaction type
        if not transaction_type or transaction_type not in types:
            flash("Error: Invalid transaction Type", "danger")
            return render_template("edit.html", transaction=transaction[0], income_categories=income_categories, expense_categories=expense_categories)

        # check input category is valid and update
        if transaction[0]["type"] == "Expense":
            if category in expense_categories:

                # update edited information if in expense
                db.execute("UPDATE transactions SET amount = ?, category = ?, description = ?, type = ? WHERE id = ?",
                amount, category, description, transaction_type, id)
                flash("Transaction Updated!", "success")
                return redirect("/history")
            else:
                flash("Error: Invalid category", "danger")
                return render_template("edit.html", transaction=transaction[0], expense_categories=expense_categories, id=id)

        # update edited information if in income
        else:
            if category in income_categories:
                db.execute("UPDATE transactions SET amount = ?, category = ?, description = ? WHERE id = ?",
                        amount, category, request.form.get("description"), id)
                flash("Transaction Updated!", "success")
                return redirect("/history")
            else:
                flash("Error: Invalid category", "danger")
                return render_template("edit.html", transaction=transaction[0], income_categories=income_categories, id=id)

    return render_template("edit.html", transaction=transaction[0], income_categories=income_categories, expense_categories=expense_categories)


@app.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    """Delete a Transaction"""

    # Check if there's a transaction id and the transaction is for the user
    if id:
        db.execute("DELETE FROM transactions WHERE id = ? AND user_id = ?", id, session["user_id"])
        flash("Transaction deleted successfully", "success")

    # redirect user to history page so that they can see the changes
    return redirect("/history")


@app.route("/details/<int:id>")
@login_required
def details(id):
    """Display full details of a transaction"""

    # get all details of the transaction id passed by the URL
    transaction_details = db.execute("SELECT * FROM transactions WHERE id = ? AND user_id = ?", id, session["user_id"])

    # query for user's currency
    currency = db.execute("SELECT currency FROM users WHERE id = ?", session["user_id"])
    user_currency = currency[0]["currency"]
    return render_template("/details.html", transaction_details=transaction_details[0], user_currency=user_currency)

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """Edit user's settings"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # if user submits a new currency in settings page, update and remain on the page. But let user know using a flash banner
        user_currency = request.form.get("user_currency")
        if user_currency:
            db.execute("UPDATE users SET currency = ? WHERE id = ?", user_currency, session["user_id"])
            flash("Changes saved successfully", "success")
            return render_template("settings.html", symbols=symbols)

        # If program runs to this level, that means user didn't change currency

        # So grab all user's input and check for empty field
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        if not old_password:
            flash("Error: Must provide old password", "danger")
            return render_template("settings.html", symbols=symbols)
        if not new_password:
            flash("Error: Must provide new password", "danger")
            return render_template("settings.html", symbols=symbols)
        if confirm_password != new_password:
            flash("Error: Password does not match", "danger")
            return render_template("settings.html", symbols=symbols)

        # if all input went well

        # get previous hased password and check against old password user input
        user = db.execute(
            "SELECT hash FROM users WHERE id = ?", session["user_id"])

        # if not same, render error message
        if not check_password_hash(user[0]["hash"], old_password):
            flash("Error: wrong password", "danger")
            return render_template("settings.html", symbols=symbols)

        # if same, hash new password and save to database
        else:
            rehashed_password = generate_password_hash(new_password)
            db.execute("UPDATE users SET hash = ? WHERE id = ?", rehashed_password, session["user_id"])
            return redirect(url_for("login", status="Password_changed"))

    # render settings page if user got here via a link or URL
    return render_template("settings.html", symbols=symbols)




