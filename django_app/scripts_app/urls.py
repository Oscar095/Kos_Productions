from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('run/<int:script_id>/', views.run_script, name='run_script'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]
