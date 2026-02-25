#MONGO_URI = "mongodb+srv://<vascm83000 _db _>:<1234>@zentaildb.fn6bed9.mongodb.net/" 

from pymongo import ReturnDocument
from flask import Flask, jsonify, request, render_template,redirect,url_for,session,flash
from werkzeug.utils import secure_filename
from pathlib import Path
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
import json
from functools import wraps
from datetime import datetime, timedelta, timezone
import os # Useful if you want to use environment variables later
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
# --- CONFIGURATION ---
# IMPORTANT: REPLACE THIS CONNECTION STRING WITH YOUR ACTUAL ATLAS URI
# Example format: "mongodb+srv://<db_username>:<db_password>@zentaildb.fn6bed9.mongodb.net/"
#MONGO_URI = "mongodb+srv://vasan83000_db:12345@zentaildb.fn6bed9.mongodb.net/zentail_products_db?retryWrites=true&w=majority"
MONGO_URI = "mongodb+srv://vasan83000_db_user:12345@zentaildb.fn6bed9.mongodb.net/zentail_products_db?retryWrites=true&w=majority"
DB_NAME = "zentail_products_db"

app = Flask(__name__)
app.secret_key = "zentail-super-secret-key-2025" 
bcrypt = Bcrypt(app)

app.config['MAX_CONTENT_LENGTH'] = 24 * 1024 * 1024
# --- Configure Mail (Add your credentials) ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'zentailofficial@gmail.com'
app.config['MAIL_PASSWORD'] = 'vn2006'
mail = Mail(app)
# --- MONGODB CONNECTION SETUP ---
try:
    # Set server selection timeout to avoid indefinite hanging
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # The command below will raise an exception if the connection fails
    client.admin.command('ping') 
    db = client[DB_NAME]
    products_collection = db.products
    users_collection = db.users
    breeds_collection = db.breeds
    locations_col = db["vet_locations"]
    # --- ANALYTICS COLLECTIONS ---
    analytics_visits = db.analytics_visits
    analytics_events = db.analytics_events
    appointments_collection = db["appointments"]
   

    print(f"✅ Successfully connected to MongoDB Atlas database: {DB_NAME}")
except Exception as e:
    print(f"❌ Could not connect to MongoDB Atlas. Check your MONGO_URI, IP Whitelist, and credentials. Error: {e}")
    # Note: The app will still run, but API calls will fail until the DB is reachable.
 
#print(list(breeds_collection.find()))


