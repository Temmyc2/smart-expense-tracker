
from flask import redirect, render_template, session
from functools import wraps
from datetime import datetime


# currency symbols
symbols = {"USD": "$", "EUR": "€", "JPY": "¥", "GBP": "£", "AUD": "A$", "CAD": "C$", "CHF": "₣", "CNY": "¥", "HKD": "HK$", "NZD": "NZ$", "NGN": "₦"}


# Route protection for users not logged in
def login_required(f):
    """Decorate routes to require login.If user not logged in, redirect to /login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Format currency to user's choice
def format_currency(value, currency):
    try:
        symbol = symbols[currency]
    except KeyError:
        symbol = currency
    return f"{symbol}{value:,.2f}"


def greet(time):
    greet = "Good"
    if 0 <= time <= 11:
        greet = "Good Morning"
    elif 12 <= time <= 16:
        greet = "Good Afternoon"
    else:
        greet = "Good Evening"
    return greet
