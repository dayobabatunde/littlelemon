from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth.models import User

class CategorySerializer (serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']

class MenuItemSerializer (serializers.ModelSerializer):
    
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True
    )
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = MenuItem
        fields = ['id',  'title', 'price', 'featured', 'category', 'category_id']
        extra_kwargs = {
            'price': {'min_value': 0},
        }
        validators = [
            UniqueTogetherValidator(
                queryset=MenuItem.objects.all(),
                fields=['title', 'category'],
                message="This category already has an item with that title."
            )
        ]
        
class UserSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset = User.objects.all(),
        source="*",            # ensures we get
    )
    class Meta:
        model = User
        fields = ['user_id', 'username', 'first_name', 'last_name', 'email', 'groups']
        read_only_fields = ["username", "first_name", "last_name", 'email', 'groups']
        
class CartSerializer (serializers.ModelSerializer):
    
    menuitem_id = serializers.PrimaryKeyRelatedField(
        queryset = MenuItem.objects.all(),
        source="menuitem",            # ensures we get
        write_only=True
    )
    menuitem = MenuItemSerializer(read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = Cart
        fields = ['user','menuitem_id', 'menuitem', 'quantity', 'unit_price', 'price']
        read_only_fields = ['unit_price', 'price']
        extra_kwargs = {
            'quantity': {'min_value': 1},
        }
        validators = [
            UniqueTogetherValidator(
                queryset=Cart.objects.all(),
                fields=['menuitem_id', 'user'],
                message='This item is already in your cart.'
            )
        ]       

class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["menuitem", "quantity", "unit_price"]


class OrderSerializer(serializers.ModelSerializer):
    
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    items = OrderItemSerializer(source="orderitem_set", many=True, read_only=True)
    
    delivery_crew_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(groups__name="Delivery Crew").prefetch_related("groups"),
        source="delivery_crew",
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Order
        fields = ["id", "user", "delivery_crew", "delivery_crew_id", "status", "total", "date", "items"]
        read_only_fields = ["user", "total", "delivery_crew", "status", "date", "items"]

class ManagerOrderSerializer(serializers.ModelSerializer):
    
    user = serializers.SlugRelatedField(read_only=True, slug_field="username")
    
    user_id = serializers.IntegerField(source="user.id", read_only=True)

    items = OrderItemSerializer(source="orderitem_set", many=True, read_only=True)
    
    delivery_crew_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(groups__name="Delivery Crew").prefetch_related("groups"),
        source="delivery_crew",
        required=False,
        allow_null=True
    )

    class Meta:
        model = Order
        fields = ["id", "user_id", "user", "delivery_crew_id", "status", "total", "date", "items"]
        read_only_fields = ["user_id", "user", "total", "date", "items"]
        
    def validate(self, attrs):
        # Double-lock: even if someone manages to pass a non-filtered user
        dc = attrs.get("delivery_crew")
        if dc and not dc.groups.filter(name="Delivery Crew").exists():
            raise serializers.ValidationError(
                {"delivery_crew_id": "Selected user is not in the Delivery Crew group."}
            )
        return attrs
        
class DeliveryCrewOrderSerializer(serializers.ModelSerializer):
    
    user = serializers.SlugRelatedField(read_only=True, slug_field="username")
    
    user_id = serializers.IntegerField(source="user.id", read_only=True)

    items = OrderItemSerializer(source="orderitem_set", many=True, read_only=True)
    
    delivery_crew_id = serializers.IntegerField(source="delivery_crew.id", read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user_id", "user", "delivery_crew_id", "status", "total", "date", "items"]
        read_only_fields = ["user_id","user", "total", "delivery_crew_id", "date", "items"]
        
    def validate(self, attrs):
        # Double-lock: even if someone manages to pass a non-filtered user
        dc = attrs.get("delivery_crew")
        if dc and not dc.groups.filter(name="Delivery Crew").exists():
            raise serializers.ValidationError(
                {"delivery_crew_id": "Selected user is not in the Delivery Crew group."}
            )
        return attrs
        