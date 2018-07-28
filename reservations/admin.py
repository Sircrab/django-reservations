from django.contrib import admin

from .models import User, Menu, MenuItem, Order

class MenuItemInline(admin.TabularInline):
    """
    Inline definition of menuItems for the admin interface, allows for easy creation of menus.
    """
    model = MenuItem
    extra = 2

class MenuAdmin(admin.ModelAdmin):
    """
    Custom menu creation and edit view for the admin panel, used mostly for testing purposes.
    """
    fieldsets = [
        ('Titulo de menu', {'fields': ['menu_title']}),
    ]
    inlines=[MenuItemInline]
    list_display = ('menu_title', 'created', 'modified', 'unique_id')

admin.site.register(User)
admin.site.register(Menu, MenuAdmin)
admin.site.register(MenuItem)
admin.site.register(Order)