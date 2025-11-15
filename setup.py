"""
Test Tool Platform - Setup Script

This script helps set up the development environment.
"""
import subprocess
import sys
import os


def run_command(command, description):
    """Run a shell command and print status."""
    print(f"\n{'='*60}")
    print(f"  {description}")
    print('='*60)
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed")
        if e.stderr:
            print(e.stderr)
        return False


def main():
    """Main setup function."""
    print("\n" + "="*60)
    print("  Test Tool Platform - Development Setup")
    print("="*60)
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("✗ Python 3.11 or higher is required")
        sys.exit(1)
    
    print(f"✓ Python version: {sys.version}")
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("\n⚠ .env file not found. Creating from .env.example...")
        try:
            with open('.env.example', 'r') as src:
                with open('.env', 'w') as dst:
                    dst.write(src.read())
            print("✓ .env file created")
            print("  Please edit .env with your database credentials")
        except Exception as e:
            print(f"✗ Failed to create .env: {e}")
    
    # Install dependencies
    if not run_command(
        "pip install -r requirements.txt",
        "Installing dependencies"
    ):
        sys.exit(1)
    
    # Run tests
    run_command(
        "pytest tests/ -v",
        "Running tests"
    )
    
    print("\n" + "="*60)
    print("  Setup Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Edit .env with your database credentials")
    print("2. Create database: CREATE DATABASE testtool_db;")
    print("3. Run migrations: alembic upgrade head")
    print("4. Start server: python app/main.py")
    print("\nAccess the application at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/api/docs")


if __name__ == "__main__":
    main()
