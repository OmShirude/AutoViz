from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User
import json
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .nlp_model.query_to_dashboard import QueryToDashboard 


def home(request):
    return render(request, 'dashboard_app/home.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("query_page")  # Redirects to the query input page
        else:
            return render(request, "dashboard_app/login.html", {"error": "Invalid credentials"})
    return render(request, "dashboard_app/login.html")

def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        #  Check if username already exists
        if User.objects.filter(username=username).exists():
            return render(request, "dashboard_app/register.html", {"error": "Username is already taken"})

        #  Check if password is at least 8 characters
        if len(password) < 8:
            return render(request, "dashboard_app/register.html", {"error": "Password must be at least 8 characters long"})

        #  Check if passwords match
        if password == confirm_password:
            user = User.objects.create_user(username=username, password=password)
            user.save()
            return redirect('upload_database')  # Ensure the name matches the URL pattern
        else:
            return render(request, "dashboard_app/register.html", {"error": "Passwords do not match"})
    
    return render(request, "dashboard_app/register.html")

def upload_database(request):
    if request.method == "POST":
        db_type = request.POST["db_type"]
        username = request.POST["db_username"]
        password = request.POST["db_password"]
        host = request.POST["db_host"]
        port = request.POST["db_port"]
        db_name = request.POST["db_name"]

        # Convert host to 127.0.0.1 if "localhost" is entered
        if host.lower() == "localhost":
            host = "127.0.0.1"

        # Validate port range
        try:
            port = int(port)
            if port < 1024 or port > 65535:
                messages.error(request, "Port must be between 1024 and 65535")
                return render(request, "dashboard_app/upload_database.html")
        except ValueError:
            messages.error(request, "Port must be a number")
            return render(request, "dashboard_app/upload_database.html")

        # Construct the database URL
        db_url = f"{db_type}://{username}:{password}@{host}:{port}/{db_name}"
        
        try:
            # Create an engine and check the connection
            engine = create_engine(db_url)
            with engine.connect() as connection:
                request.session["db_url"] = db_url  # Store engine URL in session
                messages.success(request, "Database connection successful!")
                return redirect("query_page")

        except OperationalError as e:
            error_message = str(e).lower()
            if "access denied" in error_message:
                messages.error(request, "Incorrect username or password.")
            elif "unknown database" in error_message:
                messages.error(request, "Database name is incorrect.")
            elif "can't connect to mysql server" in error_message:
                messages.error(request, "Invalid host or port.")
            else:
                messages.error(request, "Database connection failed. Please check credentials.")
            return render(request, "dashboard_app/upload_database.html")

    return render(request, "dashboard_app/upload_database.html")

def query_page(request):
    return render(request, 'dashboard_app/query.html')  

def charts_view(request):
    return render(request, 'dashboard_app/charts.html')

def logout_user(request):
    logout(request)
    return redirect('login')

@csrf_exempt
def generate_dashboard(request):
    """
    Handles user queries and creates a Superset chart.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_query = data.get("user_query", "").strip()

            if not user_query:
                return JsonResponse({"error": "Query is empty."}, status=400)

            #  No need to pass `db_url`, it is fetched inside QueryToDashboard
            q2d = QueryToDashboard(user_query)
            result = q2d.process_query()

            return JsonResponse(result, safe = False)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)
