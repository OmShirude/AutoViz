from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path('upload_database/', views.upload_database, name='upload_database'),
    path('charts/', views.charts_view, name='charts_view'),
    path('query/', views.query_page, name='query_page'),
    path('logout/', views.logout_user, name='logout'),
    path('change_database/', views.upload_database, name='change_database'),
    path("generate_dashboard/", views.generate_dashboard, name="generate_dashboard"),
]
