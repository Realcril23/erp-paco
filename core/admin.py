from django.contrib import admin
from .models import Figura, Venta, Abono

# Permite gestionar abonos directamente dentro de la vista de la Venta
class AbonoInline(admin.TabularInline):
    model = Abono
    extra = 1  # Espacio para agregar un abono nuevo rápidamente
    readonly_fields = ('fecha_pago',)

@admin.register(Figura)
class FiguraAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'medida', 'material', 'precio', 'stock')
    list_filter = ('material',)
    search_fields = ('nombre',)

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    # Columnas que verás en la lista de ventas
    list_display = ('n_contrato', 'cliente', 'figura', 'deuda_total', 'monto_pagado', 'get_saldo', 'estado')
    
    # Filtros laterales
    list_filter = ('estado', 'modalidad_pago', 'fecha_venta')
    
    # Buscador por cliente o número de contrato
    search_fields = ('cliente', 'cedula', 'n_contrato')
    
    # Integrar los abonos dentro de la edición de la venta
    inlines = [AbonoInline]

    # Función para mostrar el saldo restante en la lista
    def get_saldo(self, obj):
        return f"${obj.saldo_restante}"
    get_saldo.short_description = 'Saldo Pendiente'

# Opcional: Registrar abonos por separado también
@admin.register(Abono)
class AbonoAdmin(admin.ModelAdmin):
    list_display = ('venta', 'monto', 'fecha_pago')
    list_filter = ('fecha_pago',)