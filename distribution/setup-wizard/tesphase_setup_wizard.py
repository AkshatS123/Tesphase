#!/usr/bin/env python3
"""
TESPHASE SETUP WIZARD
Smart Solar + Tesla Charging System
Automated Configuration Tool for Friends & Neighbors
"""

import json
import os
import sys
import urllib.request
import urllib.parse
import base64
import webbrowser
from pathlib import Path
import requests
from datetime import datetime

class TesphaseSetupWizard:
    def __init__(self):
        self.config = {}
        self.setup_dir = Path.cwd()
        self.production_dir = self.setup_dir.parent / "production"
        
    def print_banner(self):
        print("=" * 60)
        print("🌞⚡ TESPHASE SETUP WIZARD ⚡🌞")
        print("Smart Solar + Tesla Charging System")
        print("Automated Setup for Friends & Neighbors")
        print("=" * 60)
        print()
        
    def print_step(self, step, title):
        print(f"\n{'='*50}")
        print(f"STEP {step}: {title}")
        print(f"{'='*50}")
        
    def validate_email(self, email):
        """Basic email validation"""
        return "@" in email and "." in email.split("@")[1]
        
    def test_enphase_connection(self, api_key, system_id):
        """Test Enphase API connection"""
        try:
            url = f"https://api.enphaseenergy.com/api/v4/systems/{system_id}/summary"
            params = {"key": api_key}
            
            complete_url = url + "?" + "&".join(f"{k}={v}" for k, v in params.items())
            request = urllib.request.Request(complete_url)
            
            with urllib.request.urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode())
                if 'system_id' in data:
                    print(f"✅ Enphase connection successful! System: {data.get('name', 'Unknown')}")
                    return True
        except Exception as e:
            print(f"❌ Enphase connection failed: {e}")
            return False
            
    def setup_enphase_api(self):
        """Step 1: Configure Enphase Solar API"""
        self.print_step(1, "ENPHASE SOLAR API SETUP")
        
        print("We need to connect to your Enphase solar system.")
        print("This requires an Enphase Developer account (free).")
        print()
        
        # Check if user already has API key
        has_api_key = input("Do you already have an Enphase API key? (y/n): ").lower().strip()
        
        if has_api_key != 'y':
            print("\n📋 GETTING YOUR ENPHASE API KEY:")
            print("1. Go to: https://developer.enphase.com/")
            print("2. Create a free developer account")
            print("3. Register a new application:")
            print("   - Name: Tesphase Solar Charging")
            print("   - Description: Smart solar + Tesla charging")
            print("4. Get your API key from the application details")
            print()
            
            open_browser = input("Open Enphase developer site now? (y/n): ").lower().strip()
            if open_browser == 'y':
                webbrowser.open("https://developer.enphase.com/")
                
            input("\nPress Enter when you have your API key...")
            
        # Get API credentials
        while True:
            api_key = input("\nEnter your Enphase API key: ").strip()
            if not api_key:
                print("❌ API key cannot be empty")
                continue
                
            system_id = input("Enter your Enphase System ID: ").strip()
            if not system_id:
                print("❌ System ID cannot be empty") 
                continue
                
            print("\n🧪 Testing Enphase connection...")
            if self.test_enphase_connection(api_key, system_id):
                self.config['enphase'] = {
                    'api_key': api_key,
                    'system_id': system_id
                }
                break
            else:
                retry = input("\nWould you like to try again? (y/n): ").lower().strip()
                if retry != 'y':
                    print("❌ Cannot proceed without valid Enphase credentials")
                    sys.exit(1)
                    
    def setup_tesla_api(self):
        """Step 2: Configure Tesla Fleet API"""
        self.print_step(2, "TESLA FLEET API SETUP")
        
        print("Setting up Tesla Fleet API for vehicle control.")
        print("This requires a Tesla Developer account (free).")
        print()
        
        # Check if user has Tesla developer account
        has_tesla_account = input("Do you have a Tesla Developer account? (y/n): ").lower().strip()
        
        if has_tesla_account != 'y':
            print("\n📋 CREATING TESLA DEVELOPER ACCOUNT:")
            print("1. Go to: https://developer.tesla.com/")
            print("2. Create a business developer account (free)")
            print("3. Register a new application:")
            print("   - Name: Tesphase Smart Charging")
            print("   - Description: Solar-powered smart charging system")
            print("   - Domain: We'll help you set this up...")
            print()
            
            open_browser = input("Open Tesla developer site now? (y/n): ").lower().strip()
            if open_browser == 'y':
                webbrowser.open("https://developer.tesla.com/")
                
            input("\nPress Enter when you have created your Tesla developer account...")
            
        # Get Tesla credentials
        print("\n🔑 TESLA APPLICATION CREDENTIALS:")
        print("From your Tesla developer dashboard, get your:")
        
        client_id = input("Tesla Client ID: ").strip()
        client_secret = input("Tesla Client Secret: ").strip()
        
        if not client_id or not client_secret:
            print("❌ Tesla credentials required to proceed")
            sys.exit(1)
            
        # Domain setup
        print("\n🌐 DOMAIN SETUP FOR TESLA:")
        print("Tesla requires a verified domain for OAuth callbacks.")
        print("We can help you set up a free subdomain or use GitHub Pages.")
        print()
        
        domain_choice = input("Choose: (1) Use existing domain (2) Setup GitHub Pages (3) Manual setup: ").strip()
        
        if domain_choice == "1":
            domain = input("Enter your domain (e.g., mydomain.com): ").strip()
        elif domain_choice == "2":
            github_username = input("Enter your GitHub username: ").strip()
            domain = f"{github_username.lower()}.github.io"
            print(f"✅ Your domain will be: {domain}")
            print(f"📋 TODO: Create repository named '{github_username}.github.io' on GitHub")
        else:
            domain = input("Enter your domain: ").strip()
            
        self.config['tesla'] = {
            'client_id': client_id,
            'client_secret': client_secret,
            'domain': domain,
            'redirect_uri': f"https://{domain}/tesphase/callback"
        }
        
        print(f"✅ Tesla configuration saved!")
        print(f"📋 Remember to add redirect URI: {self.config['tesla']['redirect_uri']}")
        
    def setup_email_notifications(self):
        """Step 3: Configure Email Notifications"""
        self.print_step(3, "EMAIL NOTIFICATIONS")
        
        print("Configure email alerts for system status and charging updates.")
        print()
        
        while True:
            email = input("Enter your email address for notifications: ").strip()
            if self.validate_email(email):
                break
            print("❌ Please enter a valid email address")
            
        # Email service setup
        print("\n📧 EMAIL SERVICE SETUP:")
        print("For Gmail, you'll need an 'App Password' (not your regular password)")
        print("1. Go to Google Account settings")
        print("2. Security → 2-Step Verification → App passwords")
        print("3. Generate app password for 'Mail'")
        print()
        
        setup_email = input("Setup email service now? (y/n): ").lower().strip()
        
        if setup_email == 'y':
            sender_email = input("Gmail address for sending alerts: ").strip()
            sender_password = input("Gmail app password: ").strip()
            
            self.config['email'] = {
                'sender_email': sender_email,
                'sender_password': sender_password,
                'receiver_email': email,
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 465
            }
        else:
            self.config['email'] = {
                'receiver_email': email,
                'enabled': False
            }
            
    def setup_vehicle_preferences(self):
        """Step 4: Vehicle Charging Preferences"""
        self.print_step(4, "VEHICLE CHARGING PREFERENCES")
        
        print("Configure your Tesla charging preferences.")
        print()
        
        # Basic preferences
        max_charge_amps = input("Maximum charging amps (default 25A): ").strip() or "25"
        min_battery = input("Minimum battery % before charging (default 20%): ").strip() or "20"
        max_battery = input("Maximum battery % to charge to (default 90%): ").strip() or "90"
        
        # Blackout hours
        enable_blackout = input("Enable blackout hours protection? (y/n): ").lower().strip() == 'y'
        
        blackout_start = "16:00"
        blackout_end = "21:00"
        
        if enable_blackout:
            blackout_start = input("Blackout start time (default 16:00): ").strip() or "16:00"
            blackout_end = input("Blackout end time (default 21:00): ").strip() or "21:00"
            
        self.config['charging'] = {
            'max_amps': int(max_charge_amps),
            'min_battery': int(min_battery),
            'max_battery': int(max_battery),
            'blackout_protection': enable_blackout,
            'blackout_start': blackout_start,
            'blackout_end': blackout_end
        }
        
    def generate_configuration_files(self):
        """Step 5: Generate Configuration Files"""
        self.print_step(5, "GENERATING CONFIGURATION")
        
        print("Creating configuration files...")
        
        # Create tokens.json template
        tokens_config = {
            "access_tokenEnphase": "WILL_BE_SET_DURING_FIRST_RUN",
            "refresh_tokenEnphase": "WILL_BE_SET_DURING_FIRST_RUN",
            "tesla_access_token": "WILL_BE_SET_DURING_OAUTH",
            "tesla_refresh_token": "WILL_BE_SET_DURING_OAUTH",
            "enphase_api_key": self.config['enphase']['api_key'],
            "enphase_system_id": self.config['enphase']['system_id'],
            "tesla_client_id": self.config['tesla']['client_id'],
            "tesla_client_secret": self.config['tesla']['client_secret']
        }
        
        # Create tesphase_config.json
        tesphase_config = {
            "setup_date": datetime.now().isoformat(),
            "version": "1.0",
            "enphase": self.config['enphase'],
            "tesla": self.config['tesla'],
            "email": self.config['email'],
            "charging": self.config['charging']
        }
        
        # Save configuration files
        config_dir = self.setup_dir / "config"
        config_dir.mkdir(exist_ok=True)
        
        with open(config_dir / "tokens.json", "w") as f:
            json.dump(tokens_config, f, indent=4)
            
        with open(config_dir / "tesphase_config.json", "w") as f:
            json.dump(tesphase_config, f, indent=4)
            
        print("✅ Configuration files created!")
        print(f"📁 Saved to: {config_dir}")
        
    def generate_startup_script(self):
        """Generate easy startup script"""
        print("\n🚀 Creating startup script...")
        
        startup_script = '''#!/usr/bin/env python3
"""
TESPHASE SMART CHARGING SYSTEM
Auto-generated startup script
"""

import sys
import os
from pathlib import Path

# Add production directory to path
production_dir = Path(__file__).parent.parent / "production"
sys.path.insert(0, str(production_dir))

# Copy configuration to production directory
import shutil
config_dir = Path(__file__).parent / "config"
prod_tokens = production_dir / "tokens.json"

if not prod_tokens.exists():
    shutil.copy2(config_dir / "tokens.json", prod_tokens)
    print("✅ Configuration copied to production")

# Start the main application
os.chdir(production_dir)
from tesphase_multi_vehicle import main

if __name__ == "__main__":
    print("🌞⚡ STARTING TESPHASE SMART CHARGING SYSTEM ⚡🌞")
    print(f"Production directory: {production_dir}")
    print("=" * 60)
    
    try:
        # Run the main loop
        while True:
            main()
    except KeyboardInterrupt:
        print("\\n👋 Tesphase stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        input("Press Enter to exit...")
'''

        with open(self.setup_dir / "start_tesphase.py", "w") as f:
            f.write(startup_script)
            
        print("✅ Startup script created: start_tesphase.py")
        
    def print_next_steps(self):
        """Display next steps for user"""
        self.print_step(6, "NEXT STEPS")
        
        print("🎉 SETUP COMPLETE! Here's what to do next:")
        print()
        print("1. 📋 TESLA OAUTH SETUP:")
        print(f"   - Add this redirect URI to your Tesla app:")
        print(f"     {self.config['tesla']['redirect_uri']}")
        print(f"   - Verify your domain: {self.config['tesla']['domain']}")
        print()
        
        if 'github_username' in locals():
            print("2. 🌐 GITHUB PAGES SETUP:")
            print("   - Create repository: {github_username}.github.io")
            print("   - Enable GitHub Pages in repository settings")
            print()
            
        print("3. 🔑 ENPHASE OAUTH:")
        print("   - Run the system once to complete Enphase OAuth")
        print("   - Follow the browser prompts for authorization")
        print()
        
        print("4. 🚗 TESLA AUTHORIZATION:")
        print("   - Use Tesla app to scan QR code for vehicle access")
        print("   - Complete OAuth flow in browser")
        print()
        
        print("5. 🚀 START SYSTEM:")
        print("   python start_tesphase.py")
        print()
        
        print("📧 SUPPORT:")
        print("   Email: s.akshat@gmail.com")
        print("   Docs: /docs/ folder")
        print()
        
        print("💰 ESTIMATED COSTS:")
        print("   - Setup: Free (except optional domain ~$10/year)")
        print("   - Monthly: <$10 (API costs)")
        print("   - Savings: $50-200/month (optimized charging)")
        print()
        
    def run_setup(self):
        """Run the complete setup wizard"""
        try:
            self.print_banner()
            
            print("This wizard will configure Tesphase for your home:")
            print("• ☀️ Enphase Solar API connection")
            print("• 🚗 Tesla Fleet API integration")
            print("• 📧 Email notifications")
            print("• ⚡ Charging preferences")
            print("• 🚀 Ready-to-run system")
            print()
            
            proceed = input("Ready to start setup? (y/n): ").lower().strip()
            if proceed != 'y':
                print("Setup cancelled.")
                return
                
            self.setup_enphase_api()
            self.setup_tesla_api()
            self.setup_email_notifications()
            self.setup_vehicle_preferences()
            self.generate_configuration_files()
            self.generate_startup_script()
            self.print_next_steps()
            
            print("🎉 TESPHASE SETUP WIZARD COMPLETE!")
            
        except KeyboardInterrupt:
            print("\n\n❌ Setup cancelled by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Setup failed: {e}")
            print("Please contact support: s.akshat@gmail.com")
            sys.exit(1)

if __name__ == "__main__":
    wizard = TesphaseSetupWizard()
    wizard.run_setup()