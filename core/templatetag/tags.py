from django import template
from core.models import OrderProcess

register = template.Library()

@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = OrderProcess.objects.filter(user=user)
        if qs.exists():
            return qs[0].products.count()
    return 0