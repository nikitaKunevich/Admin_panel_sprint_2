import debug_toolbar
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('movie_admin.api.urls')),
    path('__debug__/', include(debug_toolbar.urls)),
]
