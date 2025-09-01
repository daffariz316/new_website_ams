import os
import urllib.parse
from datetime import timedelta
from functools import wraps
import requests

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, make_response, flash
)
from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials, firestore, auth
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import MySQLdb

# ===============================
load_dotenv()

# ===============================
# APP & CONFIG
# ===============================
app = Flask(__name__, template_folder='../templates', static_folder='../static')

app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-change-me')

app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
app.config['SESSION_REFRESH_EACH_REQUEST'] = True

# ===============================
# FIREBASE ADMIN SDK
# ===============================
FIREBASE_CRED_PATH = os.getenv('FIREBASE_CRED_PATH', 'firebase-auth.json')
cred = credentials.Certificate(FIREBASE_CRED_PATH)
firebase_admin.initialize_app(cred)
db = firestore.client()

# ===============================
# MYSQL CONFIG
# ===============================
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ahsani'
mysql = MySQL(app)

# ===============================
# UPLOAD FOLDER & EXTENSIONS
# ===============================
UPLOAD_FOLDER = os.path.join(app.static_folder, 'assets/videos')
UPLOAD_LOGO_FOLDER = os.path.join(app.static_folder, 'assets/client')

ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_LOGO_FOLDER, exist_ok=True)

def allowed_video_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS

def allowed_image_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

# ===============================
# HELPERS
# ===============================
def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ===============================
# AUTH ROUTES
# ===============================
@app.route('/auth', methods=['POST'])
def authorize():
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return "Unauthorized", 401

    token = token[7:]
    try:
        decoded_token = auth.verify_id_token(token, check_revoked=True, clock_skew_seconds=60)
        session['user'] = decoded_token
        return redirect(url_for('dashboard'))
    except Exception:
        return "Unauthorized", 401
    
# Middleware untuk disable cache di semua response
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# @app.route('/logout')
# def logout():
#     session.clear()
#     flash('Anda telah logout.', 'info')
#     response = make_response(redirect(url_for('login')))
#     response.set_cookie('session', '', expires=0)
#     return response

@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah logout.', 'info')
    response = make_response(redirect(url_for('login')))
    response.set_cookie('session', '', expires=0)  # hapus cookie
    return response

# ===============================
# PUBLIC ROUTES
# ===============================
# @app.route('/')
# def index():
#     cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cur.execute("SELECT * FROM provinces WHERE status = 1")  # Ambil provinsi yang aktif
#     provinces = cur.fetchall()
#     cur.close()
#     return render_template('index.html', provinces=provinces)
# @app.route('/')
# def index():
#     cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cur.execute("SELECT * FROM provinces WHERE is_enabled = 1")
#     provinces = cur.fetchall()
#     cur.close()
#     return render_template('index.html', provinces=provinces)
# @app.route('/')
# def index():
#     cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cur.execute("SELECT * FROM provinces WHERE is_enabled = 1")
#     provinces = cur.fetchall()

#     cur.execute("SELECT * FROM regions WHERE is_enabled = 1")
#     regions = cur.fetchall()
#     cur.close()

#     for province in provinces:
#         province['kota'] = [r for r in regions if r['province_id'] == province['id'] and r['type'].lower() == 'kota']
#         province['kabupaten'] = [r for r in regions if r['province_id'] == province['id'] and r['type'].lower() == 'kabupaten']

#     return render_template('index.html', provinces=provinces)
# @app.route('/')
# def index():
#     cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

#     # provinces & regions (sudah ada)
#     cur.execute("SELECT * FROM provinces WHERE is_enabled = 1")
#     provinces = cur.fetchall()

#     cur.execute("SELECT * FROM regions WHERE is_enabled = 1")
#     regions = cur.fetchall()

#     # projects — ambil semua, newest first
#     cur.execute("SELECT * FROM projects ORDER BY created_at DESC")
#     projects = cur.fetchall()

#     cur.close()

#     # gabungkan kota/kabupaten ke tiap province
#     for province in provinces:
#         province['kota'] = [r for r in regions if r['province_id'] == province['id'] and r['type'].lower() == 'kota']
#         province['kabupaten'] = [r for r in regions if r['province_id'] == province['id'] and r['type'].lower() == 'kabupaten']

