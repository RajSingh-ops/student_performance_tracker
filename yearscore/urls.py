from django.contrib import admin
from django.urls import path, include
from tracker.views_auth import register_view, CustomLoginView, logout_view
from tracker.views import dashboard_view, handler404
from tracker import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', logout_view, name='logout'),

    path('register/', register_view, name='register'),

    path('dashboard/', dashboard_view, name='dashboard'),

    path('', include('tracker.urls')),

    path('accounts/', include('django.contrib.auth.urls')),

    path("review/", views.review_panel, name="review"),
    


    

]
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = handler404

