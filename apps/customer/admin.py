from django.contrib import admin

from apps.customer.models import Order, ReviewMessage


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_id', 'customer', 'order_type', 'status', 'location', 'confirmed_at', 'total_sum'
    )
    readonly_fields = ('order_id', 'customer', 'order_type', 'location', 'confirmed_at')
    list_filter = ('status', 'confirmed_at', 'customer')
    search_fields = ('customer__phone_number', )
    date_hierarchy = 'confirmed_at'

    def total_sum(self, obj):
        return obj.total_sum

    def get_queryset(self, request):
        queryset = super(OrderAdmin, self).get_queryset(request)
        return queryset.filter(confirmed_at__isnull=False).order_by('-confirmed_at')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ReviewMessageAdmin(admin.ModelAdmin):
    list_display = ('customer', 'message', 'created_at')
    list_filter = ('customer', 'created_at')
    search_fields = ('customer__phone_number', )
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Order, OrderAdmin)
admin.site.register(ReviewMessage, ReviewMessageAdmin)