#     # lempar projects ke template
#     return render_template('index.html', provinces=provinces, projects=projects)
@app.route('/')
def index():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # provinces & regions
    cur.execute("SELECT * FROM provinces WHERE is_enabled = 1")
    provinces = cur.fetchall()

    cur.execute("SELECT * FROM regions WHERE is_enabled = 1")
    regions = cur.fetchall()

    # projects
    cur.execute("SELECT * FROM projects ORDER BY created_at DESC")
    projects = cur.fetchall()

    # technologies
    cur.execute("SELECT * FROM project_technologies")
    techs = cur.fetchall()

    cur.close()

    # gabungkan kota/kabupaten ke tiap province
    for province in provinces:
        province['kota'] = [r for r in regions if r['province_id'] == province['id'] and r['type'].lower() == 'kota']
        province['kabupaten'] = [r for r in regions if r['province_id'] == province['id'] and r['type'].lower() == 'kabupaten']

    # gabungkan teknologi ke tiap project
    for project in projects:
        project['teknologi'] = [t['nama_teknologi'] for t in techs if t['project_id'] == project['id']]

    return render_template('index.html', provinces=provinces, projects=projects, regions=regions  )

@app.context_processor
def inject_user():
    return dict(user=session.get('user'))

# @app.route('/login')
# def login():
#     if 'user' in session:
#         return redirect(url_for('dashboard'))
#     return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')


# @app.route('/signup')
# def signup():
#     if 'user' in session:
#         return redirect(url_for('dashboard'))

#     if request.method == 'POST':
#         # proses simpan user baru di database
#         return redirect(url_for('login')) 
    
#     return render_template('signup.html')
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        # proses simpan user baru di database
        return redirect(url_for('login')) 
    
    return render_template('signup.html')

