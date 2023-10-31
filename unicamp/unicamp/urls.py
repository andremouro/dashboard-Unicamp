from django.contrib import admin
from django.urls import path, include
from dashboard import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.NewView.as_view()),
    path('pop/', views.PopView.as_view()),
    path('host/', views.HostView.as_view()),
    path('socio/', views.SocioView.as_view()),
    path('map/', views.MapView.as_view()),
    path('test/', views.TestView.as_view()),
    path('thost/', views.TestHostView.as_view()),
    path('tsocio/', views.SocioViewJS.as_view()),
    path('tmap/', views.MapViewJS.as_view()),
    path("__debug__/", include("debug_toolbar.urls"))
]

urlpatterns += staticfiles_urlpatterns()