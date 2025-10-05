from django.contrib import admin
from . import views
from django.urls import path, include

urlpatterns = [
    path('', include('djoser.urls')),
    path('menu-items',views.MenuItemsViewSet.as_view({
            'get': 'list',
            'post': 'create',
        }), name="menu-collection"),
    path('menu-items/<int:pk>',views.MenuItemsViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy',
        }), name="menu-single"),
    path('groups/manager/users',views.ManagerViewSet.as_view({
            'get': 'list',
            'post': 'create',
        }), name="manager-collection"),
    path('groups/manager/users/<int:pk>',views.ManagerViewSet.as_view({
            'delete': 'destroy',
        }), name="manager-collection"),
    path('groups/delivery-crew/users',views.DeliveryCrewViewSet.as_view({
            'get': 'list',
            'post': 'create',
        }), name="manager-collection"),
    path('groups/delivery-crew/users/<int:pk>',views.DeliveryCrewViewSet.as_view({
            'delete': 'destroy',
        }), name="manager-collection"),
    path('cart/menu-items',views.CartViewSet.as_view({
            'get': 'list',
            'post': 'create',
            'delete': 'clear',
        }), name="cart"),
    path('orders',views.OrderViewSet.as_view({
            'get': 'list',
            'post': 'order',
        }), name="order-collection"),
    path('orders/<int:pk>',views.OrderViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy',
        }), name="order-single"),
]