@app.route('/reset-password')
def reset_password():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('forgot_password.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

# @app.route('/portfolio')
# def portfolio():
#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cursor.execute("SELECT * FROM projects ORDER BY id DESC")
#     projects = cursor.fetchall()
#     return render_template('add.html', projects=projects)

@app.route('/portfolio')
def portfolio():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Ambil parameter pencarian
    q = request.args.get('q', '', type=str)

    # Ambil parameter pagination
    page = request.args.get('page', 1, type=int)
    per_page = 6
    offset = (page - 1) * per_page

    # Query hitung total
    if q:
        cursor.execute("SELECT COUNT(*) as total FROM projects WHERE judul LIKE %s OR klien LIKE %s", (f"%{q}%", f"%{q}%"))
    else:
        cursor.execute("SELECT COUNT(*) as total FROM projects")
    total = cursor.fetchone()['total']

    # Query data
    if q:
        cursor.execute("""
            SELECT * FROM projects
            WHERE judul LIKE %s OR klien LIKE %s
            ORDER BY id DESC
            LIMIT %s OFFSET %s
        """, (f"%{q}%", f"%{q}%", per_page, offset))
    else:
        cursor.execute("""
            SELECT * FROM projects
            ORDER BY id DESC
            LIMIT %s OFFSET %s
        """, (per_page, offset))

    projects = cursor.fetchall()
    cursor.close()

    # Hitung range data tampil
    start = offset + 1 if total > 0 else 0
    end = min(offset + per_page, total)

    return render_template(
        'add.html',
        projects=projects,
        page=page,
        per_page=per_page,
        total=total,
        start=start,
        end=end,
        q=q   # kirim query pencarian ke template
    )



# @app.route('/admin/provinces', methods=['GET', 'POST'])
# @auth_required
# def manage_provinces():
#     cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

#     if request.method == 'POST':
#         name = request.form['name']
#         logo = request.files['logo']

#         if logo and allowed_image_file(logo.filename):
#             filename = secure_filename(logo.filename)
#             logo.save(os.path.join(UPLOAD_LOGO_FOLDER, filename))
#             logo_path = f'assets/client/{filename}'
#         else:
#             logo_path = ''

#         cur.execute("INSERT INTO provinces (name, logo) VALUES (%s, %s)", (name, logo_path))
#         mysql.connection.commit()
#         cur.close()
#         return redirect(url_for('manage_provinces'))

#     cur.execute("SELECT * FROM provinces")
#     provinces = cur.fetchall()
#     cur.close()
#     return render_template('admin_provinces.html', provinces=provinces)

# @app.route('/admin/provinces', methods=['GET', 'POST'])
# @auth_required
# def manage_provinces():
#     cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     try:
#         # POST (tambah)
#         if request.method == 'POST':
#             name = request.form.get('name', '').strip()
#             logo = request.files.get('logo')

#             if not name:
#                 flash('Nama provinsi wajib diisi.', 'warning')
#                 return redirect(url_for('manage_provinces'))

#             logo_path = ''
#             if logo and allowed_image_file(logo.filename):
#                 filename = secure_filename(logo.filename)
#                 import time
#                 filename = f"{int(time.time())}_{filename}"
#                 logo.save(os.path.join(UPLOAD_LOGO_FOLDER, filename))
#                 logo_path = f'assets/client/{filename}'

#             cur.execute(
#                 "INSERT INTO provinces (name, logo) VALUES (%s, %s)",
#                 (name, logo_path)
#             )
#             mysql.connection.commit()
#             flash('Provinsi berhasil ditambahkan.', 'success')
#             return redirect(url_for('manage_provinces'))

#         # GET (list + search) — tampilkan SEMUA provinsi (aktif & non-aktif)
#         search_query = request.args.get('q', '').strip()
#         if search_query:
#             cur.execute("""
#                 SELECT * FROM provinces
#                 WHERE name LIKE %s
#                 ORDER BY name ASC
#             """, (f"%{search_query}%",))
#         else:
#             cur.execute("""
#                 SELECT * FROM provinces
#                 ORDER BY name ASC
#             """)
#         provinces = cur.fetchall()
#         return render_template('admin_provinces.html', provinces=provinces, q=search_query)
#     finally:
#         cur.close()

@app.route('/admin/provinces', methods=['GET', 'POST'])
@auth_required
def manage_provinces():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        # POST (tambah)
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            logo = request.files.get('logo')

            if not name:
                flash('Nama provinsi wajib diisi.', 'warning')
                return redirect(url_for('manage_provinces'))

            logo_path = ''
            if logo and allowed_image_file(logo.filename):
                filename = secure_filename(logo.filename)
                import time
                filename = f"{int(time.time())}_{filename}"
                logo.save(os.path.join(UPLOAD_LOGO_FOLDER, filename))
                logo_path = f'assets/client/{filename}'

            cur.execute(
                "INSERT INTO provinces (name, logo) VALUES (%s, %s)",
                (name, logo_path)
            )
            mysql.connection.commit()
            flash('Provinsi berhasil ditambahkan.', 'success')
            return redirect(url_for('manage_provinces'))

        # GET (list + search) — pagination
        search_query = request.args.get('q', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = 10
        offset = (page - 1) * per_page

        # Hitung total
        if search_query:
            cur.execute("SELECT COUNT(*) as total FROM provinces WHERE name LIKE %s", (f"%{search_query}%",))
        else:
            cur.execute("SELECT COUNT(*) as total FROM provinces")
        total = cur.fetchone()['total']

        # Ambil data per halaman
        if search_query:
            cur.execute("""
                SELECT * FROM provinces
                WHERE name LIKE %s
                ORDER BY name ASC
                LIMIT %s OFFSET %s
            """, (f"%{search_query}%", per_page, offset))
        else:
            cur.execute("""
                SELECT * FROM provinces
                ORDER BY name ASC
                LIMIT %s OFFSET %s
            """, (per_page, offset))

        provinces = cur.fetchall()

        # Hitung range data ditampilkan
        start = offset + 1 if total > 0 else 0
        end = min(offset + per_page, total)

        return render_template(
            'admin_provinces.html',
            provinces=provinces,
            q=search_query,
            page=page,
            per_page=per_page,
            total=total,
            start=start,
            end=end
        )
    finally:
        cur.close()

# @app.route('/admin/regions', methods=['GET', 'POST'])
# @auth_required
# def manage_regions():
#     cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

#     # Ambil daftar provinsi (untuk form tambah)
#     cur.execute("SELECT * FROM provinces")
#     provinces = cur.fetchall()

#     # Handle form POST (tambah data region)
#     if request.method == 'POST':
#         province_id = request.form['province_id']
#         name = request.form['name']
#         region_type = request.form['type']
#         logo = request.files['logo']

#         if logo and allowed_image_file(logo.filename):
#             filename = secure_filename(logo.filename)
#             logo.save(os.path.join(UPLOAD_LOGO_FOLDER, filename))
#             logo_path = f'assets/client/{filename}'
#         else:
#             logo_path = ''

#         cur.execute(
#             "INSERT INTO regions (province_id, name, type, logo) VALUES (%s, %s, %s, %s)",
#             (province_id, name, region_type, logo_path)
#         )
#         mysql.connection.commit()
#         cur.close()
#         return redirect(url_for('manage_regions'))

#     # Handle GET: ambil data region (dengan pencarian jika ada)
#     search_query = request.args.get('q', '').strip()

#     if search_query:
#         cur.execute("""
#             SELECT r.*, p.name AS province_name
#             FROM regions r
#             JOIN provinces p ON r.province_id = p.id
#             WHERE r.is_enabled = 1 AND (
#                 r.name LIKE %s OR r.type LIKE %s OR p.name LIKE %s
#             )
#             ORDER BY p.name, r.type, r.name
#         """, (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"))
#     else:
#         cur.execute("""
#             SELECT r.*, p.name AS province_name
#             FROM regions r
#             JOIN provinces p ON r.province_id = p.id
#             ORDER BY p.name, r.type, r.name
#         """)

#     regions = cur.fetchall()
#     cur.close()

#     return render_template('admin_regions.html', provinces=provinces, regions=regions)
# @app.route('/admin/regions', methods=['GET', 'POST'])
# @auth_required
# def manage_regions():
#     cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

#     # Ambil daftar provinsi (untuk form tambah)
#     cur.execute("SELECT * FROM provinces")
#     provinces = cur.fetchall()

#     # Handle form POST (tambah data region)
#     if request.method == 'POST':
#         province_id = request.form['province_id']
#         name = request.form['name']
#         region_type = request.form['type']
#         logo = request.files['logo']

#         if logo and allowed_image_file(logo.filename):
#             filename = secure_filename(logo.filename)
#             logo.save(os.path.join(UPLOAD_LOGO_FOLDER, filename))
#             logo_path = f'assets/client/{filename}'
#         else:
#             logo_path = ''

#         cur.execute(
#             "INSERT INTO regions (province_id, name, type, logo) VALUES (%s, %s, %s, %s)",
#             (province_id, name, region_type, logo_path)
#         )
#         mysql.connection.commit()
#         cur.close()
#         return redirect(url_for('manage_regions'))

#     # --- PAGINATION SETUP ---
#     page = request.args.get('page', 1, type=int)
#     per_page = 10  # jumlah data per halaman
#     offset = (page - 1) * per_page

#     search_query = request.args.get('q', '').strip()

#     # Hitung total data
#     if search_query:
#         cur.execute("""
#             SELECT COUNT(*) as total
#             FROM regions r
#             JOIN provinces p ON r.province_id = p.id
#             WHERE r.is_enabled = 1 AND (
#                 r.name LIKE %s OR r.type LIKE %s OR p.name LIKE %s
#             )
#         """, (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"))
#     else:
#         cur.execute("SELECT COUNT(*) as total FROM regions")
#     total = cur.fetchone()['total']

#     # Ambil data sesuai pagination
#     if search_query:
#         cur.execute("""
#             SELECT r.*, p.name AS province_name
#             FROM regions r
#             JOIN provinces p ON r.province_id = p.id
#             WHERE r.is_enabled = 1 AND (
#                 r.name LIKE %s OR r.type LIKE %s OR p.name LIKE %s
#             )
#             ORDER BY p.name, r.type, r.name
#             LIMIT %s OFFSET %s
#         """, (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", per_page, offset))
#     else:
#         cur.execute("""
#             SELECT r.*, p.name AS province_name
#             FROM regions r
#             JOIN provinces p ON r.province_id = p.id
#             ORDER BY p.name, r.type, r.name
#             LIMIT %s OFFSET %s
#         """, (per_page, offset))

#     regions = cur.fetchall()
#     cur.close()

#     # Hitung range data ditampilkan
#     start = offset + 1 if total > 0 else 0
#     end = min(offset + per_page, total)

#     return render_template(
#         'admin_regions.html',
#         provinces=provinces,
#         regions=regions,
#         page=page,
#         per_page=per_page,
#         total=total,
#         start=start,
#         end=end
#     )
def get_coordinates(city_name, province_name):
    query = f"{city_name}, {province_name}, Indonesia"
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={query}"
    try:
        response = requests.get(url, headers={"User-Agent": "MyApp/1.0"})
        data = response.json()
        if data:
            lat = float(data[0]["lat"])
            lng = float(data[0]["lon"])
            return lat, lng
    except Exception as e:
        print("Error geocoding:", e)
    return None, None


@app.route('/admin/regions', methods=['GET', 'POST'])
@auth_required
def manage_regions():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Ambil daftar provinsi (untuk form tambah)
    cur.execute("SELECT * FROM provinces")
    provinces = cur.fetchall()

    # Handle form POST (tambah data region)
    if request.method == 'POST':
        province_id = request.form['province_id']
        name = request.form['name']
        region_type = request.form['type']
        logo = request.files['logo']

        # Ambil nama provinsi untuk query geocoding
        cur.execute("SELECT name FROM provinces WHERE id = %s", (province_id,))
        prov = cur.fetchone()
        province_name = prov['name'] if prov else ''

        # Cari koordinat otomatis (lat/lng)
        lat, lng = get_coordinates(name, province_name)

        # Upload logo
        if logo and allowed_image_file(logo.filename):
            filename = secure_filename(logo.filename)
            logo.save(os.path.join(UPLOAD_LOGO_FOLDER, filename))
            logo_path = f'assets/client/{filename}'
        else:
            logo_path = ''

        # Simpan data ke DB
        cur.execute(
            "INSERT INTO regions (province_id, name, type, logo, latitude, longitude, is_enabled) VALUES (%s, %s, %s, %s, %s, %s, 1)",
            (province_id, name, region_type, logo_path, lat, lng)
        )
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('manage_regions'))

    # --- PAGINATION SETUP ---
    page = request.args.get('page', 1, type=int)
    per_page = 10  # jumlah data per halaman
    offset = (page - 1) * per_page

    search_query = request.args.get('q', '').strip()

    # Hitung total data
    if search_query:
        cur.execute("""
            SELECT COUNT(*) as total
            FROM regions r
            JOIN provinces p ON r.province_id = p.id
            WHERE r.is_enabled = 1 AND (
                r.name LIKE %s OR r.type LIKE %s OR p.name LIKE %s
            )
        """, (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"))
    else:
        cur.execute("SELECT COUNT(*) as total FROM regions")
    total = cur.fetchone()['total']

    # Ambil data sesuai pagination
    if search_query:
        cur.execute("""
            SELECT r.*, p.name AS province_name
            FROM regions r
            JOIN provinces p ON r.province_id = p.id
            WHERE r.is_enabled = 1 AND (
                r.name LIKE %s OR r.type LIKE %s OR p.name LIKE %s
            )
            ORDER BY p.name, r.type, r.name
            LIMIT %s OFFSET %s
        """, (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", per_page, offset))
    else:
        cur.execute("""
            SELECT r.*, p.name AS province_name
            FROM regions r
            JOIN provinces p ON r.province_id = p.id
            ORDER BY p.name, r.type, r.name
            LIMIT %s OFFSET %s
        """, (per_page, offset))

    regions = cur.fetchall()
    cur.close()

    # Hitung range data ditampilkan
    start = offset + 1 if total > 0 else 0
    end = min(offset + per_page, total)

    return render_template(
        'admin_regions.html',
        provinces=provinces,
        regions=regions,
        page=page,
        per_page=per_page,
        total=total,
        start=start,
        end=end
    )


# @app.route('/admin/region/edit/<int:id>', methods=['GET', 'POST'])
# @auth_required
# def edit_region(id):
#     cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

#     if request.method == 'POST':
#         name = request.form['name']
#         province_id = request.form['province_id']
#         logo = request.files['logo']

#         if logo and logo.filename != '':
#             filename = secure_filename(logo.filename)
#             logo.save(os.path.join(UPLOAD_LOGO_FOLDER, filename))
#             logo_path = f'assets/client/{filename}'

#             cur.execute("""
#                 UPDATE regions SET name = %s, logo = %s, province_id = %s WHERE id = %s
#             """, (name, logo_path, province_id, id))
#         else:
#             cur.execute("""
#                 UPDATE regions SET name = %s, province_id = %s WHERE id = %s
#             """, (name, province_id, id))

#         mysql.connection.commit()
#         cur.close()
#         return redirect(url_for('manage_regions'))

#     # GET: Ambil data region & daftar provinsi
#     cur.execute("SELECT * FROM regions WHERE id = %s", (id,))
#     region = cur.fetchone()
#     cur.execute("SELECT * FROM provinces")
#     provinces = cur.fetchall()
#     cur.close()

#     return render_template('edit_regions.html', region=region, provinces=provinces)
def get_coordinates_from_name(place_name):
    """Ambil latitude & longitude pakai Nominatim API"""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": place_name, "format": "json", "limit": 1}
    headers = {"User-Agent": "your-app-name"}
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return float(data['lat']), float(data['lon'])
    return None, None


@app.route('/admin/region/edit/<int:id>', methods=['GET', 'POST'])
@auth_required
def edit_region(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        name = request.form.get('name')
        province_id = request.form.get('province_id')
        logo = request.files.get('logo')

        # Ambil logo lama
        cur.execute("SELECT logo FROM regions WHERE id = %s", (id,))
        old_region = cur.fetchone()
        old_logo = old_region['logo'] if old_region else None

        logo_path = old_logo

        if logo and logo.filename != '':
            filename = secure_filename(logo.filename)

            import time
            filename = f"{int(time.time())}_{filename}"

            logo.save(os.path.join(UPLOAD_LOGO_FOLDER, filename))
            logo_path = f'client/{filename}'

            # opsional: hapus logo lama
            if old_logo and os.path.exists(os.path.join('static', old_logo)):
                try:
                    os.remove(os.path.join('static', old_logo))
                except Exception as e:
                    print("Gagal hapus logo lama:", e)

        # Ambil lat & lng baru dari geocoding
        latitude, longitude = get_coordinates_from_name(name)

        # Update data
        cur.execute("""
            UPDATE regions 
            SET name = %s, logo = %s, province_id = %s, latitude = %s, longitude = %s
            WHERE id = %s
        """, (name, logo_path, province_id, latitude, longitude, id))

        mysql.connection.commit()
        cur.close()
        return redirect(url_for('manage_regions'))

    # GET: Ambil data region & daftar provinsi
    cur.execute("SELECT * FROM regions WHERE id = %s", (id,))
    region = cur.fetchone()

    cur.execute("SELECT * FROM provinces")
    provinces = cur.fetchall()
    cur.close()

    return render_template('edit_regions.html', region=region, provinces=provinces)

@app.route('/admin/region/delete/<int:id>', methods=['POST'])
@auth_required
def delete_region(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM regions WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('manage_regions'))



@app.route('/admin/provinces/toggle/<int:id>', methods=['POST'])
@auth_required
def toggle_province_status(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT is_enabled FROM provinces WHERE id = %s", (id,))
    province = cur.fetchone()
    if province:
        new_status = not province['is_enabled']
        cur.execute("UPDATE provinces SET is_enabled = %s WHERE id = %s", (new_status, id))
        mysql.connection.commit()
    cur.close()
    return redirect(url_for('manage_provinces'))

@app.route('/admin/provinces/edit/<int:id>', methods=['GET', 'POST'])
@auth_required
def edit_province(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        name = request.form['name']
        logo = request.files['logo']
        if logo and allowed_image_file(logo.filename):
            filename = secure_filename(logo.filename)
            save_path = os.path.join(UPLOAD_LOGO_FOLDER, filename)
            logo.save(save_path)
            logo_path = f'assets/client/{filename}'
            cur.execute(
                "UPDATE provinces SET name=%s, logo=%s WHERE id=%s",
                (name, logo_path, id)
            )
        else:
            cur.execute(
                "UPDATE provinces SET name=%s WHERE id=%s",
                (name, id)
            )
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('manage_provinces'))
    else:
        cur.execute("SELECT * FROM provinces WHERE id=%s", (id,))
        province = cur.fetchone()
        cur.close()
        return render_template('edit_province.html', province=province)

@app.route('/admin/provinces/delete/<int:id>', methods=['POST'])
@auth_required
def delete_province(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM provinces WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('manage_provinces'))

# ===============================
# PORTFOLIO ADMIN FORM & UPLOAD
# ===============================
# @app.route('/portfolio/add', methods=['GET', 'POST'])
# @auth_required
# def add_portfolio():
#     if request.method == 'POST':
#         judul = request.form['judul']
#         klien = request.form['klien']
#         deskripsi = request.form['deskripsi']
#         durasi = request.form['durasi']
        
#         fitur_utama_raw = request.form['fitur_utama']
#         fitur_utama_list = [f.strip() for f in fitur_utama_raw.split('\n') if f.strip()]
#         fitur_utama = '\n'.join(fitur_utama_list)

#         # fitur = request.form['fitur'].split(',') if request.form['fitur'] else []
#         teknologi = request.form['teknologi'].split(',') if request.form['teknologi'] else []

#         video_file = request.files['video_file']

#         if video_file and allowed_video_file(video_file.filename):
#             filename = secure_filename(video_file.filename)
#             save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             video_file.save(save_path)
#             video_path = f'assets/videos/{filename}'

#             cur = mysql.connection.cursor()
#             cur.execute(
#                 "INSERT INTO projects (judul, klien, deskripsi, fitur_utama, durasi, video_path) VALUES (%s, %s, %s, %s, %s, %s)",
#                 (judul, klien, deskripsi, fitur_utama, durasi, video_path)
#             )
#             project_id = cur.lastrowid

#             # for f in fitur:
#             #     cur.execute("INSERT INTO project_features (project_id, nama_fitur) VALUES (%s, %s)", (project_id, f.strip()))

#             for t in teknologi:
#                 cur.execute("INSERT INTO project_technologies (project_id, nama_teknologi) VALUES (%s, %s)", (project_id, t.strip()))

#             mysql.connection.commit()
#             cur.close()

#             return redirect(url_for('add_portfolio'))
#         else:
#             return "File tidak valid", 400

#     cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cur.execute("SELECT * FROM projects ORDER BY id DESC")
#     projects = cur.fetchall()
#     cur.close()

#     return render_template('add.html', projects=projects)

@app.route('/portfolio/add', methods=['GET', 'POST'])
@auth_required
def add_portfolio():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        judul = request.form['judul']
        klien = request.form['klien']
        deskripsi = request.form['deskripsi']
        durasi = request.form['durasi']

        fitur_utama_raw = request.form['fitur_utama']
        fitur_utama_list = [f.strip() for f in fitur_utama_raw.split('\n') if f.strip()]
        fitur_utama = '\n'.join(fitur_utama_list)

        teknologi = request.form['teknologi'].split(',') if request.form['teknologi'] else []

        video_file = request.files['video_file']

        if video_file and allowed_video_file(video_file.filename):
            filename = secure_filename(video_file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            video_file.save(save_path)
            video_path = f'assets/videos/{filename}'

            cur.execute(
                "INSERT INTO projects (judul, klien, deskripsi, fitur_utama, durasi, video_path) VALUES (%s, %s, %s, %s, %s, %s)",
                (judul, klien, deskripsi, fitur_utama, durasi, video_path)
            )
            project_id = cur.lastrowid

            for t in teknologi:
                cur.execute("INSERT INTO project_technologies (project_id, nama_teknologi) VALUES (%s, %s)", (project_id, t.strip()))

            mysql.connection.commit()
            cur.close()

            return redirect(url_for('add_portfolio'))
        else:
            return "File tidak valid", 400

    # 🔹 PAGINATION
    page = request.args.get('page', 1, type=int)
    per_page = 6
    offset = (page - 1) * per_page

    # hitung total projects
    cur.execute("SELECT COUNT(*) as total FROM projects")
    total = cur.fetchone()['total']

    # ambil projects sesuai pagination
    cur.execute("""
        SELECT * FROM projects
        ORDER BY id DESC
        LIMIT %s OFFSET %s
    """, (per_page, offset))
    projects = cur.fetchall()
    cur.close()

    # hitung range tampil
    start = offset + 1 if total > 0 else 0
    end = min(offset + per_page, total)

    return render_template(
        'add.html',
        projects=projects,
        page=page,
        per_page=per_page,
        total=total,
        start=start,
        end=end
    )

@app.route('/portfolio/edit/<int:id>', methods=['GET', 'POST'])
@auth_required
def edit_portfolio(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        judul = request.form['judul']
        klien = request.form['klien']
        deskripsi = request.form['deskripsi']
        durasi = request.form['durasi']
        fitur_utama_raw = request.form['fitur_utama']
        fitur_utama_list = [f.strip() for f in fitur_utama_raw.split('\n') if f.strip()]
        fitur_utama = '\n'.join(fitur_utama_list)

        video_file = request.files['video_file']
        if video_file and allowed_video_file(video_file.filename):
            filename = secure_filename(video_file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            video_file.save(save_path)
            video_path = f'assets/videos/{filename}'
            cur.execute("""
                UPDATE projects SET judul=%s, klien=%s, deskripsi=%s, fitur_utama=%s, durasi=%s, video_path=%s WHERE id=%s
            """, (judul, klien, deskripsi, fitur_utama, durasi, video_path, id))
        else:
            cur.execute("""
                UPDATE projects SET judul=%s, klien=%s, deskripsi=%s, fitur_utama=%s, durasi=%s WHERE id=%s
            """, (judul, klien, deskripsi, fitur_utama, durasi, id))

        mysql.connection.commit()
        cur.close()
        return redirect(url_for('add_portfolio'))

    else:
        cur.execute("SELECT * FROM projects WHERE id=%s", (id,))
        project = cur.fetchone()
        cur.close()
        return render_template('edit_portfolio.html', project=project)

@app.route('/portfolio/delete/<int:id>', methods=['POST'])
@auth_required
def delete_portfolio(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM projects WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('add_portfolio'))

# ===============================
# CONTACT FORM -> WHATSAPP
# ===============================
@app.route('/send_message', methods=['POST'])
def send_message():
    name = request.form['name']
    email = request.form['email']
    subject = request.form['subject']
    message = request.form['message']

    whatsapp_number = os.getenv('WHATSAPP_NUMBER', '62895372499072')

    text = f"Halo! Saya {name} {email} {subject} {message}"
    encoded_text = urllib.parse.quote(text)
    whatsapp_url = f"https://wa.me/{whatsapp_number}?text={encoded_text}"

    return redirect(whatsapp_url)

# ===============================
# PRIVATE ROUTES
# ===============================

# @app.route('/dashboard')
# @auth_required
# def dashboard():
#     # Cek lagi, pastikan user masih ada di session
#     if 'user' not in session:
#         return redirect(url_for('login'))

#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

#     # Total provinsi
#     cursor.execute("SELECT COUNT(*) AS total_provinces FROM provinces WHERE is_enabled=1")
#     total_provinces = cursor.fetchone()['total_provinces']

#     # Total regions (kota + kabupaten)
#     cursor.execute("SELECT COUNT(*) AS total_regions FROM regions WHERE is_enabled=1")
#     total_regions = cursor.fetchone()['total_regions']

#     # Total kota
#     cursor.execute("SELECT COUNT(*) AS total_kota FROM regions WHERE type='Kota' AND is_enabled=1")
#     total_kota = cursor.fetchone()['total_kota']

#     # Total kabupaten
#     cursor.execute("SELECT COUNT(*) AS total_kabupaten FROM regions WHERE type='Kabupaten' AND is_enabled=1")
#     total_kabupaten = cursor.fetchone()['total_kabupaten']

#     cursor.close()

#     return render_template(
#         'home.html',
#         user=session.get('user'),
#         total_provinces=total_provinces,
#         total_regions=total_regions,
#         total_kota=total_kota,
#         total_kabupaten=total_kabupaten
#     )
@app.route('/dashboard')
@auth_required
def dashboard():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Hitung statistik
    cur.execute("SELECT COUNT(*) AS total FROM provinces")
    total_provinces = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) AS total FROM regions")
    total_regions = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) AS total FROM regions WHERE type = 'Kota'")
    total_kota = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) AS total FROM regions WHERE type = 'Kabupaten'")
    total_kabupaten = cur.fetchone()['total']

    # Ambil semua region dengan koordinat
    cur.execute("SELECT id, name, type, latitude, longitude FROM regions WHERE latitude IS NOT NULL AND longitude IS NOT NULL")
    regions = cur.fetchall()
    cur.close()

    return render_template(
        'home.html',
        total_provinces=total_provinces,
        total_regions=total_regions,
        total_kota=total_kota,
        total_kabupaten=total_kabupaten,
        regions=regions
    )


# ===============================
# RUN
# ===============================
if __name__ == '__main__':
    app.run(debug=True, port=5001)
