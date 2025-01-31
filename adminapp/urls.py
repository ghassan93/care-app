from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'index', views.IndexViewSet, basename='index')
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'vendors', views.VendorViewSet, basename='vendor')
router.register(r'services', views.ServiceViewSet, basename='service')
router.register(r'withdraw-request', views.WithdrawRequestViewSet, basename='withdraw-request')
router.register(r'offers', views.OfferViewSet, basename='offer')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'invoices', views.InvoiceViewSet, basename='invoice')
router.register(r'cities', views.CityViewSet, basename='city')
router.register(r'policies', views.PoliciesViewSet, basename='policies')
router.register(r'tags', views.TgaViewSet, basename='tag')
router.register(r'banners', views.BannerViewSet, basename='banner')
router.register(r'wallets', views.WalletViewSet, basename='wallet')
router.register(r'comments', views.CommentViewSet, basename='comment')
router.register(r'notifications', views.NotificationViewSet, basename='notification')

urlpatterns = [
    path('', views.home_view, name='home_view'),
    path('profile/', views.user_profile_view, name='user_profile_view'),

    path('customers/', views.customer_view, name='customer_view'),
    path('customers/create/', views.customer_create_view, name='customer_create_view'),
    path('customers/update/<str:slug>/', views.customer_update_view, name='customer_update_view'),
    path('customers/wallet/<str:slug>/', views.wallet_view, name='wallet_view'),

    path('services/', views.service_view, name='service_view'),
    path('services/update/<str:slug>/', views.service_view_update_view, name='service_update_view'),

    path('vendors/', views.vendor_view, name='vendor_view'),
    path('vendors/update/<str:slug>/', views.vendor_update_view, name='vendor_update_view'),
    path('vendors/detail/<str:slug>/', views.vendor_detail_view, name='vendor_detail_view'),
    path('vendors/users/update/<str:slug>/', views.vendor_user_update_view, name='vendor_user_update_view'),

    path('orders/', views.order_view, name='order_view'),
    path('orders/detail/<int:pk>/', views.order_detail_view, name='order_detail_view'),

    path('invoices/', views.invoice_view, name='invoice_view'),
    path('invoices/detail/<int:pk>/', views.invoice_detail_view, name='invoice_detail_view'),
    path('invoices/dowload/<int:pk>/', views.generate_invoice_file, name='generate_invoice_file'),

    path('settings/', views.settings_view, name='settings_view'),

    path('managers/', views.manager_view, name='manager_view'),
    path('managers/create/', views.manager_create_view, name='manager_create_view'),
    path('managers/update/<str:slug>/', views.manager_update_view, name='manager_update_view'),

    path('cities/', views.city_view, name='city_view'),
    path('cities/create/', views.city_create_view, name='city_create_view'),
    path('cities/update/<str:slug>/', views.city_update_view, name='city_update_view'),

    path('ploicies/', views.policies_view, name='policies_view'),
    path('ploicies/create/', views.policies_create_view, name='policies_create_view'),
    path('ploicies/update/<str:slug>/', views.policies_update_view, name='policies_update_view'),

    path('tags/', views.tag_view, name='tag_view'),
    path('tags/create/', views.tag_create_view, name='tag_create_view'),
    path('tags/update/<str:slug>/', views.tag_update_view, name='tag_update_view'),

    path('offers/', views.offer_view, name='offer_view'),
    path('offers/create/', views.offer_create_view, name='offer_create_view'),
    path('offers/activate/<int:pk>/', views.activate_offer_code, name='activate_offer_code'),

    path('withdraw-request/', views.withdraw_request_view, name='withdraw_request_view'),
    path('withdraw-request/update/<int:pk>/', views.withdraw_request_update_view, name='withdraw_request_update_view'),

    path('banner/', views.banner_view, name='banner_view'),
    path('banner/create/', views.banner_create_view, name='banner_create_view'),
    path('banner/update/<int:pk>/', views.banner_update_view, name='banner_update_view'),

    path('comments/', views.comment_view, name='comment_view'),
    path('comments/update/<int:pk>/', views.comment_update_view, name='comment_update_view'),

    path('notifications/', views.notification_view, name='notification_view'),
    path('notifications/settings/', views.notification_settings_view, name='notification_settings_view'),
    path('notifications/send/<str:role>/', views.notification_messages_view, name='notification_messages_view'),
    path('send-marketing-email/', views.send_marketing_email_view, name='send_marketing_email_view'),
        # path('test/', views.test, name='test'),


]

urlpatterns += (
    path('api/', include((router.urls, 'authapp'), namespace='api'), ),
)
