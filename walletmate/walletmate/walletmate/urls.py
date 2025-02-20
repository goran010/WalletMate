from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('walletmate_app.urls')),  # Include your app's URLs
    path('accounts/', include('django.contrib.auth.urls'))
]

