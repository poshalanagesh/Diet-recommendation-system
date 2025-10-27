import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import joblib

# Sample data for diabetes diet recommendation
def create_sample_data():
    # Create sample data (in a real application, this would be real patient data)
    np.random.seed(42)
    n_samples = 1000
    
    # Generate features
    glucose_levels = np.random.normal(140, 30, n_samples)  # Blood glucose levels
    bmi = np.random.normal(28, 5, n_samples)  # BMI
    age = np.random.normal(50, 15, n_samples)  # Age
    physical_activity = np.random.normal(3, 1, n_samples)  # Hours per week
    
    # Create diet categories based on features
    diets = []
    for i in range(n_samples):
        if glucose_levels[i] > 160 and bmi[i] > 30:
            diets.append('low_carb_diet')
        elif glucose_levels[i] > 140 and bmi[i] > 25:
            diets.append('mediterranean_diet')
        elif physical_activity[i] > 4:
            diets.append('balanced_diet')
        else:
            diets.append('dash_diet')
    
    # Create DataFrame
    data = pd.DataFrame({
        'glucose_level': glucose_levels,
        'bmi': bmi,
        'age': age,
        'physical_activity': physical_activity,
        'recommended_diet': diets
    })
    
    return data

def train_model():
    # Get sample data
    data = create_sample_data()
    
    # Prepare features and target
    X = data[['glucose_level', 'bmi', 'age', 'physical_activity']]
    y = data['recommended_diet']
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_scaled, y)
    
    # Save model and scaler
    joblib.dump(model, 'diet_model.joblib')
    joblib.dump(scaler, 'scaler.joblib')

def get_diet_recommendation(glucose_level, bmi, age, physical_activity):
    try:
        print("Loading model and scaler...")  # Debug print
        # Load model and scaler
        model = joblib.load('diet_model.joblib')
        scaler = joblib.load('scaler.joblib')
        
        print("Preparing input data...")  # Debug print
        # Prepare input data
        input_data = np.array([[glucose_level, bmi, age, physical_activity]])
        print("Input data shape:", input_data.shape)  # Debug print
        print("Input data values:", input_data)  # Debug print
        
        input_scaled = scaler.transform(input_data)
        print("Scaled input data:", input_scaled)  # Debug print
        
        print("Making prediction...")  # Debug print
        # Get prediction
        diet = model.predict(input_scaled)[0]
        print("Raw predicted diet:", diet)  # Debug print
        
        # Diet descriptions
        diet_descriptions = {
            'low_carb_diet': {
                'description': 'A diet low in carbohydrates, focusing on proteins and healthy fats.',
                'recommendations': [
                    'Lean meats and fish',
                    'Green leafy vegetables',
                    'Nuts and seeds',
                    'Limit bread and pasta',
                    'Avoid sugary foods'
                ]
            },
            'mediterranean_diet': {
                'description': 'A diet based on traditional Mediterranean cuisine.',
                'recommendations': [
                    'Olive oil as main fat source',
                    'Plenty of vegetables and fruits',
                    'Whole grains',
                    'Fish and seafood',
                    'Limited red meat'
                ]
            },
            'balanced_diet': {
                'description': 'A well-balanced diet with all food groups.',
                'recommendations': [
                    'Varied fruits and vegetables',
                    'Whole grain products',
                    'Lean proteins',
                    'Low-fat dairy',
                    'Moderate portions'
                ]
            },
            'dash_diet': {
                'description': 'Dietary Approaches to Stop Hypertension diet.',
                'recommendations': [
                    'Rich in fruits and vegetables',
                    'Low-fat dairy products',
                    'Whole grains',
                    'Lean meats',
                    'Reduce sodium intake'
                ]
            }
        }
        
        print("Looking up diet description for:", diet)  # Debug print
        if diet not in diet_descriptions:
            print("WARNING: Diet type not found in descriptions:", diet)
            diet = 'balanced_diet'  # Default to balanced diet
            print("Using default diet type:", diet)
        
        # Create response with all required fields
        response = {
            'diet_type': diet,
            'description': diet_descriptions[diet]['description'],
            'recommendations': diet_descriptions[diet]['recommendations']
        }
        
        print("Final response:", response)  # Debug print
        return response
        
    except Exception as e:
        print("Error in get_diet_recommendation:", str(e))  # Debug print
        import traceback
        print("Traceback:", traceback.format_exc())  # Debug print
        raise

def predict_from_dataset(file_path):
    """
    Predict diet recommendations for multiple entries from a CSV/Excel file
    Expected columns: glucose_level, bmi, age, physical_activity
    """
    try:
        # Try reading as CSV first
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        # Try reading as Excel if not CSV
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format. Please upload CSV or Excel file.")
        
        required_columns = ['glucose_level', 'bmi', 'age', 'physical_activity']
        
        # Check if all required columns are present
        if not all(col in df.columns for col in required_columns):
            missing_cols = [col for col in required_columns if col not in df.columns]
            raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")
        
        # Load model and scaler
        model = joblib.load('diet_model.joblib')
        scaler = joblib.load('scaler.joblib')
        
        # Prepare input data
        X = df[required_columns]
        X_scaled = scaler.transform(X)
        
        # Get predictions
        predictions = model.predict(X_scaled)
        
        # Diet descriptions
        diet_descriptions = {
            'low_carb_diet': {
                'description': 'A diet low in carbohydrates, focusing on proteins and healthy fats.',
                'recommendations': [
                    'Lean meats and fish',
                    'Green leafy vegetables',
                    'Nuts and seeds',
                    'Limit bread and pasta',
                    'Avoid sugary foods'
                ]
            },
            'mediterranean_diet': {
                'description': 'A diet based on traditional Mediterranean cuisine.',
                'recommendations': [
                    'Olive oil as main fat source',
                    'Plenty of vegetables and fruits',
                    'Whole grains',
                    'Fish and seafood',
                    'Limited red meat'
                ]
            },
            'balanced_diet': {
                'description': 'A well-balanced diet with all food groups.',
                'recommendations': [
                    'Varied fruits and vegetables',
                    'Whole grain products',
                    'Lean proteins',
                    'Low-fat dairy',
                    'Moderate portions'
                ]
            },
            'dash_diet': {
                'description': 'Dietary Approaches to Stop Hypertension diet.',
                'recommendations': [
                    'Rich in fruits and vegetables',
                    'Low-fat dairy products',
                    'Whole grains',
                    'Lean meats',
                    'Reduce sodium intake'
                ]
            }
        }
        
        # Create results DataFrame
        results_df = df.copy()
        results_df['recommended_diet'] = predictions
        results_df['diet_description'] = [diet_descriptions[diet]['description'] for diet in predictions]
        results_df['diet_recommendations'] = [', '.join(diet_descriptions[diet]['recommendations']) for diet in predictions]
        
        return {
            'success': True,
            'predictions': results_df.to_dict('records')
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

if __name__ == '__main__':
    train_model() 