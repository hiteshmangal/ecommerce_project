from django.urls import path
from .views import upload_data, signup, login, generate_report

urlpatterns = [
    path('upload/', upload_data, name='upload_data'),
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('report/', generate_report, name='generate_report'),
]