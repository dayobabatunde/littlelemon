from django.shortcuts import render
from datetime import date
from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from django.contrib.auth.models import User, Group
from django.db import IntegrityError
from .models import MenuItem, Cart, Order, OrderItem
from .permissions import MenuItemPermissions, ManagerPermissions, CartPermissions, OrderPermissions
from .serializers import MenuItemSerializer, UserSerializer, CartSerializer, OrderSerializer, ManagerOrderSerializer, DeliveryCrewOrderSerializer

# Create your views here.
class MenuItemsViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    search_fields = ['title', 'price', 'featured']
    filterset_fields = ['category']
    ordering_fields = ['price']
    permission_classes = [MenuItemPermissions] 

class ManagerViewSet(viewsets.ModelViewSet):
    
    queryset = User.objects.filter(groups__name="Manager")
    serializer_class = UserSerializer
    permission_classes = [ManagerPermissions] 
    
    def create(self, request, *args, **kwargs):
        
        # Get user_id to be promoted to manager
        user_id = request.data.get("user_id")
        
        # If user_id not provided throw bad request error
        if not user_id:
            return Response({"detail": "No user_id field provided in body"},
                            status=status.HTTP_400_BAD_REQUEST)
 
        # See if user_id maps to a user, if it doesn't throw not found error
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."},
                            status=status.HTTP_404_NOT_FOUND)

        # Check if user is in manager group
        if user.groups.filter(name="Manager").exists():
            return Response({"detail": "User is already in the Manager group."},
                            status=status.HTTP_400_BAD_REQUEST)
            
        # Get Manager group
        manager_group = Group.objects.get(name="Manager")
        
        # Add user to the Manager group
        user.groups.add(manager_group)
        
        # Return that user has been added
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, *args, **kwargs):
        
        # Find user based on pk, error with bad request if not found
        user = self.get_object()  

        #  If user not in manager group return bad request
        if not user.groups.filter(name="Manager").exists():
            return Response({"detail": "User is not in the Manager group."},
                            status=status.HTTP_400_BAD_REQUEST)
        # Get manager group
        manager_group = Group.objects.get(name="Manager")

        # Remove user from group
        user.groups.remove(manager_group)
        
        # Return 200 response that tells client that user has been removed from manager group
        return Response({"detail": f"User {user.username} removed from Manager group."},
                        status=status.HTTP_200_OK)
        
class DeliveryCrewViewSet(viewsets.ModelViewSet):
    
    queryset = User.objects.filter(groups__name="Delivery Crew")
    serializer_class = UserSerializer
    permission_classes = [ManagerPermissions] 
    
    def create(self, request, *args, **kwargs):
        
        # Get user_id to be promoted to Delivery Crew
        user_id = request.data.get("user_id")
        
        # If user_id not provided throw bad request error
        if not user_id:
            return Response({"detail": "No user_id field provided in body"},
                            status=status.HTTP_400_BAD_REQUEST)
 
        # See if user_id maps to a user, if it doesn't throw not found error
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."},
                            status=status.HTTP_404_NOT_FOUND)

        # Check if user is in delivery crew group
        if user.groups.filter(name="Delivery Crew").exists():
            return Response({"detail": "User is already in the Delivery Crew group."},
                            status=status.HTTP_400_BAD_REQUEST)
            
        # Get Delivery Crew group
        delivery_crew_group = Group.objects.get(name="Delivery Crew")
        
        # Add user to the Deliver Crew group
        user.groups.add(delivery_crew_group)
        
        # Return that user has been added
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, *args, **kwargs):
        
        # Find user based on pk, error with bad request if not found
        user = self.get_object()  

        # If user not in Delivery Crew group return bad request
        if not user.groups.filter(name="Delivery Crew").exists():
            return Response({"detail": "User is not in the Delivery Crew group."},
                            status=status.HTTP_400_BAD_REQUEST)
            
        # Get Delivery Crew group
        delivery_crew_group = Group.objects.get(name="Delivery Crew")

        # Remove user from group
        user.groups.remove(delivery_crew_group)
        
        # Return 200 response that tells client that user has been removed from Delivery Crew group
        return Response({"detail": f"User {user.username} removed from Delivery Crew group."},
                        status=status.HTTP_200_OK)
        
class CartViewSet(viewsets.ModelViewSet):
    
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated, CartPermissions]
    
    def get_queryset(self):
        # Only return cart items for the logged-in user
        return Cart.objects.filter(user=self.request.user)
        
    
    def create(self, request, *args, **kwargs):
        
        # Validate input with serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # then the validated menu item is at:
        menuitem = serializer.validated_data["menuitem"]
        # Quantity
        quantity = serializer.validated_data["quantity"]

        # Prices
        unit_price = menuitem.price  # Decimal
        price = unit_price * quantity  # Decimal * int is fine

        # Insert user’s cart line (unique_together: (menuitem, user))
        try:
            cart_item = Cart.objects.create(
                user=request.user,
                menuitem=menuitem,
                quantity=quantity,
                unit_price=unit_price,
                price=price
            )
        except IntegrityError:
            return Response(
                {"detail": "This menu item is already in your cart"},
                status=status.HTTP_400_BAD_REQUEST)
            
        # Return the saved object using the read serializer
        read_data = self.get_serializer(cart_item).data
        return Response(read_data, status=status.HTTP_201_CREATED)      
    
    def clear(self, request, *args, **kwargs):
        self.get_queryset().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [OrderPermissions]
    
    def get_serializer_class(self):
        if self.request.user.is_superuser or self.request.user.groups.filter(name="Manager").exists():
            return ManagerOrderSerializer
        elif self.request.user.groups.filter(name="Delivery Crew").exists():
            return DeliveryCrewOrderSerializer
        else:
            return OrderSerializer
    
    def get_queryset(self):
        # Only return cart items for the logged-in user
        if self.request.user.is_superuser or self.request.user.groups.filter(name="Manager").exists():
            return Order.objects.all().prefetch_related("orderitem_set__menuitem")
        elif self.request.user.groups.filter(name="Delivery Crew").exists():
            return Order.objects.filter(delivery_crew=self.request.user).prefetch_related("orderitem_set__menuitem")
        else:
            return Order.objects.filter(user=self.request.user).prefetch_related("orderitem_set__menuitem")
    
    def order(self, request, *args, **kwargs):
        
        if request.user.groups.exists():
            return Response({"detail": "Only customers can order"}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        # Get cart for this user
        user_cart = Cart.objects.filter(user=request.user)
        
        # If there are no items in cart, in order should not be created
        if not user_cart.exists():
            return Response("No items in cart to order", status=status.HTTP_400_BAD_REQUEST)
        
        # Make new Order
        new_order = Order.objects.create(
            user = request.user,
            delivery_crew = None,
            status = False,
            total = 0,
            date = date.today()
        )
        
        total = 0
        
        # Make new OrderItem for every item in cart
        for item in user_cart:
            OrderItem.objects.create(
                order = new_order,
                menuitem = item.menuitem,
                quantity = item.quantity,
                unit_price = item.unit_price,
            )
            
            # Update order total price based on price (qunaitity * unit_price)
            total += item.price
            
        new_order.total = total
        new_order.save()
        
        # Delete all items in the user's cart
        user_cart.delete()
        
        # Let user know order was made
        return Response({"detail": "Order created successfully"}, status=status.HTTP_201_CREATED)
            
            
        
            
    
        
        
        