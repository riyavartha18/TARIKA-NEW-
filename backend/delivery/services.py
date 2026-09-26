from datetime import datetime, timezone
from django.db import transaction
from django.db.models import Q, Count
from warehouse.models import Delivery, Order
from accounts.models import Employee


class DeliveryPartnerService:
    @staticmethod
    def get_assigned_deliveries(employee_id, status=None, search=None):
        """
        Fetch ONLY deliveries assigned to the specified delivery employee_id.
        Optionally filter by status (case-insensitive) or search across delivery_id/order_id/customer name.
        """
        qs = (
            Delivery.objects
            .filter(assigned_employee_id=employee_id)
            .select_related('order__customer', 'assigned_employee', 'warehouse')
        )

        if status and status.upper() != 'ALL':
            qs = qs.filter(delivery_status__iexact=status)

        if search:
            q = search.strip()
            search_q = (
                Q(delivery_id__icontains=q) |
                Q(order__order_id__icontains=q) |
                Q(order__customer__full_name__icontains=q) |
                Q(order__shipping_address__icontains=q)
            )
            if q.isdigit():
                search_q |= Q(order__customer__phone=int(q))
            qs = qs.filter(search_q)

        return qs.order_by('-dispatch_date', '-delivery_id')

    @staticmethod
    def get_delivery_detail(delivery_id, employee_id):
        """
        Fetch a single delivery by delivery_id ensuring it belongs to employee_id.
        Raises Delivery.DoesNotExist if not found or unauthorized.
        """
        delivery = (
            Delivery.objects
            .select_related('order__customer', 'assigned_employee', 'warehouse')
            .filter(delivery_id=delivery_id, assigned_employee_id=employee_id)
            .first()
        )
        if not delivery:
            raise Delivery.DoesNotExist(f"Delivery '{delivery_id}' not found or not assigned to you.")
        return delivery

    @classmethod
    def update_delivery_status(cls, delivery_id, employee_id, new_status, reason=''):
        """
        Updates the status of an assigned delivery.
        When status becomes 'Delivered':
        - delivery_status = 'Delivered'
        - actual_delivery_date = current date (YYYY-MM-DD)
        - linked order.order_status = 'delivered'
        When Delayed or Failed:
        - delivery_status = new_status
        - failure_reason = reason
        """
        delivery = cls.get_delivery_detail(delivery_id, employee_id)
        now_date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        now_iso_str = datetime.now(timezone.utc).isoformat()

        with transaction.atomic():
            delivery.delivery_status = new_status

            if new_status.lower() == 'delivered':
                delivery.actual_delivery_date = now_date_str
                # Sync linked Order status to 'delivered'
                if delivery.order:
                    order = delivery.order
                    order.order_status = 'delivered'
                    order.updated_at = now_iso_str
                    order.save(update_fields=['order_status', 'updated_at'])
            elif new_status.lower() in ['delayed', 'failed']:
                if reason:
                    delivery.failure_reason = reason.strip()

            delivery.save()

        # Return refreshed delivery object with pre-fetched relations
        return cls.get_delivery_detail(delivery_id, employee_id)

    @staticmethod
    def get_dashboard_metrics(employee_id):
        """
        Returns metric counts for the logged-in delivery employee.
        """
        deliveries = Delivery.objects.filter(assigned_employee_id=employee_id)
        
        counts = {
            'total': deliveries.count(),
            'assigned': 0,
            'picked_up': 0,
            'in_transit': 0,
            'delivered': 0,
            'delayed': 0,
            'failed': 0,
        }

        status_counts = deliveries.values('delivery_status').annotate(count=Count('delivery_id'))
        for sc in status_counts:
            st = (sc['delivery_status'] or '').strip().lower()
            cnt = sc['count']
            if st == 'assigned':
                counts['assigned'] += cnt
            elif st == 'picked up':
                counts['picked_up'] += cnt
            elif st == 'in transit':
                counts['in_transit'] += cnt
            elif st == 'delivered':
                counts['delivered'] += cnt
            elif st == 'delayed':
                counts['delayed'] += cnt
            elif st == 'failed':
                counts['failed'] += cnt

        return counts
