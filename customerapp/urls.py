from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'tags', views.TagViewSet, basename='tag')
router.register(r'vendors-types', views.VendorTypeViewSet, basename='vendor-type')
router.register(r'places', views.PlaceViewSet, basename='place')
router.register(r'persons-allowed', views.PersonAllowedViewSet, basename='person-allowed')
router.register(r'vendors-status', views.VendorStatusViewSet, basename='vendor-status')
router.register(r'payments-types', views.PaymentTypeChoicesViewSet, basename='payment-type')
router.register(r'schedules-types', views.ScheduleTypeChoicesViewSet, basename='schedule-type')
router.register(r'banners', views.BannerViewSet, basename='banner')
router.register(r'vendors', views.VendorViewSet, basename='vendor')
router.register(r'services', views.ServiceViewSet, basename='service')
router.register(r'employees', views.EmployeeViewSet, basename='employee')
router.register(r'availabilities', views.AvailabilityViewSet, basename='availability')
router.register(r'orders-status', views.OrderStatusViewSet, basename='order-status')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'offer-code', views.OfferCodeViewSet, basename='offer-code')
router.register(r'wallet', views.WalletViewSet, basename='wallet')
router.register(r'alrajhi', views.AlrajhiViewSet, basename='alrajhi')
router.register(r'tamara', views.TamaraViewSet, basename='tamara')

urlpatterns = [
  path('pagment/success/', views.payment_success_view, name='payment_success_view'),
  path('pagment/cacel/', views.payment_cancel_view, name='payment_cancel_view'),
  path('pagment/error/', views.payment_error_view, name='payment_error_view'),
]

urlpatterns += (
    path('api/', include((router.urls, 'authapp'), namespace='api'), ),
)
