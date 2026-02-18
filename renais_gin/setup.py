#!/usr/bin/env python
"""
Quick setup script for Renais Gin platform.
Run this after installing requirements to set up the database and initial data.
"""

import os
import sys
import subprocess


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'=' * 60}")
    print(f"  {description}")
    print(f"{'=' * 60}")
    try:
        subprocess.run(command, check=True, shell=True)
        print(f"✓ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} - FAILED")
        print(f"Error: {e}")
        return False


def main():
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║            RENAIS GIN PLATFORM SETUP                  ║
    ║        Craft Your Perfect World - Setup Tool         ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """)

    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("ERROR: manage.py not found!")
        print("Please run this script from the renais_gin directory")
        sys.exit(1)

    # Create necessary directories
    print("\n[1/8] Creating required directories...")
    directories = [
        'media/qr_codes',
        'media/pdfs/user_uploads',
        'media/pdfs/generated_reports',
        'staticfiles',
        'logs'
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✓ Created: {directory}")

    # Run migrations
    if not run_command('python manage.py makemigrations', '[2/8] Creating migrations'):
        sys.exit(1)

    if not run_command('python manage.py migrate', '[3/8] Running migrations'):
        sys.exit(1)

    # Collect static files
    if not run_command('python manage.py collectstatic --noinput', '[4/8] Collecting static files'):
        print("  (This is optional - continuing...)")

    # Initialize ecosystem
    if not run_command('python manage.py initialize_ecosystem', '[5/8] Initializing ecosystem'):
        print("  (This is optional - continuing...)")

    # Create demo user
    print("\n[6/8] Creating demo user...")
    print("  Username: demo")
    print("  Password: demo123")
    if not run_command('python manage.py create_demo_user', 'Creating demo user'):
        print("  (This is optional - continuing...)")

    # Add test bottles
    print("\n[7/8] Adding test bottles...")
    if not run_command('python manage.py add_test_bottles --count 20', 'Adding test bottles'):
        print("  (This is optional - continuing...)")

    # Final message
    print(f"\n{'=' * 60}")
    print("  [8/8] Setup Complete!")
    print(f"{'=' * 60}")

    print("""
    ✓ Setup completed successfully!

    📋 Next Steps:

    1. Start the development server:
       python manage.py runserver

    2. Access the platform:
       - Main site: http://127.0.0.1:8000/
       - Admin panel: http://127.0.0.1:8000/admin/

    3. Login credentials:
       Admin:
         Username: admin
         Password: adminpassword

       Demo User:
         Username: demo
         Password: demo123

    📚 Documentation:
       - README.md - Project overview
       - DEPLOYMENT.md - Deployment guide
       - DEVELOPMENT.md - Development guide

    🎉 Ready to craft a better world!
    """)


if __name__ == '__main__':
    main()
