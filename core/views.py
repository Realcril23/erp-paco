from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User 
from django.contrib import messages 
from django.db.models import Sum 
from django.utils import timezone
from decimal import Decimal
import datetime # Importante para timedelta

from .models import Figura, Venta, Abono

# 1. Inicio
def landing(request):
    return render(request, 'core/landing.html')

# 2. Login Administrativo
def login_view(request):
    if request.method == 'POST':
        usuario = request.POST.get('username')
        clave = request.POST.get('password')
        user = authenticate(request, username=usuario, password=clave)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'core/login.html', {'error': 'Credenciales incorrectas'})
    return render(request, 'core/login.html')

# 3. Registro de Usuarios
def register(request):
    if request.method == 'POST':
        usuario = request.POST.get('username')
        correo = request.POST.get('email')
        clave = request.POST.get('password')
        if User.objects.filter(username=usuario).exists():
            return render(request, 'core/register.html', {'error': 'Ese nombre de usuario ya existe.'})
        User.objects.create_user(username=usuario, email=correo, password=clave)
        return redirect('login')
    return render(request, 'core/register.html')

# 4. Portal del Cliente (Login y Vista)
def login_cliente(request):
    if request.method == 'POST':
        cedula = request.POST.get('username')
        clave = request.POST.get('password')
        user = authenticate(request, username=cedula, password=clave)
        if user is not None:
            login(request, user)
            return redirect('portal_cliente')
        else:
            return render(request, 'cliente/login_cliente.html', {'error': 'Cédula o contraseña incorrecta.'})
    return render(request, 'cliente/login_cliente.html')

@login_required
def portal_cliente(request):
    # Buscamos la venta donde la cédula coincida con el nombre de usuario
    venta = Venta.objects.filter(cedula=request.user.username).first()
    
    if not venta:
        messages.warning(request, "No tienes contratos activos vinculados.")
        return redirect('landing')
    
    context = {
        'venta': venta,
        'saldo': venta.saldo_restante,
        'fecha_compra': venta.fecha_venta,
        'fecha_pago': venta.fecha_limite,
        'producto': venta.figura
    }
    return render(request, 'cliente/portal_cliente.html', context)

# 5. Cerrar Sesión
def logout_view(request):
    logout(request)
    return redirect('landing')

# 6. Dashboard (Finanzas y Gráficas)
@login_required 
def dashboard(request):
    total_neto = Venta.objects.aggregate(Sum('monto_pagado'))['monto_pagado__sum'] or 0
    ventas_todas = Venta.objects.all().order_by('-fecha_venta')
    por_cobrar = sum(v.saldo_restante for v in ventas_todas)
    facturas_pendientes = Venta.objects.exclude(estado='PAGADO').count()

    dias_labels = []
    ganancias_data = []
    
    # Generar datos de los últimos 7 días para la gráfica
    for i in range(6, -1, -1):
        dia_iterado = timezone.now().date() - datetime.timedelta(days=i)
        dias_labels.append(dia_iterado.strftime('%d %b'))
        monto_dia = Abono.objects.filter(fecha_pago__date=dia_iterado).aggregate(Sum('monto'))['monto__sum'] or 0
        ganancias_data.append(float(monto_dia))

    context = {
        'total_neto': total_neto,
        'por_cobrar': por_cobrar,
        'facturas_pendientes': facturas_pendientes,
        'ventas': ventas_todas[:10],
        'grafica_dias': dias_labels,
        'grafica_monto': ganancias_data,
    }
    return render(request, 'core/dashboard.html', context)

# 7. Galería / Inventario
@login_required
def cursos(request):
    if request.method == 'POST':
        nom = request.POST.get('nombre')
        mat = request.POST.get('material')
        pre = request.POST.get('precio')
        stk = int(request.POST.get('stock', 0))
        med = request.POST.get('medida', '40cm')
        desc = request.POST.get('descripcion')
        img = request.FILES.get('imagen') 

        Figura.objects.create(
            nombre=nom, material=mat, precio=pre,
            medida=med, imagen=img, stock=stk,
            descripcion=desc
        )
        messages.success(request, f"Pieza '{nom}' registrada exitosamente.")
        return redirect('cursos')

    figuras_db = Figura.objects.all().order_by('-id')
    return render(request, 'core/cursos.html', {'figuras': figuras_db})

# 8. Ventas y Pagos
@login_required
def realizar_venta(request, figura_id):
    if request.method == 'POST':
        figura = get_object_or_404(Figura, id=figura_id)
        if figura.stock <= 0:
            messages.error(request, "¡ERROR! No queda stock.")
            return redirect('cursos')

        Venta.objects.create(
            cliente=request.POST.get('cliente'),
            cedula=request.POST.get('cedula'),
            telefono=request.POST.get('telefono'),
            domicilio=request.POST.get('domicilio'),
            referencia=request.POST.get('referencia'),
            n_contrato=request.POST.get('n_contrato'),
            modalidad_pago=request.POST.get('modalidad_pago'),
            archivo_contrato=request.FILES.get('archivo_contrato'),
            figura=figura,
            deuda_total=figura.precio,
            monto_pagado=0,
            fecha_limite=request.POST.get('fecha_limite'),
            vendedor=request.user,
            estado='PENDIENTE'
        )
        figura.stock -= 1
        figura.save()
        messages.success(request, "Venta realizada exitosamente.")
    return redirect('dashboard')

@login_required
def abonar_pago(request, venta_id):
    if request.method == 'POST':
        venta = get_object_or_404(Venta, id=venta_id)
        try:
            monto = Decimal(request.POST.get('monto', 0))
            if monto > 0:
                Abono.objects.create(venta=venta, monto=monto)
                messages.success(request, f"Abono de ${monto} registrado.")
            else:
                messages.error(request, "El monto debe ser mayor a 0.")
        except:
            messages.error(request, "Monto inválido.")
    return redirect('dashboard')

# 9. Otros
@login_required
def eliminar_figura(request, figura_id):
    figura = get_object_or_404(Figura, id=figura_id)
    figura.delete()
    return redirect('cursos')

def demo_view(request):
    clientes_demo = [{
        'nombre': 'Usuario de Prueba',
        'deuda_total': 100,
        'monto_pagado': 45,
        'porcentaje': 45
    }]
    return render(request, 'core/demo.html', {'clientes': clientes_demo})