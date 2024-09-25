from django.urls import path
from .views import mynews, Category, Details

urlpatterns = [
    path('', mynews, name='mynews' ),
    path('home/', mynews, name='home' ),
    path('trending/', mynews, name='mynews' ),
    path('category/<category>/', Category, name='category' ),
    path('details/<int:id>/', Details, name='details' ),
]