#!/usr/bin/env python3
"""Test Gemini API models"""
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

try:
    # List available models
    print("📋 Available Gemini Models:\n")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"  ✅ {m.name}")
            print(f"     Display: {m.display_name}")
            print(f"     Description: {m.description[:100] if m.description else 'N/A'}...")
            print()
            
    # Test with gemini-pro
    print("\n🧪 Testing gemini-pro:")
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Say hello")
        print(f"  ✅ Works! Response: {response.text[:50]}")
    except Exception as e:
        print(f"  ❌ Failed: {e}")
    
    # Test with gemini-1.5-flash
    print("\n🧪 Testing gemini-1.5-flash:")
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Say hello")
        print(f"  ✅ Works! Response: {response.text[:50]}")
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        
except Exception as e:
    print(f"❌ Error: {e}")
