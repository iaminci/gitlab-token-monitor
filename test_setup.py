#!/usr/bin/env python3
"""
Test script to verify GitLab Token Monitor setup
"""

import os
import sys

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import requests
        print("✅ requests module available")
    except ImportError:
        print("❌ requests module missing - run: pip install requests")
        return False
    
    required_files = ['config.py', 'gitlab_api.py', 'token_analyzer.py', 'email_reporter.py']
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} found")
        else:
            print(f"❌ {file} missing")
            return False
    
    try:
        from config import Config
        print("✅ config module can be imported")
    except ImportError as e:
        print(f"❌ Cannot import config: {e}")
        return False
        
    try:
        from gitlab_api import GitLabAPI
        print("✅ gitlab_api module can be imported")
    except ImportError as e:
        print(f"❌ Cannot import gitlab_api: {e}")
        return False
        
    return True

def test_environment():
    """Test environment variables"""
    print("\n🔍 Testing environment variables...")
    
    required_vars = {
        'GITLAB_URL': 'GitLab instance URL',
        'GITLAB_ADMIN_TOKEN': 'GitLab admin token',
        'FROM_EMAIL': 'Email sender address'
    }
    
    optional_vars = {
        'TO_EMAILS': 'Email recipients',
        'SMTP_SERVER': 'SMTP server',
        'SMTP_USERNAME': 'SMTP username',
        'SMTP_PASSWORD': 'SMTP password'
    }
    
    all_good = True
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value and value not in ['your-admin-token', 'alerts@yourcompany.com', 'https://your-gitlab.com']:
            print(f"✅ {var}: {description} is set")
        else:
            print(f"❌ {var}: {description} is NOT SET")
            print(f"   Set with: export {var}='your-value'")
            all_good = False
    
    print(f"\n📋 Optional variables:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {description} is set")
        else:
            print(f"⚠️  {var}: {description} is not set (will use defaults)")
    
    return all_good

def test_config_loading():
    """Test config loading"""
    print("\n🔍 Testing config loading...")
    
    try:
        from config import Config
        config = Config()
        print("✅ Config loaded successfully")
        return True
    except SystemExit:
        print("❌ Config validation failed - check environment variables above")
        return False
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 GitLab Token Monitor Setup Test\n")
    
    tests = [
        ("Import Test", test_imports),
        ("Environment Test", test_environment), 
        ("Config Loading Test", test_config_loading)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append(False)
        print()
    
    print("📊 Test Summary:")
    print("=" * 50)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    if all(results):
        print(f"\n🎉 All tests passed! You can run: python main.py")
    else:
        print(f"\n🚨 Some tests failed. Fix the issues above before running main.py")
        
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)