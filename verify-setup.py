#!/usr/bin/env python3
"""
LOUS Setup Verification Script
Checks that all components are properly configured
"""

import os
import sys
import json

def check_mark(condition):
    return "✅" if condition else "❌"

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def check_backend():
    """Check backend setup"""
    print_header("Backend Verification")

    checks = []

    # Check if main.py exists
    main_exists = os.path.exists("backend/main.py")
    checks.append(("main.py exists", main_exists))
    print(f"{check_mark(main_exists)} Backend main.py found")

    # Check requirements.txt
    req_exists = os.path.exists("backend/requirements.txt")
    checks.append(("requirements.txt exists", req_exists))
    print(f"{check_mark(req_exists)} Requirements file found")

    # Check routers
    routers_exist = os.path.exists("backend/routers/auth.py")
    checks.append(("Routers configured", routers_exist))
    print(f"{check_mark(routers_exist)} Authentication router found")

    # Check database module
    db_exists = os.path.exists("backend/db/database.py")
    checks.append(("Database module exists", db_exists))
    print(f"{check_mark(db_exists)} Database module found")

    # Try to import and initialize database
    try:
        sys.path.insert(0, 'backend')
        from db.database import Database
        db = Database()
        checks.append(("Database initialization", True))
        print(f"✅ Database initialized successfully")

        # Check for default users
        admin = db.get_user_by_username("admin")
        if admin:
            print(f"✅ Default admin user found")
            checks.append(("Default users created", True))
        else:
            print(f"❌ Default users not found")
            checks.append(("Default users created", False))

    except Exception as e:
        print(f"❌ Database error: {e}")
        checks.append(("Database initialization", False))
        checks.append(("Default users created", False))

    return all(check[1] for check in checks)

def check_frontend():
    """Check frontend setup"""
    print_header("Frontend Verification")

    checks = []

    # Check package.json
    pkg_exists = os.path.exists("frontend/package.json")
    checks.append(("package.json exists", pkg_exists))
    print(f"{check_mark(pkg_exists)} package.json found")

    # Check vite config
    vite_exists = os.path.exists("frontend/vite.config.js")
    checks.append(("Vite config exists", vite_exists))
    print(f"{check_mark(vite_exists)} Vite configuration found")

    # Check tailwind config
    tailwind_exists = os.path.exists("frontend/tailwind.config.js")
    checks.append(("Tailwind config exists", tailwind_exists))
    print(f"{check_mark(tailwind_exists)} Tailwind configuration found")

    # Check main components
    app_exists = os.path.exists("frontend/src/App.jsx")
    checks.append(("App.jsx exists", app_exists))
    print(f"{check_mark(app_exists)} App.jsx found")

    # Check pages
    login_exists = os.path.exists("frontend/src/pages/LoginPage.jsx")
    dashboard_exists = os.path.exists("frontend/src/pages/Dashboard.jsx")
    checks.append(("Pages exist", login_exists and dashboard_exists))
    print(f"{check_mark(login_exists)} LoginPage.jsx found")
    print(f"{check_mark(dashboard_exists)} Dashboard.jsx found")

    # Check API client
    api_exists = os.path.exists("frontend/src/api/client.js")
    checks.append(("API client exists", api_exists))
    print(f"{check_mark(api_exists)} API client found")

    return all(check[1] for check in checks)

def check_docker():
    """Check Docker configuration"""
    print_header("Docker Configuration")

    checks = []

    # Check Dockerfile
    dockerfile_exists = os.path.exists("Dockerfile")
    checks.append(("Dockerfile exists", dockerfile_exists))
    print(f"{check_mark(dockerfile_exists)} Dockerfile found")

    # Check docker-compose
    compose_exists = os.path.exists("docker-compose.yml")
    checks.append(("docker-compose.yml exists", compose_exists))
    print(f"{check_mark(compose_exists)} docker-compose.yml found")

    return all(check[1] for check in checks)

def check_documentation():
    """Check documentation"""
    print_header("Documentation")

    checks = []

    readme_exists = os.path.exists("README.md")
    checks.append(("README.md exists", readme_exists))
    print(f"{check_mark(readme_exists)} README.md found")

    quickstart_exists = os.path.exists("QUICKSTART.md")
    checks.append(("QUICKSTART.md exists", quickstart_exists))
    print(f"{check_mark(quickstart_exists)} QUICKSTART.md found")

    deployment_exists = os.path.exists("DEPLOYMENT.md")
    checks.append(("DEPLOYMENT.md exists", deployment_exists))
    print(f"{check_mark(deployment_exists)} DEPLOYMENT.md found")

    return all(check[1] for check in checks)

def main():
    print("\n" + "="*60)
    print("  LOUS - Setup Verification")
    print("  AI Automated Loan Origination Underwriting System")
    print("="*60)

    # Change to project directory
    if not os.path.exists("backend") or not os.path.exists("frontend"):
        print("\n❌ Error: Please run this script from the lous directory")
        sys.exit(1)

    results = []

    # Run all checks
    results.append(("Backend", check_backend()))
    results.append(("Frontend", check_frontend()))
    results.append(("Docker", check_docker()))
    results.append(("Documentation", check_documentation()))

    # Print summary
    print_header("Summary")

    all_passed = True
    for component, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{component:20} {status}")
        if not passed:
            all_passed = False

    print("\n" + "="*60)

    if all_passed:
        print("\n🎉 All checks passed! Your LOUS setup is ready.")
        print("\nNext steps:")
        print("  1. Install dependencies:")
        print("     cd backend && pip install -r requirements.txt")
        print("     cd frontend && npm install")
        print("\n  2. Start the application:")
        print("     ./start-dev.sh")
        print("\n  Or use Docker:")
        print("     docker-compose up --build")
        print("\n  3. Login with:")
        print("     Username: admin")
        print("     Password: admin123")
        print()
    else:
        print("\n⚠️  Some checks failed. Please review the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
