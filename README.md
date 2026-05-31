# SMART EXPENSE TRACKER
#### Video Demo: https://www.youtube.com/watch?v=lg0Gq4JYjMs
#### Description:
> Smart Expense Tracker is a web application I built for my CS50x final project. The purpose of the application is to help users keep track of their income and expenses in one place.

> Users can create an account, log in, add income, add expenses, edit transactions, delete transactions, view transaction history, and see a dashboard that summarizes their finances. Users can also choose their preferred currency and switch between light mode and dark mode.

> I chose this project because it is something I can actually use in my everyday life. While building it, I wanted to practice many of the concepts I learned in CS50x such as Flask, SQLite, SQL, Python, HTML, CSS, JavaScript, sessions, and user authentication.

> This project is inspired by the Finance problem set, but instead of tracking stocks, it focuses on personal income and expense management.

##### app.py:

This is the main file of the project.

It contains all the Flask routes and most of the backend logic. Some of the routes include:

- Dashboard
* Register
+ Login
- Logout
* Add Expense
+ Add Income
- History
* Edit Transaction
+ Delete Transaction
- Settings
+ Details

This file is also responsible for querying the database and sending information to the templates.




##### helpers.py
This file contains helper functions used in different parts of the application.

The functions include:

- login_required
* format_currency
+ greet

I moved these functions into a separate file to avoid making app.py too large.



##### expense.db
This is the SQLite database used by the project.

The database contains two main tables.

###### users:
Stores information about users such as:

- id
+ username
* password hash
- preferred currency

###### transactions
Stores information about each transaction such as:

- id
* user_id
+ type
- amount
+ category
* description
- created_at

Each transaction belongs to a specific user.



##### Templates
The templates folder contains all HTML pages used by the application.

###### dashboard.html
Shows:
- Total income
+ Total expenses
* Net balance
- Recent transactions
+ Charts

###### register.html
Used for user registration.

###### login.html
Used for user login.

###### add_expense.html
Used for adding expenses.

###### add_income.html
Used for adding income.

I decided to separate income and expense into two different pages because I felt it would be easier for users and easier for me to build.

###### history.html
Displays all transactions and allows filtering.

###### edit.html
Allows users to edit a transaction.

###### settings.html
Allows users to change their currency and password.

###### details.html
shows the full details of a transaction

###### layout.html
Contains the header, navbar and footer information for all html pages



##### Static Files
>The static folder contains the CSS and JavaScript files.
>The CSS file is used for styling the application.
>The JavaScript file is used for:

- Dark mode
* Delete confirmation
+ Charts
- search function

>JavaScript was one of the hardest parts of this project because I had very little experience with it before starting.




##### Design Choices Debated
>One design choice I made was separating income and expense into different pages instead of using one form for both. This created some repeated code, but I felt it made the application easier to understand.

>Another choice was allowing users to select their preferred currency. This preference is stored in the database and used when displaying amounts throughout the application.

>I also added a greeting on the dashboard that changes depending on the time of day.



##### Challenges
>The biggest challenge for me was JavaScript. Most of my experience before this project was with Python and Flask, so adding interactive features took a lot of research and testing.

>Another challenge was creating the dashboard queries. I had to learn how to use SQL functions like SUM, GROUP BY, and COALESCE to calculate totals and generate chart data.

>I also spent a lot of time debugging because fixing one route sometimes affected another route.



##### Challenges
>The biggest challenge for me was JavaScript. Most of my experience before this project was with Python and Flask, so adding interactive features took a lot of research and testing.

>Another challenge was creating the dashboard queries. I had to learn how to use SQL functions like SUM, GROUP BY, and COALESCE to calculate totals and generate chart data.

>I also spent a lot of time debugging because fixing one route sometimes affected another route.



##### Future Improvements
> Some features I would like to add in the future are:

- Budgets
+ Savings goals
* Export to CSV
- Email support
+ Recurring transactions
* Mobile app version

> I would also like to continue improving the user interface and eventually use the application to manage my own personal expenses.
