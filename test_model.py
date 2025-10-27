from model import get_diet_recommendation

def test_recommendation():
    # Test case
    test_input = {
        'glucose_level': 140,
        'bmi': 25,
        'age': 45,
        'physical_activity': 3
    }
    
    try:
        result = get_diet_recommendation(**test_input)
        print("Test Result:", result)
        print("\nKeys in result:", list(result.keys()))
        return result
    except Exception as e:
        print("Error:", str(e))
        return None

if __name__ == "__main__":
    test_recommendation() 