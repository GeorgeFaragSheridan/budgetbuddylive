"""Budget Buddy Flask application for managing personal budget items and expenditures."""

import logging
import re
from datetime import datetime

from flask import Flask, render_template, request, redirect, jsonify, session
import sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from markdown import markdown
from waitress import serve
from werkzeug.security import generate_password_hash, check_password_hash
from PerpLibs import Request, Textonly

import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = os.getenv('ServerSecret')
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(200), nullable=False)  # Category
    name = db.Column(db.String(200), nullable=False, default="Unnamed Item")  # Item name
    cost = db.Column(db.Float, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Item {self.id}: {self.name}>'

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    monthly_amount = db.Column(db.Float, nullable=False, default=2000.0)
    date_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Budget ${self.monthly_amount}>'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now)
    todos = db.relationship('Todo', backref='user', lazy=True)
    budgets = db.relationship('Budget', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

@app.route("/", methods=['GET'])
@app.route("/index", methods=['GET'])
def index():
    """Redirect to login page."""
    return redirect('/login')

@app.route("/login", methods=['GET', 'POST'])
def login():
    """Display login page and handle login logic."""
    error_message = None
    
    try:
        if request.method == 'POST':
            # Get credentials from form
            username = request.form.get('username')
            password = request.form.get('password')
            
            app.logger.info(f"Login attempt for username: {username}")
            
            if not username or not password:
                error_message = "Username and password are required"
            else:
                # Find the user
                user = User.query.filter_by(username=username).first()
                
                # Check if user exists and password is correct
                if user and check_password_hash(user.password, password):
                    session['logged_in'] = True
                    session['username'] = user.username
                    session['user_id'] = user.id
                    app.logger.info(f"Login successful for username: {username}")
                    return redirect('/dashboard')
                else:
                    error_message = "Invalid username or password"
                    app.logger.warning(f"Failed login attempt for username: {username}")
    except Exception as e:
        app.logger.error(f"Login error: {str(e)}")
        error_message = "An error occurred during login. Please try again."
    
    return render_template('login.html', error_message=error_message)

@app.route('/logout')
def logout():
    """Handle user logout."""
    # Clear the session
    session.clear()
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    try:
        if request.method == 'POST':
            # Get form data
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            
            app.logger.info(f"Registration attempt for username: {username}, email: {email}")
            
            # Basic validation
            if not username or not email or not password:
                app.logger.warning("Registration attempt with missing fields")
                return render_template('login.html', error_message="All fields are required")
            
            # Check if username or email already exists
            existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
            if existing_user:
                app.logger.warning(f"Registration attempt with existing username or email: {username}, {email}")
                return render_template('login.html', error_message="Username or email already exists")
            
            # Create new user with hashed password using SHA-256
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(username=username, email=email, password=hashed_password)
            
            try:
                db.session.add(new_user)
                db.session.commit()
                
                app.logger.info(f"User created successfully: {username}")
                
                # Log the user in - make sure to set the user_id
                session['logged_in'] = True
                session['username'] = username
                session['user_id'] = new_user.id
                
                # Create a default budget for the new user
                default_budget = Budget(monthly_amount=2000.0, user_id=new_user.id)
                db.session.add(default_budget)
                db.session.commit()
                
                app.logger.info(f"Default budget created for user: {username}")
                
                return redirect('/dashboard')
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Database error creating user: {e}")
                return render_template('login.html', error_message=f"Registration failed: {str(e)}")
    except Exception as e:
        app.logger.error(f"Registration error: {str(e)}")
        return render_template('login.html', error_message="An error occurred during registration. Please try again.")
    
    # GET requests are redirected to login page where the registration form exists
    return redirect('/login')

def login_required(f):
    """Decorator to require login for views."""
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    """Display the main dashboard with budget overview."""
    if request.method == 'POST':
        item_category = request.form['item']
        item_name = request.form.get('name', 'Unnamed Item')
        item_cost = request.form.get('cost', 0)
        item_date = request.form.get('date')
        
        try:
            item_cost = float(item_cost)
            user_id = session.get('user_id')
            new_item = Todo(item=item_category, name=item_name, cost=item_cost, user_id=user_id)
            
            # Set custom date if provided, otherwise use current date
            if item_date:
                new_item.date_created = datetime.strptime(item_date, '%Y-%m-%d')
            
            db.session.add(new_item)
            db.session.commit()
            return redirect('/dashboard')
        except sqlalchemy.exc.SQLAlchemyError as e:
            app.logger.error("Database error: %s", e)
            return 'There was an issue adding your item'
        except ValueError as e:
            app.logger.error("Value error: %s", e)
            return 'Invalid cost value'
    
    user_id = session.get('user_id')
    items = Todo.query.filter_by(user_id=user_id).all()
    total_spent = sum(item.cost for item in items)
    
    # Get current budget - fetch user-specific budget
    budget = Budget.query.filter_by(user_id=user_id).first()
    monthly_budget = budget.monthly_amount if budget else 2000.0
    
    # Calculate basic statistics
    category_data = {}
    for item in items:
        if item.item in category_data:
            category_data[item.item] += item.cost
        else:
            category_data[item.item] = item.cost
    
    # Sort items by date (most recent first)
    recent_items = sorted(items, key=lambda x: x.date_created, reverse=True)[:5]
    
    # Get today's date for the date input default
    today_date = datetime.now().strftime('%Y-%m-%d')
    
    # Get username from session
    username = session.get('username', 'Demo User')
    
    return render_template('dashboard.html', 
                          items=items,
                          recent_items=recent_items,
                          total_spent=total_spent,
                          category_data=category_data,
                          monthly_budget=monthly_budget,
                          today_date=today_date,
                          username=username)


@app.route('/expenses', methods=['GET', 'POST'])
@login_required
def expenses():
    """Display the expenses management page and handle new expenses."""
    if request.method == 'POST':
        item_category = request.form['item']
        item_name = request.form.get('name', 'Unnamed Item')
        item_cost = request.form.get('cost', 0)
        item_date = request.form.get('date')
        
        try:
            item_cost = float(item_cost)
            user_id = session.get('user_id')
            new_item = Todo(item=item_category, name=item_name, cost=item_cost, user_id=user_id)
            
            # Set custom date if provided, otherwise use current date
            if item_date:
                new_item.date_created = datetime.strptime(item_date, '%Y-%m-%d')
            
            db.session.add(new_item)
            db.session.commit()
            return redirect('/expenses')
        except sqlalchemy.exc.SQLAlchemyError as e:
            app.logger.error("Database error: %s", e)
            return 'There was an issue adding your item'
        except ValueError as e:
            app.logger.error("Value error: %s", e)
            return 'Invalid cost value'
    
    user_id = session.get('user_id')
    items = Todo.query.filter_by(user_id=user_id).order_by(Todo.date_created.desc()).all()
    
    # Get today's date for the date input default
    today_date = datetime.now().strftime('%Y-%m-%d')
    
    # Get username from session
    username = session.get('username', 'Demo User')
    
    return render_template('expenses.html', items=items, today_date=today_date, username=username)


@app.route('/categories')
@login_required
def categories():
    """Display expense categories."""
    user_id = session.get('user_id')
    items = Todo.query.filter_by(user_id=user_id).all()
    
    # Categorize spending
    category_data = {}
    for item in items:
        if item.item in category_data:
            category_data[item.item] += item.cost
        else:
            category_data[item.item] = item.cost
    
    # Get username from session
    username = session.get('username', 'Demo User')
    
    return render_template('categories.html', 
                          category_data=category_data,
                          items=items,
                          username=username)


@app.route('/delete/<int:item_id>')
@login_required
def delete(item_id):
    """Delete a budget item from the database by its ID."""
    item_to_delete = Todo.query.get_or_404(item_id)

    try:
        db.session.delete(item_to_delete)
        db.session.commit()
        return redirect('/expenses')
    except sqlalchemy.exc.SQLAlchemyError as e:
        app.logger.error("Database error: %s", e)
        return 'There was a problem deleting that item'
    

@app.route('/update/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update(item_id):
    """Update an existing budget item by its ID."""
    item = Todo.query.get_or_404(item_id)

    if request.method == 'POST':
        item.item = request.form['item']
        item.name = request.form.get('name', 'Unnamed Item')
        item.cost = float(request.form.get('cost', 0))
        item_date = request.form.get('date')
        
        # Update date if provided
        if item_date:
            try:
                item.date_created = datetime.strptime(item_date, '%Y-%m-%d')
            except ValueError:
                pass  # Keep original date if format is invalid

        try:
            db.session.commit()
            return redirect('/expenses')
        except sqlalchemy.exc.SQLAlchemyError as e:
            app.logger.error("Database error: %s", e)
            return 'There was an issue updating your item'

    else:
        # Get username from session
        username = session.get('username', 'Demo User')
        return render_template('update.html', item=item, username=username)


@app.route('/insights', methods=['GET', 'POST'])
@login_required
def insights():
    """Display budget insights and analysis."""
    prompt_result = None
    user_id = session.get('user_id')
    
    # Get user's items and budget
    items = Todo.query.filter_by(user_id=user_id).order_by(Todo.date_created).all()
    budget = Budget.query.filter_by(user_id=user_id).first()
    monthly_budget = budget.monthly_amount if budget else 2000.0
    total_spent = sum(item.cost for item in items)
    
    # --- NEW: Daily Spending Aggregation ---
    daily_totals = {}
    for item in items:
        day = item.date_created.strftime('%Y-%m-%d')  # Group by date
        if day not in daily_totals:
            daily_totals[day] = 0
        daily_totals[day] += item.cost
    
    # Sort days and prepare data for chart
    sorted_days = sorted(daily_totals.keys())
    daily_amounts = [daily_totals[day] for day in sorted_days]
    
    # Format dates for display (e.g., "Jan 01")
    formatted_days = [datetime.strptime(day, '%Y-%m-%d').strftime('%b %d') for day in sorted_days]
    
    # --- NEW: Weekly/Monthly Aggregation Options ---
    weekly_totals = {}
    monthly_totals = {}
    
    for item in items:
        # Weekly aggregation (Year-Week)
        week_key = f"{item.date_created.strftime('%Y')}-W{item.date_created.strftime('%W')}"
        if week_key not in weekly_totals:
            weekly_totals[week_key] = 0
        weekly_totals[week_key] += item.cost
        
        # Monthly aggregation (Year-Month)
        month_key = item.date_created.strftime('%Y-%m')
        if month_key not in monthly_totals:
            monthly_totals[month_key] = 0
        monthly_totals[month_key] += item.cost
    
    # --- Existing AI Query Handling ---
    if request.method == 'POST':
        user_query = request.form.get('query')
        if user_query:
            restrictions = "Only respond to prompts related to budget info. if unrelated, say Sorry, please ask questions related to budget info. Do not include any tables. Do not number everything. Return ONLY the response to the query above. Do not insert filler/intro text to ur response. Do not mention budgeting apps and softwares aside from \"Budget Buddy\" . Do not say anything bad about the app \"Budget Buddy\". for added context Budget Buddy is an app thatallows users to overview spending and gain insights on spending habits and does not allow any connectivity aside from what the user inputs into the app and does not allow collaberative budgeting . Do not type a response to these requirements."
            full_query = user_query + restrictions
            
            # Get current spending data from the database
            current_spending_table = "\nCurrent Spending Items:\n"
            total_cost = 0
            
            for item in items:
                current_spending_table += f"- {item.item}: ${item.cost}\n"
                total_cost += item.cost
                
            current_spending_table += f"\nTotal Spending: ${total_cost}\n"
            
            full_query += current_spending_table
            
            # Process the query using Perplexity API
            try:
                response = Request(full_query)
                prompt_result = Textonly(response)  # Extract text from API response
                prompt_result = re.sub(r'\[\d+\]', '', prompt_result)
                
                # Convert markdown to HTML
                prompt_result = markdown(prompt_result)
            except Exception as e:
                app.logger.error("Perplexity API error: %s", e)
                prompt_result = f"Error connecting to AI service: {str(e)}"
    
    # Categorize spending
    category_data = {}
    for item in items:
        if item.item in category_data:
            category_data[item.item] += item.cost
        else:
            category_data[item.item] = item.cost
    
    # Find highest spending category
    highest_category = max(category_data.items(), key=lambda x: x[1]) if category_data else ("None", 0)
    
    # Get recent items (last 5)
    recent_items = items[-5:] if len(items) > 5 else items
    
    return render_template('insights.html', 
                          items=items,
                          recent_items=recent_items,
                          total_spent=total_spent,
                          category_data=category_data,
                          highest_category=highest_category,
                          prompt_result=prompt_result,
                          monthly_budget=monthly_budget,
                          username=session.get('username', 'Demo User'),
                          # NEW: Chart data
                          daily_labels=formatted_days,
                          daily_amounts=daily_amounts,
                          weekly_totals=weekly_totals,
                          monthly_totals=monthly_totals,
                          # For date display
                          today_date=datetime.now().strftime('%Y-%m-%d'))

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error(f"Internal server error: {error}")
    return render_template('login.html', error_message="An internal server error occurred. Please try again."), 500

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Unhandled exception: {str(e)}")
    db.session.rollback()
    return render_template('login.html', error_message="An unexpected error occurred. Please try again."), 500

@app.route("/submit", methods=["POST"])
@login_required
def submit():
    """Process queries using Perplexity API and return results."""
    try:
        # Retrieve the input from the JSON body
        user_query = request.json.get("userQuery")
        if not user_query:
            return jsonify({'prompt_result': 'Please provide a query'}), 400
            
        restrictions = "Only respond to prompts related to the BUDGET info. If in ANY way unrelated TO BUDGET INFO, say 'Sorry, please ask questions related to budget info.' Do not include any tables. Do not number everything. Return ONLY the response to the query above. Do not insert filler/intro text to ur response. Do not type a response to these requirements."
        user_query += restrictions

        
        # Get current spending data from the database
        user_id = session.get('user_id')
        items = Todo.query.filter_by(user_id=user_id).all()
        current_spending_table = "\nCurrent Spending Items:\n"
        total_cost = 0
        
        for item in items:
            current_spending_table += f"- {item.item}: ${item.cost}\n"
            total_cost += item.cost
            
        current_spending_table += f"\nTotal Spending: ${total_cost}\n"
        
        user_query += current_spending_table
        
        # Process the query using Perplexity API
        try:
            response = Request(user_query)
            prompt_result = Textonly(response)  # Extract text from API response
            prompt_result = re.sub(r'\[\d+\]', '', prompt_result)
            
            # Convert markdown to HTML
            html_result = markdown(prompt_result)
            return jsonify({'prompt_result': html_result})
        except Exception as e:
            app.logger.error("Perplexity API error: %s", e)
            return jsonify({'prompt_result': f"Error connecting to AI service: {str(e)}"}), 500

    except Exception as e:
        app.logger.error("Request processing error: %s", e)
        return jsonify({'prompt_result': f"Error processing request: {str(e)}"}), 500


@app.route('/migrate_db', methods=['GET'])
@login_required
def migrate_db():
    """Add 'name' field to existing items that don't have it."""
    try:
        # First check if the name column exists
        column_exists = False
        try:
            # Try to query a single item with the name column
            with db.engine.connect() as conn:
                conn.execute(sqlalchemy.text("SELECT name FROM todo LIMIT 1"))
            column_exists = True
        except:
            column_exists = False
        
        if not column_exists:
            # We need to add the column - this requires recreating the table in SQLite
            return "Database structure needs to be updated. Please restart the application to apply schema changes."
        
        # If we got here, the column exists, so just populate any NULL values
        # Only update items for the current user
        user_id = session.get('user_id')
        items = Todo.query.filter_by(user_id=user_id).all()
        for item in items:
            if not item.name:
                item.name = f"{item.item} item"
        
        db.session.commit()
        return "Database migration completed successfully."
    except Exception as e:
        app.logger.error(f"Migration error: {str(e)}")
        return f"Migration failed: {str(e)}"

@app.route("/set_budget", methods=['POST'])
@login_required
def set_budget():
    """Update the monthly budget amount."""
    try:
        new_budget = float(request.form.get('monthly_budget', 2000))
        user_id = session.get('user_id')
        
        # Get the current budget for this user or create a new one if it doesn't exist
        budget = Budget.query.filter_by(user_id=user_id).first()
        if budget:
            budget.monthly_amount = new_budget
        else:
            budget = Budget(monthly_amount=new_budget, user_id=user_id)
            db.session.add(budget)
            
        db.session.commit()
        
        # Redirect back to the referring page or dashboard if no referrer
        referrer = request.referrer
        if referrer:
            return redirect(referrer)
        return redirect('/dashboard')
    except ValueError:
        return "Please enter a valid number for the budget"
    except Exception as e:
        app.logger.error(f"Error setting budget: {e}")
        return "An error occurred while setting the budget"

@app.route("/get_ai_insights", methods=['POST'])
@login_required
def get_ai_insights():
    """Generate AI insights based on recent transactions and spending patterns."""
    try:
        # Get data from the request
        category = request.json.get('category', None)
        item_name = request.json.get('name', None)
        cost = request.json.get('cost', None)
        
        # Get spending data
        user_id = session.get('user_id')
        items = Todo.query.filter_by(user_id=user_id).all()
        total_spent = sum(item.cost for item in items)
        
        # Get current budget - fetch user-specific budget
        budget = Budget.query.filter_by(user_id=user_id).first()
        monthly_budget = budget.monthly_amount if budget else 2000.0
        
        # Categorize spending
        category_data = {}
        for item in items:
            if item.item in category_data:
                category_data[item.item] += item.cost
            else:
                category_data[item.item] = item.cost
        
        # Build a query based on spending patterns
        query = "Give 1-2 short personalized budget tips based on the following information:"
        
        # Include general budget status
        query += f"\nTotal spending: ${total_spent:.2f}, Monthly budget: ${monthly_budget:.2f}"
        
        # Include category-specific information if available
        if category and category in category_data:
            query += f"\nSpending on {category}: ${category_data[category]:.2f}"
            
            # Find similar items in the same category
            similar_items = [i for i in items if i.item == category]
            if similar_items:
                query += f"\nOther {category} expenses:"
                for item in similar_items[:5]:  # Limit to 5 examples
                    query += f"\n- {item.name}: ${item.cost:.2f}"
        
        # Include information about the newly added item if available
        if category and item_name and cost:
            query += f"\nNew expense just added: {item_name} (Category: {category}) for ${float(cost):.2f}"
            
        # Make sure the tips are focused on the specific category if available
        if category:
            query += f"\nFocus your tips on {category} spending and be specific."
        
        # Include restrictions to keep the response focused
        restrictions = " Provide 1-2 concise, specific money-saving tips based on this spending pattern. Format as HTML with <p> tags. Keep each tip under 40 words. No introductions or conclusions. Don't mention 'Budget Buddy' directly. Focus only on actionable financial advice. Don't provide long-term financial planning advice. Focus only on immediate spending habits. DO NOT use markdown formatting like **bold** or *italic* in your response."
        query += restrictions
        
        # Process the query using Perplexity API
        response = Request(query)
        ai_response = Textonly(response)
        
        # Clean up the response
        ai_response = re.sub(r'\[\d+\]', '', ai_response)
        
        # Remove markdown asterisks if they appear
        ai_response = re.sub(r'\*\*(.*?)\*\*', r'\1', ai_response)  # Remove bold markdown
        ai_response = re.sub(r'\*(.*?)\*', r'\1', ai_response)      # Remove italic markdown
        
        # Convert any remaining markdown to HTML
        ai_response = markdown(ai_response)
        
        return jsonify({'insights': ai_response})
    except Exception as e:
        app.logger.error(f"Error generating AI insights: {e}")
        return jsonify({'insights': f"<p>Error generating insights: {str(e)}</p>"}), 500

# Create database tables with proper user_id foreign key support
with app.app_context():
    # Check if the inspector can see the tables
    inspector = sqlalchemy.inspect(db.engine)
    tables = inspector.get_table_names()
    
    # Check if we need to create tables
    if not tables or 'user' not in tables:
        app.logger.info("Creating all database tables")
        db.create_all()
    else:
        # Just make sure all tables are created without dropping
        db.create_all()
        app.logger.info("Database tables already exist, ensuring all tables are created")
    
    # Check if we have any users
    user_count = User.query.count()
    if user_count == 0:
        # Create demo user
        demo_password = generate_password_hash('demo123', method='pbkdf2:sha256')
        demo_user = User(
            username='demo',
            email='demo@example.com',
            password=demo_password
        )
        db.session.add(demo_user)
        db.session.commit()
        
        # Create default budget
        default_budget = Budget(monthly_amount=2000.0)
        db.session.add(default_budget)
        db.session.commit()
        
        # If there are any existing Todo items without user_id, assign them to demo user
        try:
            demo_user_id = demo_user.id
            orphan_todos = Todo.query.filter(Todo.user_id == None).all()
            for todo in orphan_todos:
                todo.user_id = demo_user_id
            db.session.commit()
            if orphan_todos:
                app.logger.info(f"Assigned {len(orphan_todos)} existing Todo items to demo user")
        except Exception as e:
            app.logger.error(f"Error migrating orphan todos: {e}")
        
        app.logger.info("Created demo user and default budget")
    else:
        app.logger.info(f"Database has {user_count} existing users")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    serve(app, host="0.0.0.0", port=8000)
