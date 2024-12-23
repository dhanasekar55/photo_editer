from django.urls import path
from .views import home, edit_image

urlpatterns = [
    path('', home, name='home'),
    path('edit/<int:image_id>/', edit_image, name='edit_image'),
]
