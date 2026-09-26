from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from accounts.permissions import IsCustomer
from cart.services import CustomerResolver
from .serializers import CheckoutRequestSerializer, OrderDetailSerializer
from .services import OrderCreationService, OrderQueryService
from .models import Order


class CheckoutView(APIView):
    """
    POST /api/orders/checkout/
    Validates delivery address & payment selection, re-checks real-time inventory,
    creates Order + OrderItem(s) + Payment, and clears the customer's cart.
    Requires authenticated CUSTOMER role.
    """
    permission_classes = [IsCustomer]

    def post(self, request):
        customer = CustomerResolver.get_customer_for_user(request.user)
        serializer = CheckoutRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = OrderCreationService.create_order_from_cart(
            customer=customer,
            checkout_data=serializer.validated_data
        )

        response_data = OrderDetailSerializer(order).data
        return Response({
            'message': 'Order placed successfully.',
            'order': response_data,
        }, status=status.HTTP_201_CREATED)


class OrderDetailView(APIView):
    """
    GET /api/orders/<order_id>/
    Retrieves full details of an order.
    Enforces authorization: Customers can only view their own orders.
    Requires authenticated CUSTOMER role.
    """
    permission_classes = [IsCustomer]

    def get(self, request, order_id):
        customer = CustomerResolver.get_customer_for_user(request.user)
        order = OrderQueryService.get_customer_order(customer, order_id)
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomerOrdersListView(APIView):
    """
    GET /api/orders/
    Lists all orders placed by the authenticated customer.
    Requires authenticated CUSTOMER role.
    """
    permission_classes = [IsCustomer]

    def get(self, request):
        customer = CustomerResolver.get_customer_for_user(request.user)
        orders = Order.objects.filter(customer=customer).order_by('-order_date')
        serializer = OrderDetailSerializer(orders, many=True)
        return Response({
            'count': len(serializer.data),
            'results': serializer.data
        }, status=status.HTTP_200_OK)
