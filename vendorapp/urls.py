from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'tags', views.TagViewSet, basename='tag')
router.register(r'vendors-types', views.VendorTypeViewSet, basename='vendor-type')
router.register(r'places', views.PlaceViewSet, basename='place')
router.register(r'persons-allowed', views.PersonAllowedViewSet, basename='person-allowed')
router.register(r'vendors-status', views.VendorStatusViewSet, basename='vendor-status')
router.register(r'phones-types', views.PhoneTypeViewSet, basename='phone-type')
router.register(r'pictures-types', views.PictureTypeViewSet, basename='picture-type')
router.register(r'hours-choices', views.HoursChoicesViewSet, basename='hour-choice')
router.register(r'minutes-choices', views.MinutesChoicesViewSet, basename='minute-choice')
router.register(r'payments-types', views.PaymentTypeChoicesViewSet, basename='payment-type')
router.register(r'schedules-types', views.ScheduleTypeChoicesViewSet, basename='schedule-type')
router.register(r'vendor', views.VendorViewSet, basename='vendor')
router.register(r'services', views.ServiceViewSet, basename='service')
router.register(r'employees', views.EmployeeViewSet, basename='employee')
router.register(r'availabilities', views.AvailabilityViewSet, basename='availability')
router.register(r'banks', views.BankAccountViewSet, basename='bank')
router.register(r'withdraws-requests', views.WithdrawRequestViewSet, basename='withdraw_request')
router.register(r'offers', views.OfferViewSet, basename='offer')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'comments', views.CommentViewSet, basename='comment')

urlpatterns = [

]

urlpatterns += (
    path('api/', include((router.urls, 'authapp'), namespace='api'), ),
)
