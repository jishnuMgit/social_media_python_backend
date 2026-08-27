import json

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from .models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

@csrf_exempt
@api_view(['POST'])
def register(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "POST method required"},
            status=405
        )

    try:
        data = json.loads(request.body)

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        phone = data.get("phone")

        # Check required fields
        if not username or not email or not password:
            return JsonResponse(
                {
                    "error": "username, email and password are required"
                },
                status=400
            )

        # Check username
        if User.objects.filter(username=username).exists():
            return JsonResponse(
                {"error": "Username already exists"},
                status=400
            )

        # Check email
        if User.objects.filter(email=email).exists():
            return JsonResponse(
                {"error": "Email already exists"},
                status=400
            )

        # Check phone if provided
        if phone and User.objects.filter(phone=phone).exists():
            return JsonResponse(
                {"error": "Phone already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # IMPORTANT:
        # create_user() hashes the password correctly
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            phone=phone
        )

        return JsonResponse(
            {
                "message": "User registered successfully",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "phone": user.phone
                }
            },
            status=201
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON"},
            status=400
        )

@api_view(["POST"])
def user_login(request):

    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")

    # Need username OR email
    if not username and not email:
        return Response(
            {"error": "Username or email is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Password is always required
    if not password:
        return Response(
            {"error": "Password is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Login using email
    if email:
        try:
            user = User.objects.get(email=email)
            username = user.username
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid email or password"},
                status=status.HTTP_401_UNAUTHORIZED
            )

    # Django checks the password hash
    user = authenticate(
        request,
        username=username,
        password=password
    )

    if user is None:
        return Response(
            {"error": "Invalid username/email or password"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    login(request, user)
    refresh = RefreshToken.for_user(user)
    return Response(
    {
        "message": "Login successful",
        "tokens": {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        },
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone
        }
    },
    status=status.HTTP_200_OK
)
@api_view(['POST'])
def user_logout(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "POST method required"},
            status=405
        )

    logout(request)

    return JsonResponse(
        {"message": "Logout successful"},
        status=200
    )