# Breeds image setup 
# existing:
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "images")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# add a subfolder path for breeds
BREEDS_SUBFOLDER = os.path.join(UPLOAD_FOLDER, "breeds")
os.makedirs(BREEDS_SUBFOLDER, exist_ok=True)
from bson.errors import InvalidId
#@app.route('/api/products/delete/<product_id>', methods=['DELETE'])
#def delete_product(product_id):
#    try:
#        result = products_collection.delete_one({'_id': ObjectId(product_id)})
#        if result.deleted_count == 1:
#            return jsonify({"success": True, "message": "Product deleted successfully"}), 200
#        else:
#            return jsonify({"error": "Product not found"}), 404
#    except Exception as e:
#        return jsonify({"error": f"Error deleting product: {e}"}), 500
@app.route('/api/products/delete/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        # Step 1: Try to treat the ID as an integer (for your custom numeric IDs)
        try:
            query_id = int(product_id)
        except ValueError:
            # Step 2: If not an integer, handle the "ObjectId('...')" string format
            if product_id.startswith("ObjectId"):
                import re
                product_id = re.search(r"'(.*?)'", product_id).group(1)
            query_id = ObjectId(product_id)

        result = products_collection.delete_one({"_id": query_id})

        if result.deleted_count == 1:
            return jsonify({"success": True, "message": "Product deleted successfully"}), 200
        else:
            return jsonify({"error": "Product not found"}), 404

    except Exception as e:
        # Logging the error helps you see exactly what went wrong in your console
        print(f"Delete Error: {e}")
        return jsonify({"error": f"Error deleting product: {str(e)}"}), 500
    
@app.route('/api/products', methods=['GET'])
def get_products_api():
    """Fetches all products from MongoDB."""
    try:
        products_cursor = products_collection.find()
        
        products_list = []
        for doc in products_cursor:
            # Convert ObjectId to string for JSON serialization
            doc['_id'] = str(doc['_id'])
            products_list.append(doc)

        return jsonify(products_list), 200

    except Exception as e:
        return jsonify({"error": f"Database fetching failed: {e}"}), 500

@app.route('/product-detail/<product_id>')
def product_detail(product_id):
    """Fetches a single product by ID and renders the detail view using the products.html template."""
    try:
        obj_id = ObjectId(product_id)
        # Assuming you have products_collection set up from MongoDB connection
        product = products_collection.find_one({"_id": obj_id}) 

        if product:
            product['_id'] = str(product['_id'])
            # CRITICAL: Pass the product under the name 'single_product'
            return render_template(
                'products.html', 
                active_page='products', 
                single_product=product 
            )
        else:
            return render_template('error.html', message="Product not found", status_code=404), 404

    except Exception as e:
        return render_template('error.html', message=f"Invalid Product ID: {e}"), 400

@app.route('/api/user/register', methods=['POST'])
def register_user_api():
    """Receives registration data and securely stores the user in MongoDB."""
    
    data = request.get_json()
    
    if not data or not all(field in data for field in ['email', 'password', 'name']):
        return jsonify({"error": "Missing required fields (email, password, name)."}), 400
    
    email = data['email']
    password = data['password']
    
    # 1. Check if user already exists
    if users_collection.find_one({"email": email}):
        return jsonify({"error": "This email is already registered."}), 409 # Conflict
    
    try:
        # 2. Securely hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # 3. Prepare user data for MongoDB
        user_data = {
            "name": data['name'],
            "email": email,
            "password_hash": hashed_password, # Store the hash, NOT the raw password
            "created_at": datetime.utcnow(),
            "role": "user" # Default role
        }
        
        # 4. Insert into the 'users' collection
        result = users_collection.insert_one(user_data)
        
        return jsonify({
            "success": True, 
            "message": "Account created successfully! Please log in.", 
            "id": str(result.inserted_id)
        }), 201

    except Exception as e:
        return jsonify({"error": f"Registration failed: {e}"}), 500

@app.route('/api/breeds', methods=['GET', 'POST'])
def api_breeds():
    # ---------- GET (ADMIN & USER) ----------
    if request.method == 'GET':
        breeds = list(breeds_collection.find())
        for b in breeds:
            b['_id'] = str(b['_id'])
        return jsonify(breeds)

    # ---------- POST (ADMIN ONLY) ----------
    try:
        name = request.form.get('name', '').strip()
        species = request.form.get('species', '').strip()
        purpose = request.form.get('purpose', '').strip()
        lifespan = request.form.get('lifespan', '').strip()
        about = request.form.get('about', '').strip()

        if not name:
            return jsonify({"success": False, "error": "Breed name required"}), 400

        image_file = request.files.get('image')
        image_path = None

        if image_file and image_file.filename:
            if not allowed_file(image_file.filename):
                return jsonify({"success": False, "error": "Invalid image type"}), 400

            filename = secure_filename(image_file.filename)
            save_path = os.path.join(BREEDS_SUBFOLDER, filename)
            image_file.save(save_path)
            image_path = f"images/breeds/{filename}"

        breeds_collection.insert_one({
            "name": name,
            "species": species,
            "purpose": purpose,
            "lifespan": lifespan,
            "about": about,
            "image": image_path,
            "created_at": datetime.utcnow()
        })

        return jsonify({"success": True, "message": "Breed added successfully"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/breeds/<breed_id>', methods=['DELETE'])
def delete_breed(breed_id):
    try:
        result = breeds_collection.delete_one({'_id': ObjectId(breed_id)})
        if result.deleted_count == 1:
            return jsonify({"success": True})
        return jsonify({"error": "Breed not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/admin/breeds", methods=["GET", "POST"])
def admin_breeds():
    if breeds_collection is None:
        return "Database not available", 500

    # keep your POST logic / redirect here if you are still posting to /admin/breeds

    breeds_list = list(breeds_collection.find().sort("name", 1))
    for b in breeds_list:
        b["_id"] = str(b["_id"])

    return render_template(
        "admin_breeds.html",
        active_page="breeds",
        breeds=breeds_list
    )

# --- TEMPLATE ROUTES ---
#def login_page():
#@app.route('/', methods=['GET', 'POST'])
#    # Handle Firebase callback (user already authenticated)
#
#        try:    
#            # ADMIN CHECK
#            if session['username'].lower().startswith('admin'):
#                return redirect(url_for('admin_dashboard'))
#            else:
#                return redirect(url_for('home'))
#        except:
#            pass  # Invalid token, show login
#    
#        return render_template('login.html')


# Make sure Firebase app is initialized somewhere
# firebase_admin.initialize_app()

@app.route('/', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = verify_user(email, password)
        if not user:
            flash('Invalid credentials', 'error')
            return render_template('login.html')

        firebase_email = user.email.lower().strip()
        is_admin = firebase_email.startswith('admin')

        session.permanent = True
        session['user'] = {
            'name': user.display_name or firebase_email.split('@')[0],
            'email': firebase_email,
            'role': 'admin' if is_admin else 'user'
        }

        print("SESSION SET:", session['user'])

        return redirect('/admin' if is_admin else '/home')

    return render_template('login.html')

@app.route('/firebase-login', methods=['POST'])
def firebase_login():
    data = request.get_json()
    email = data.get('email', '').lower().strip()

    if not email:
        return jsonify({"error": "email missing"}), 400

    is_admin = 'admin' in email

    session['user'] = {
        'email': email,
        'role': 'admin' if is_admin else 'user'
    }

    return jsonify({
        "redirect": "/admin" if is_admin else "/home"
    })


@app.route('/api/session-user')
def api_session_user():
    if 'user' in session:
        return jsonify(session['user'])
    return jsonify({"error": "not logged in"}), 401



@app.route('/create-account')
def create_account_page():
    """
    Defines the route to render the sign-up page.
    """
    return render_template('signup.html')




@app.route("/products")
def products():
    # Now only serves the HTML file; data is loaded via client-side JS calling /api/products
    return render_template("products.html", active_page='products')


@app.route('/api/product/add', methods=['POST'])
def add_product_api():
    try:
        data = request.get_json()

        # 🔢 Get next product ID
        counter = db.counters.find_one_and_update(
            {"_id": "product_id"},
            {"$inc": {"seq": 1}},
            return_document=ReturnDocument.AFTER,
            upsert=True
        )

        product_id = counter["seq"]  # starts from 1

        product = {
            "_id": product_id,          # 👈 CUSTOM ID
            "name": data.get("name"),
            "price": float(data.get("price")),
            "category": data.get("category"),
            "type": data.get("type"),
            "brand": data.get("brand"),
            "quantity": float(data.get("quantity")),
            "unit": data.get("unit"),
            "image": data.get("image"),
            "marketplaces": data.get("marketplaces", []),
            "created_at": datetime.utcnow()
        }

        products_collection.insert_one(product)

        return jsonify({
            "success": True,
            "message": "Product added successfully",
            "product_id": product_id
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500



@app.route("/breeds")
def breeds():
    breeds_list = list(breeds_collection.find().sort("name", 1))
    for b in breeds_list:
        b["_id"] = str(b["_id"])

    return render_template(
        "breeds.html",
        active_page="breeds",
        breeds=breeds_list
    )

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route("/admin/stats")
def admin_stats():
    try:
        products_count = products_collection.count_documents({})
        breeds_count = breeds_collection.count_documents({})
        total_bookings = appointments_collection.count_documents({})

        # Emergency logic (same as admin-bookings)
        emergencies = ['accident', 'vomiting', 'injury', 'bleeding', 'emergency', 'fracture', 'surgery']
        emergency_count = 0

        for appt in appointments_collection.find({}, {"reason": 1}):
            reason = str(appt.get("reason", "")).lower()
            if any(e in reason for e in emergencies):
                emergency_count += 1

        now = datetime.utcnow()
        day_visits = analytics_visits.count_documents({"timestamp": {"$gte": now - timedelta(days=1)}})
        month_visits = analytics_visits.count_documents({"timestamp": {"$gte": now - timedelta(days=30)}})
        year_visits = analytics_visits.count_documents({"timestamp": {"$gte": now - timedelta(days=365)}})

        top_events = list(
            analytics_events.aggregate([
                {"$group": {"_id": "$label", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 5}
            ])
        )

        return jsonify({
            "products": products_count,
            "breeds": breeds_count,
            "total_bookings": total_bookings,
            "emergency_count": emergency_count,
            "visit_daily": day_visits,
            "visit_monthly": month_visits,
            "visit_yearly": year_visits,
            "top_events": [{"label": e["_id"], "count": e["count"]} for e in top_events]
        })

    except Exception as e:
        print("Stats Error:", e)
        return jsonify({"error": str(e)}), 500


@app.route('/home')
def home():
    return render_template('base.html')

#@app.route("/book-slot", methods=["GET", "POST"])
#def book_slot():
#    appt_time = request.form.get("time")
#    if request.method == "POST":
#        # Extract data from the form
#        appointment_data = {
#            "owner_name": request.form.get("owner_name"),
#            "contact": request.form.get("phone"), # Matches your form's name="phone"
#            "email": request.form.get("email"),
#            "pet_name": request.form.get("pet_name"),
#            "pet_type": request.form.get("pet_type"),
#            "clinic_name": request.form.get("clinic_name"),
#            "datetime": datetime.utcnow(), # Or your conversion logic
#            "reason": request.form.get("reason"),
#            "status": "pending",
#            "time": appt_time,
#            "consulted": False,
#            "created_at": datetime.utcnow()
#        }
#        
#        # Save to database
#        appointments_collection.insert_one(appointment_data)
#        
#        # FIX: Added the missing return statement
#        flash("Appointment booked successfully! 🐾", "success")
#        return redirect(url_for("book_slot"))
#
#    return render_template("book_slot.html")
        # ... (rest of function)
# --- UPDATED BOOKING ROUTE ---
@app.route("/book-slot", methods=["GET", "POST"])
def book_slot():
    if request.method == "POST":
        # We take the email directly from the form to identify the user
        #user_email = request.form.get("email") 
        user_email = session.get('user', {}).get('email') or request.form.get('email', '').strip()
        if not user_email:
            flash('Email required for booking!', 'error')
            return redirect(url_for('login'))
        appointment_data = {
            "owner_name": request.form.get("owner_name"),
            "contact": request.form.get("phone"),
            "email": user_email,  # This is our unique identifier
            "pet_name": request.form.get("pet_name"),
            "pet_type": request.form.get("pet_type"),
            "clinic_name": request.form.get("clinic_name"),
            "date": request.form.get("date"),
            "time": request.form.get("time"),
            "reason": request.form.get("reason"),
            "status": "pending",
            "cancel_reason": "", # Placeholder for admin reason
            "created_at": datetime.now(timezone.utc)
        }
        appointments_collection.insert_one(appointment_data)
        flash(f"Booking recorded for {user_email}! Check status below", "success")
        return redirect(url_for('book_slot'))
    
    return render_template("book_slot.html")

# --- UPDATED API ROUTE ---
@app.route("/api/my-appointments/<email>")
def get_my_appointments(email):
    appointments = list(
        appointments_collection.find({"email": email}).sort("created_at", -1)
    )

    for appt in appointments:
        appt["_id"] = str(appt["_id"])
        appt["status"] = appt.get("status", "pending")
        appt["cancel_reason"] = appt.get("cancel_reason")

    return jsonify(appointments)


@app.route('/about')
def about():
    return render_template('about.html', active_page='about')

@app.route('/vet-locator')
def vet_locator():
    return render_template('vet_locator.html', active_page='vet-locator')

@app.post("/save-location")
def save_location():
    data = request.get_json()
    lat = data.get("lat")
    lon = data.get("lon")
    accuracy = data.get("accuracy")
    print("User GPS:", lat, lon, "±", accuracy, "m")
    return jsonify(success=True)

@app.route('/add-product')

def add_product():
    # Serves the admin product form
    return render_template('add_product.html', active_page='add-product')




@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

def log_page_visit(page_name):
    try:
        analytics_visits.insert_one({
            "page": page_name,
            "ip": request.remote_addr,
            "user_agent": request.headers.get("User-Agent"),
            "referrer": request.referrer,
            "timestamp": datetime.utcnow()
        })
    except Exception as e:
        print("Analytics visit error:", e)

@app.route("/track-event", methods=["POST"])
def track_event():
    data = request.json

    analytics_events.insert_one({
        "event_type": data.get("event_type"),   # click, nav, button
        "label": data.get("label"),             # Dashboard, Products, Buy Now
        "page": data.get("page"),
        "ip": request.remote_addr,
        "timestamp": datetime.utcnow()
    })

    return jsonify({"status": "ok"})

def get_visit_stats():
    total_visits = analytics_visits.count_documents({})

    page_breakdown = analytics_visits.aggregate([
        {"$group": {"_id": "$page", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ])

    return total_visits, list(page_breakdown)

def get_event_stats():
    return list(
        analytics_events.aggregate([
            {"$group": {
                "_id": {
                    "type": "$event_type",
                    "label": "$label"
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 20}
        ])
    )

@app.route("/admin/analytics")
def admin_analytics():
    total_visits, page_stats = get_visit_stats()
    event_stats = get_event_stats()

    return render_template(
        "admin_analytics.html",
        total_visits=total_visits,
        page_stats=page_stats,
        event_stats=event_stats
    )

@app.before_request
def track_page_visit():
    # Only track GET requests, not static files or API calls
    if request.method == "GET" and not request.path.startswith("/static"):
        log_page_visit(request.path)

@app.route("/appointment-success/<appt_id>")
def appointment_success(appt_id):
    appointment = appointments_collection.find_one(
        {"_id": ObjectId(appt_id)}
    )
    return render_template("appointment_success.html", appointment=appointment)

#@app.route("/admin/appointments")
#def admin_appointments():
#    # Fetch appointments, latest first
#    appointments = list(appointments_collection.find().sort("created_at", -1))
#
#    # Convert ObjectId & format timestamps
#    for appt in appointments:
#        appt["_id"] = str(appt["_id"])
#        if isinstance(appt.get("created_at"), datetime):
#            appt["created_at_str"] = appt["created_at"].strftime("%Y-%m-%d %H:%M:%S")
#        else:
#            appt["created_at_str"] = str(appt.get("created_at"))
#
#    return render_template("admin_appointments.html", appointments=appointments)
#

#@app.route("/admin/appointments")
#def admin_appointments():
#    appointments = list(appointments_collection.find())
#
#    appointments = list(appointments_collection.find())
#
## Format and ensure values exist
#    for appt in appointments:
#        appt["_id"] = str(appt["_id"])
#
#    # Date
#        appt["date_str"] = appt.get("date").strftime("%Y-%m-%d") if appt.get("date") else "—"
#    # Time
#        appt["time_str"] = appt.get("time").strftime("%I:%M %p") if appt.get("time") else "—"
#    # Created At
#        appt["created_at_str"] = appt.get("created_at").strftime("%Y-%m-%d %H:%M") if appt.get("created_at") else "—"
#    
#    # Consulted timestamp
#        appt["consulted_at_str"] = appt.get("consulted_at").strftime("%Y-%m-%d %H:%M:%S") if appt.get("consulted_at") else "—"
#
## Custom sort: priority high → low, then created_at ascending
#    def sort_key(appt):
#    # Default priority = 1 if missing
#        priority = int(appt.get("priority") or 1)
#        created_at = appt.get("created_at") or datetime.utcnow()
#        return ( -priority, created_at )
#
#    appointments.sort(key=sort_key)
#
#    return render_template("admin_bookings.html", appointments=appointments)

#@app.route("/admin/bookings")
#def admin_bookings():
#    # Fetch all bookings
#    appointments = list(appointments_collection.find())
#    
#    # EMERGENCY SORTING LOGIC
#    emergencies = ['accident', 'vomiting', 'injury', 'bleeding', 'emergency', 'fracture','surgery']
#    
#    def get_priority(appt):
#        reason = str(appt.get('reason', '')).lower()
#        # 0 = Emergency (Top), 1 = Normal
#        priority = 0 if any(e in reason for e in emergencies) else 1
#        return (priority, appt.get('created_at') or datetime.max)
#
#    appointments.sort(key=get_priority)
#
#    for appt in appointments:
#        appt["_id"] = str(appt["_id"])
#        # Ensure 'phone' is mapped to 'contact' for UI consistency
#        appt["contact"] = appt.get("phone") or appt.get("contact")
#        if isinstance(appt.get("datetime"), datetime):
#            appt["date"] = appt["datetime"].strftime("%Y-%m-%d")
#            appt["time"] = appt["datetime"].strftime("%I:%M %p")
#    
#    return render_template("admin_bookings.html", appointments=appointments)

@app.route("/admin/bookings")
def admin_bookings():
    appointments = list(appointments_collection.find())
    
    # Emergency keywords for sorting
    emergencies = ['accident', 'vomiting', 'injury', 'bleeding', 'emergency', 'fracture', 'surgery']
    
    for appt in appointments:
        appt["_id"] = str(appt["_id"])
        
        # Handle Date/Time Display
        # If your data uses 'datetime' object (as seen in book_slot), extract them:
        if isinstance(appt.get("datetime"), datetime):
            appt["date"] = appt["datetime"].strftime("%Y-%m-%d")
            appt["time"] = appt["datetime"].strftime("%I:%M %p")
        
        # Ensure 'contact' field is consistent
        appt["contact"] = appt.get("contact") or appt.get("phone") or "No Number"

    # Sorting logic: Emergencies at the top
    def get_priority(appt):
        reason = str(appt.get('reason', '')).lower()
        priority = 0 if any(e in reason for e in emergencies) else 1
        return (priority, appt.get('created_at') or datetime.max)

    appointments.sort(key=get_priority)
    return render_template("admin_bookings.html", appointments=appointments)
    
@app.route("/admin/appointments/cancel/<appt_id>", methods=["POST"])
def cancel_appointment(appt_id):
    data = request.get_json()
    reason = data.get("reason", "Not specified")
    appt = appointments_collection.find_one({"_id": ObjectId(appt_id)})
    
    appointments_collection.update_one(
        {"_id": ObjectId(appt_id)},
        {"$set": {"status": "Cancelled", "cancel_reason": reason, "cancelled": True}}
    )
    
    # Send Email Notification
    try:
        msg = Message("Appointment Cancelled - ZenTail", 
                      sender=app.config['MAIL_USERNAME'], 
                      recipients=[appt['email']])
        msg.body = f"Hello {appt['owner_name']}, your appointment for {appt['pet_name']} has been cancelled. Reason: {reason}"
        mail.send(msg)
    except Exception as e:
        print(f"Mail failed: {e}")
        
    return jsonify({"success": True})

# --- Delete Route ---
@app.route("/admin/appointments/delete/<appt_id>", methods=["POST"])
def delete_appointment(appt_id):
    try:
        appointments_collection.delete_one({"_id": ObjectId(appt_id)})
        return jsonify({"success": True, "message": "Record deleted"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    
@app.route("/admin/appointments/reopen/<appt_id>", methods=["POST"])
def reopen_appointment(appt_id):
    # This resets the status so it moves back to 'New & Urgent'
    appointments_collection.update_one(
        {"_id": ObjectId(appt_id)},
        {"$set": {"status": "pending", "consulted": False, "cancelled": False}}
    )
    return jsonify({"success": True})
# AJAX API to fetch data without reload
@app.route("/api/admin/fetch_bookings")
def fetch_bookings_api():
    appointments = list(appointments_collection.find())
    for appt in appointments:
        appt["_id"] = str(appt["_id"])
    return jsonify(appointments)


@app.route("/admin/appointments/approve/<appt_id>", methods=["POST"])
def approve_appointment(appt_id):
    result = appointments_collection.update_one(
        {"_id": ObjectId(appt_id)},
        {"$set": {"status": "confirmed", "confirmed_at": datetime.utcnow()}}
    )
    return jsonify({"success": True, "message": "Appointment confirmed 🐾"})

@app.route("/admin/appointments/consulted/<appt_id>", methods=["POST"])
def mark_consulted(appt_id):
    appointments_collection.update_one(
        {"_id": ObjectId(appt_id)},
        {
            "$set": {
                "consulted": True,
                "consulted_at": datetime.utcnow()
            }
        }
    )
    return jsonify({"success": True})

@app.route("/admin/appointments/complete/<appt_id>", methods=["POST"])
def complete_appointment(appt_id):
    appointments_collection.update_one(
        {"_id": ObjectId(appt_id)},
        {
            "$set": {
                "status": "completed",
                "completed_at": datetime.utcnow()
            }
        }
    )
    return jsonify({"success": True})


@app.route('/privacy')
def privacy():
    return render_template('privacy.html')





if __name__ == '__main__':
    # Flask application starts here
    app.run(debug=True)