from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import refresh_jwt_token, verify_jwt_token

from . import views

router = DefaultRouter()

router.register(r'register', views.RegisterViewSet, basename='register')
router.register(r'token', views.AuthenticationViewSet, basename='token')
router.register(r'password', views.PasswordViewSet, basename='password')
router.register(r'email', views.EmailViewSet, basename='email')
router.register(r'profile', views.UserProfileViewSet, basename='profile')
router.register(r'addresses', views.AddressViewSet, basename='address')
router.register(r'notifications', views.NotificationViewSet, basename='notification')
router.register(r'cities', views.CityViewSet, basename='city')

urlpatterns = [

]

urlpatterns += (

    path('api/token/refresh/', refresh_jwt_token, name='refresh_jwt_token'),
    path('api/token/verify/', verify_jwt_token, name='verify_jwt_token'),

    path('login/', views.login_view, name='login_view'),

    path('logout/', views.logout_view, name='logout_view'),

    path('logout/done', views.logout_done_view, name='logout_done_view'),

    path('password/reset/', views.password_rest_view, name='reset_password_view'),

    path('password/reset/done/', views.password_rest_done_view, name='reset_password_done_view'),

    re_path(r'^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<code>.+)/$', views.password_rest_key_view,
            name='reset_password_key_view'),

    path('password/reset/key/done', views.password_rest_key_done_view, name='reset_password_key_done_view'),

    path('policies/<str:slug>/', views.policies_view, name='policies_view'),

)

urlpatterns += (
    path('api/', include((router.urls, 'authapp'), namespace='api'), ),
)
