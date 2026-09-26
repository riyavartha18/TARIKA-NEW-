import datetime
from django.db.models import Q
from warehouse.models import Delivery, Order


class DeliveryPartnerService:
    """
    Business service layer for Delivery Partner portal.
    Enforces strict employee data isolation so partners only see/modify
    deliveries assigned to their employee profile.
    """

    @staticmethod
    def get_assigned_deliveries(employee_id, status=None, search=None):
        """
        Returns deliveries assigned to the given delivery partner employee.
        Supports status filtering and search across delivery ID, order ID,
        customer name, city, phone, and address.
        """
        qs = (
            Delivery.objects
            .filter(assigned_employee_id=employee_id)
            .select_related('order__customer', 'assigned_employee', 'warehouse')
        )

        if status and status.strip().lower() not in ['all', '']:
            qs = qs.filter(delivery_status__iexact=status.strip())

        if search and search.strip():
            term = search.strip()
            qs = qs.filter(
                Q(delivery_id__icontains=term) |
                Q(order_id__icontains=term) |
                Q(order__customer__full_name__icontains=term) |
                Q(order__customer__city__icontains=term) |
                Q(order__customer__phone__icontains=term) |
                Q(order__shipping_address__icontains=term)
            )

        return qs.order_by('-dispatch_date', '-delivery_id')

    @staticmethod
    def get_delivery_detail(delivery_id, employee_id):
        """
        Fetch single delivery detail, strictly validating ownership.
        Raises Delivery.DoesNotExist if not found or not assigned to employee.
        """
        return (
            Delivery.objects
            .select_related('order__customer', 'assigned_employee', 'warehouse')
            .get(delivery_id=delivery_id, assigned_employee_id=employee_id)
        )

    @staticmethod
    def update_delivery_status(delivery_id, employee_id, new_status, reason=''):
        """
        Updates the status of an assigned delivery.
        Transitions: Assigned -> Picked Up -> In Transit -> Delivered (or Delayed / Failed).
        """
        delivery = (
            Delivery.objects
            .select_related('order', 'order__customer', 'assigned_employee', 'warehouse')
            .get(delivery_id=delivery_id, assigned_employee_id=employee_id)
        )

        # Normalize status to canonical capitalization
        valid_map = {
            'assigned': 'Assigned',
            'picked up': 'Picked Up',
            'in transit': 'In Transit',
            'delivered': 'Delivered',
            'delayed': 'Delayed',
            'failed': 'Failed',
        }
        canonical_status = valid_map.get(new_status.strip().lower(), new_status.strip())

        delivery.delivery_status = canonical_status
        now_date_str = datetime.date.today().strftime('%Y-%m-%d')
        now_iso = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')

        if canonical_status == 'Delivered':
            delivery.actual_delivery_date = now_date_str
            delivery.failure_reason = None
            if delivery.order:
                delivery.order.order_status = 'delivered'
                delivery.order.updated_at = now_iso
                delivery.order.save(update_fields=['order_status', 'updated_at'])

        elif canonical_status in ['Delayed', 'Failed']:
            delivery.failure_reason = reason or delivery.failure_reason or f"Marked {canonical_status} by delivery partner"

        elif canonical_status in ['Picked Up', 'In Transit']:
            # Clear exception reason if transitioning back to normal flow unless reason explicitly passed
            if not reason:
                delivery.failure_reason = None
            if delivery.order and (delivery.order.order_status or '').lower() in ['pending', 'confirmed']:
                delivery.order.order_status = 'shipped'
                delivery.order.updated_at = now_iso
                delivery.order.save(update_fields=['order_status', 'updated_at'])

        delivery.save()
        return delivery

    @staticmethod
    def get_dashboard_metrics(employee_id):
        """
        Calculates real-time delivery performance metrics for the logged-in partner.
        """
        qs = Delivery.objects.filter(assigned_employee_id=employee_id)

        all_deliveries = list(qs.values('delivery_status'))
        total = len(all_deliveries)

        status_counts = {}
        for d in all_deliveries:
            st = (d.get('delivery_status') or '').strip().title()
            status_counts[st] = status_counts.get(st, 0) + 1

        pending_pickup = status_counts.get('Assigned', 0)
        picked_up = status_counts.get('Picked Up', 0)
        in_transit = status_counts.get('In Transit', 0)
        delivered = status_counts.get('Delivered', 0)
        delayed = status_counts.get('Delayed', 0)
        failed = status_counts.get('Failed', 0)

        active = pending_pickup + picked_up + in_transit
        exceptions = delayed + failed

        return {
            'total_assigned': total,
            'active_deliveries': active,
            'pending_pickup': pending_pickup,
            'picked_up': picked_up,
            'in_transit': in_transit,
            'delivered': delivered,
            'delayed': delayed,
            'failed': failed,
            'exceptions': exceptions,
        }
