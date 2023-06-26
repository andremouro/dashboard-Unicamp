from django.contrib import admin
from django.urls import path, include
from dashboard import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.NewView.as_view()),
    path('pop/', views.PopView.as_view()),
    path('host/', views.HostView.as_view())
]

urlpatterns += staticfiles_urlpatterns()