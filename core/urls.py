from django.urls import path
from . import views

urlpatterns = [
    # --- Autenticación e Inicio ---
    path('', views.landing, name='landing'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    
    # --- PORTAL DEL CLIENTE (Rutas Reales) ---
    path('portal/login/', views.login_cliente, name='login_cliente'),
    path('portal/inicio/', views.portal_cliente, name='portal_cliente'),
    
    # --- Panel Principal Admin ---
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # --- Galería / Inventario ---
    path('galeria/', views.cursos, name='cursos'),
    path('eliminar-figura/<int:figura_id>/', views.eliminar_figura, name='eliminar_figura'),
    
    # --- Ventas y Finanzas ---
    path('vender/<int:figura_id>/', views.realizar_venta, name='realizar_venta'),
    path('abonar/<int:venta_id>/', views.abonar_pago, name='abonar_pago'),
    
    # --- Auxiliares ---
    path('demo/', views.demo_view, name='demo'),
]