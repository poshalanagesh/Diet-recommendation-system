from model import train_model, get_diet_recommendation

def main():
    print("Training model...")
    train_model()
    
    print("\nTesting model with sample data...")
    test_data = {
        'glucose_level': 140,
        'bmi': 25,
        'age': 45,
        'physical_activity': 3
    }
    
    try:
        result = get_diet_recommendation(**test_data)
        print("\nPrediction result:")
        print("Diet type:", result['diet_type'])
        print("Description:", result['description'])
        print("Recommendations:", "\n- " + "\n- ".join(result['recommendations']))
    except Exception as e:
        print("Error testing model:", str(e))

if __name__ == "__main__":
    main() 