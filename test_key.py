import google.generativeai as genai
import os

# --- PASTE YOUR KEY HERE ---
# Make sure there are NO spaces before or after the key inside the quotes.
my_key = "AIzaSyCOIUuyORBe9iCGEZTpf2WZNEnFqF_ZCYc"

os.environ["GEMINI_API_KEY"] = my_key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

print(f"Testing Key: {my_key[:10]}... (hidden)")

try:
    # Try the newer, faster model first
    print("Attempting to connect with 'gemini-1.5-flash'...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Hello, are you working?")
    print("✅ SUCCESS! Response:", response.text)
    
except Exception as e:
    print("\n❌ ERROR with Flash:", e)
    print("Trying 'gemini-pro' instead...")
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Hello?")
        print("✅ SUCCESS with Pro! Response:", response.text)
    except Exception as e2:
        print("\n❌ FATAL ERROR:", e2)
        print("Your API Key might be invalid, or you haven't enabled the API in Google AI Studio.")