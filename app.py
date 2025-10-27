from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_cors import CORS
from model import train_model, get_diet_recommendation, predict_from_dataset
from models import db, User, DietPrediction
import os
from werkzeug.utils import secure_filename
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = '391490'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diet_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Create database tables
with app.app_context():
    db.create_all()
    # Create admin user if not exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@example.com', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

# Train the model when the app starts
if not os.path.exists('diet_model.joblib'):
    train_model()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard' if not user.is_admin else 'admin_dashboard'))
        
        flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    predictions = DietPrediction.query.filter_by(user_id=current_user.id).order_by(DietPrediction.prediction_date.desc()).all()
    return render_template('dashboard.html', predictions=predictions)

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    users = User.query.filter_by(is_admin=False).all()
    predictions = DietPrediction.query.order_by(DietPrediction.prediction_date.desc()).all()
    return render_template('admin_dashboard.html', users=users, predictions=predictions)

@app.route('/predict', methods=['POST'])
def predict():  # Temporarily removed @login_required
    try:
        data = request.json
        logger.debug("Received data: %s", data)
        
        if not data:
            logger.error("No JSON data received")
            return jsonify({'error': 'No data received'}), 400
        
        required_fields = ['glucose_level', 'bmi', 'age', 'physical_activity']
        for field in required_fields:
            if field not in data:
                logger.error("Missing required field: %s", field)
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        glucose_level = float(data['glucose_level'])
        bmi = float(data['bmi'])
        age = float(data['age'])
        physical_activity = float(data['physical_activity'])
        
        logger.debug("Making prediction with values: %s", {
            'glucose_level': glucose_level,
            'bmi': bmi,
            'age': age,
            'physical_activity': physical_activity
        })
        
        recommendation = get_diet_recommendation(glucose_level, bmi, age, physical_activity)
        logger.debug("Model recommendation: %s", recommendation)
        
        if not recommendation or 'diet_type' not in recommendation:
            logger.error("Invalid recommendation format: %s", recommendation)
            return jsonify({'error': 'Invalid recommendation format'}), 500
        
        # Save prediction to database if user is logged in
        if current_user.is_authenticated:
            try:
                prediction = DietPrediction(
                    user_id=current_user.id,
                    glucose_level=glucose_level,
                    bmi=bmi,
                    age=age,
                    physical_activity=physical_activity,
                    recommended_diet=recommendation['diet_type']
                )
                db.session.add(prediction)
                db.session.commit()
                logger.debug("Prediction saved to database")
            except Exception as db_error:
                logger.error("Database error: %s", str(db_error))
                db.session.rollback()
                # Continue anyway since the prediction was successful
        
        return jsonify(recommendation)
    except Exception as e:
        logger.error("Error in prediction: %s", str(e))
        import traceback
        logger.error("Traceback: %s", traceback.format_exc())
        return jsonify({'error': str(e)}), 400

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        result = predict_from_dataset(filepath)
        
        if result['success']:
            # Save batch predictions to database
            for pred in result['predictions']:
                prediction = DietPrediction(
                    user_id=current_user.id,
                    glucose_level=pred['glucose_level'],
                    bmi=pred['bmi'],
                    age=pred['age'],
                    physical_activity=pred['physical_activity'],
                    recommended_diet=pred['recommended_diet']
                )
                db.session.add(prediction)
            db.session.commit()
        
        os.remove(filepath)
        return jsonify(result)
    
    return jsonify({'success': False, 'error': 'Invalid file type'})

@app.route('/sample_template')
@login_required
def download_template():
    # Create a sample template file
    df = pd.DataFrame({
        'glucose_level': [140],
        'bmi': [25],
        'age': [45],
        'physical_activity': [3]
    })
    
    template_path = os.path.join(app.config['UPLOAD_FOLDER'], 'template.csv')
    df.to_csv(template_path, index=False)
    
    return send_file(
        template_path,
        as_attachment=True,
        download_name='diet_prediction_template.csv',
        mimetype='text/csv'
    )

if __name__ == '__main__':
    app.run(debug=True) 