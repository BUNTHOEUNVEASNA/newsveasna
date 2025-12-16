from django.contrib import admin
from .models import Category, NewsSource, Article

# Register Category Model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)} # Automatically fill slug from name

# Register NewsSource Model
@admin.register(NewsSource)
class NewsSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_url', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'base_url')

# Register Article Model
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    # This fixes the admin.E108 and admin.E116 errors by correctly using 'timestamp'
    list_display = (
        'title', 
        'source', 
        'timestamp', # Correct model field name (was incorrectly set to 'published_at')
        'created_at',
        'display_categories', # Custom method to display categories
    )
    
    list_filter = (
        'source', 
        'timestamp', # Correct model field name
        'categories', 
        'created_at'
    )
    
    search_fields = ('title', 'content', 'url')
    
    fieldsets = (
        (None, {'fields': ('title', 'url', 'image_url', 'source', 'content', 'timestamp')}),
        ('Categorization', {'fields': ('categories',)}),
        ('Metadata', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    # Custom method to display ManyToMany relationship in list_display
    def display_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    display_categories.short_description = 'Categories'