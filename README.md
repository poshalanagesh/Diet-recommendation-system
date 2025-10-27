# Diabetes Diet Recommendation System

A machine learning-based web application that provides personalized diet recommendations for people with diabetes based on their health metrics.

## Features

- Predicts suitable diet plans based on:
  - Blood glucose levels
  - BMI (Body Mass Index)
  - Age
  - Physical activity level
- Provides detailed diet recommendations
- Simple and user-friendly web interface
- Real-time predictions

## Diet Types

The system recommends one of the following diet types:
1. Low Carb Diet
2. Mediterranean Diet
3. Balanced Diet
4. DASH Diet

## Setup Instructions

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your web browser and navigate to:
```
http://localhost:5000
```

## How to Use

1. Enter your health metrics in the form:
   - Blood Glucose Level (mg/dL)
   - BMI
   - Age
   - Physical Activity (hours per week)
2. Click "Get Recommendation"
3. View your personalized diet recommendation

## Technical Details

- Built with Python Flask
- Uses scikit-learn for machine learning
- Frontend built with Bootstrap 5
- Responsive design for mobile and desktop

## Note

This is a simplified model for demonstration purposes. For actual medical advice, please consult with healthcare professionals. 