# products/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (AttributeGroupViewSet, AttributeViewSet, AttributeOptionViewSet,
                    ConditionalRuleViewSet, content_type_autocomplete, object_autocomplete)

# ساخت یک روتر
router = DefaultRouter()

# ثبت ViewSet ها در روتر
router.register(r'groups', AttributeGroupViewSet, basename='group')
router.register(r'attributes', AttributeViewSet, basename='attribute')
router.register(r'options', AttributeOptionViewSet, basename='option')
router.register(r'rules', ConditionalRuleViewSet, basename='rule')

# URLهای برنامه شما توسط روتر به صورت خودکار ساخته می‌شوند
urlpatterns = [
    path('', include(router.urls)),
    path('content-type-autocomplete/', content_type_autocomplete, name='target-content-type-autocomplete'),
    path('object-id-autocomplete/', object_autocomplete, name='target-object-id-autocomplete'),
]