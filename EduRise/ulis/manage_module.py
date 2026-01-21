#!/usr/bin/env python
"""
ULIS Prediction Module Management Script
Handles deployment, testing, and configuration
"""

import os
import sys
import json
import subprocess
from pathlib import Path


class ULISManager:
    """Manager for ULIS prediction module"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.config_file = self.base_dir / "config.json"
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from config.json"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def check_dependencies(self):
        """Check if all required packages are installed"""
        print("🔍 Checking dependencies...")
        
        required_packages = ['django', 'requests']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"  ✅ {package} installed")
            except ImportError:
                print(f"  ❌ {package} NOT installed")
                missing_packages.append(package)
        
        if missing_packages:
            print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
            print(f"   Install with: pip install {' '.join(missing_packages)}")
            return False
        
        print("\n✅ All dependencies installed!")
        return True
    
    def check_files(self):
        """Check if all required files exist"""
        print("\n📁 Checking required files...")
        
        required_files = [
            'forms.py',
            'views.py',
            'ml_predictor.py',
            'urls.py',
            'models.py',
            'admin.py',
            'apps.py',
            '__init__.py',
            'README.md',
            'HUGGINGFACE_INTEGRATION.md',
            'config.json',
            'test_ulis_prediction.py',
        ]
        
        missing_files = []
        for filename in required_files:
            filepath = self.base_dir / filename
            if filepath.exists():
                print(f"  ✅ {filename}")
            else:
                print(f"  ❌ {filename} MISSING")
                missing_files.append(filename)
        
        if missing_files:
            print(f"\n⚠️  Missing files: {', '.join(missing_files)}")
            return False
        
        print("\n✅ All required files present!")
        return True
    
    def check_template(self):
        """Check if template file exists"""
        print("\n🎨 Checking template...")
        
        template_path = self.base_dir.parent / "templates" / "ulis" / "ulis.html"
        if template_path.exists():
            print(f"  ✅ Template found: {template_path.relative_to(self.base_dir.parent.parent)}")
            return True
        else:
            print(f"  ❌ Template NOT found at: {template_path}")
            return False
    
    def test_syntax(self):
        """Test Python syntax of all module files"""
        print("\n🧪 Checking Python syntax...")
        
        python_files = [
            'forms.py',
            'views.py',
            'ml_predictor.py',
            'urls.py',
            'models.py',
            'admin.py',
            'test_ulis_prediction.py',
        ]
        
        all_ok = True
        for filename in python_files:
            filepath = self.base_dir / filename
            if filepath.exists():
                try:
                    compile(open(filepath).read(), filepath, 'exec')
                    print(f"  ✅ {filename} - OK")
                except SyntaxError as e:
                    print(f"  ❌ {filename} - SYNTAX ERROR: {e}")
                    all_ok = False
            else:
                print(f"  ⚠️  {filename} - NOT FOUND")
        
        if all_ok:
            print("\n✅ All Python files have valid syntax!")
        else:
            print("\n❌ Some files have syntax errors!")
        
        return all_ok
    
    def display_config(self):
        """Display module configuration"""
        print("\n⚙️  Module Configuration:")
        print(f"  App Name: {self.config.get('app_name', 'N/A')}")
        print(f"  Version: {self.config.get('version', 'N/A')}")
        print(f"  Description: {self.config.get('description', 'N/A')}")
        
        if 'huggingface_config' in self.config:
            hf = self.config['huggingface_config']
            print(f"\n🤗 HuggingFace Configuration:")
            print(f"  Space URL: {hf.get('space_url', 'N/A')}")
            print(f"  Endpoint: {hf.get('endpoint', 'N/A')}")
            print(f"  Timeout: {hf.get('timeout_seconds', 'N/A')} seconds")
    
    def test_huggingface_connection(self):
        """Test connection to HuggingFace Space"""
        print("\n🔗 Testing HuggingFace connection...")
        
        try:
            import requests
        except ImportError:
            print("  ❌ 'requests' package not installed")
            return False
        
        hf_config = self.config.get('huggingface_config', {})
        space_url = hf_config.get('space_url')
        
        if not space_url:
            print("  ❌ HuggingFace Space URL not configured")
            return False
        
        try:
            response = requests.head(space_url, timeout=5)
            if response.status_code < 400:
                print(f"  ✅ Space is accessible ({response.status_code})")
                return True
            else:
                print(f"  ❌ Space returned error ({response.status_code})")
                return False
        except requests.exceptions.Timeout:
            print("  ⚠️  Connection timeout")
            return False
        except requests.exceptions.ConnectionError:
            print("  ❌ Cannot connect to Space")
            return False
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return False
    
    def run_full_check(self):
        """Run all checks"""
        print("=" * 50)
        print("🚀 ULIS Prediction Module Health Check")
        print("=" * 50)
        
        results = {
            "dependencies": self.check_dependencies(),
            "files": self.check_files(),
            "template": self.check_template(),
            "syntax": self.test_syntax(),
        }
        
        self.display_config()
        
        print("\n" + "=" * 50)
        print("📊 Summary")
        print("=" * 50)
        
        for check, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {check.capitalize()}: {status}")
        
        all_passed = all(results.values())
        
        if all_passed:
            print("\n🎉 All checks passed! Module is ready to deploy.")
            print("\nOptional: Test HuggingFace connection?")
            print("  Run: python manage.py shell")
            print("  Then: from ulis.ml_predictor import send_prediction_request")
        else:
            print("\n⚠️  Some checks failed. Please review and fix issues above.")
        
        return all_passed
    
    def print_info(self):
        """Print module information"""
        print("=" * 50)
        print("ℹ️  ULIS Prediction Module Information")
        print("=" * 50)
        
        self.display_config()
        
        print("\n📋 Components:")
        if 'components' in self.config:
            for component, details in self.config['components'].items():
                print(f"  • {component.capitalize()}: {details.get('file', 'N/A')}")
        
        print("\n🎯 Features:")
        if 'features' in self.config:
            for feature, enabled in self.config['features'].items():
                status = "✅" if enabled else "❌"
                print(f"  {status} {feature.replace('_', ' ').capitalize()}")
        
        print("\n📚 Documentation:")
        if 'documentation' in self.config:
            for doc_type, filename in self.config['documentation'].items():
                filepath = self.base_dir / filename
                if filepath.exists():
                    print(f"  ✅ {doc_type.replace('_', ' ').capitalize()}: {filename}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ULIS Prediction Module Manager')
    parser.add_argument('--check', action='store_true', help='Run health check')
    parser.add_argument('--info', action='store_true', help='Display module information')
    parser.add_argument('--test-hf', action='store_true', help='Test HuggingFace connection')
    
    args = parser.parse_args()
    
    manager = ULISManager()
    
    if args.check:
        manager.run_full_check()
    elif args.info:
        manager.print_info()
    elif args.test_hf:
        manager.test_huggingface_connection()
    else:
        manager.run_full_check()


if __name__ == '__main__':
    main()
 
