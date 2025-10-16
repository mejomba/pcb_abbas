from rest_framework import serializers
from .models import (AttributeGroup, Attribute, AttributeOption,
                     ConditionalRule, Order, OrderSelection)


class AttributeOptionSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای مدل گزینه‌ها
    """
    class Meta:
        model = AttributeOption
        # تمام فیلدهای مدل را شامل می‌شود
        fields = ['id', 'attribute', 'value', 'display_name', 'is_default', 'display_order']


class AttributeSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای مدل ویژگی‌ها به همراه گزینه‌های زیرمجموعه‌اش
    """
    # نمایش گزینه‌های مربوط به هر ویژگی به صورت تودرتو (Nested)
    options = AttributeOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Attribute
        fields = ['id', 'group', 'name', 'display_name', 'control_type', 'display_order', 'options']


class AttributeGroupSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای مدل گروه‌ها به همراه ویژگی‌های زیرمجموعه‌اش
    """
    # نمایش ویژگی‌های مربوط به هر گروه به صورت تودرتو
    attributes = AttributeSerializer(many=True, read_only=True)

    class Meta:
        model = AttributeGroup
        fields = ['id', 'name', 'display_name', 'display_order', 'attributes']


class ConditionalRuleSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای مدل قوانین شرطی، با فرمتی ساده برای فرانت‌اند.
    """
    # نام مدل هدف را به صورت یک رشته ساده برمی‌گردانیم (مثال: 'attribute' یا 'option')
    target_type = serializers.CharField(source='target_content_type.model', read_only=True)

    class Meta:
        model = ConditionalRule
        fields = [
            'id',
            'trigger_option',  # شناسه گزینه‌ای که شرط را فعال می‌کند
            'action_type',     # نوع عمل: 'disable', 'hide', 'enable', 'show'
            'target_type',     # نوع هدف: 'attributegroup', 'attribute', 'attributeoption'
            'target_object_id' # شناسه هدف
        ]


class OrderSelectionSerializer(serializers.ModelSerializer):
    attribute_name = serializers.CharField(source='attribute.display_name', read_only=True)
    selected_option_name = serializers.CharField(source='selected_option.display_name', read_only=True)

    class Meta:
        model = OrderSelection
        fields = [
            'id',
            'attribute',
            'attribute_name',
            'selected_option',
            'selected_option_name',
            'value',
        ]


class OrderSerializer(serializers.ModelSerializer):
    selections = OrderSelectionSerializer(many=True, required=False)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'user_name',
            'quantity',
            'status',
            'created_at',
            'updated_at',
            'selections',
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def create(self, validated_data):
        selections_data = validated_data.pop('selections', [])
        order = Order.objects.create(**validated_data)

        # ایجاد رکوردهای انتخابی
        for selection in selections_data:
            OrderSelection.objects.create(order=order, **selection)
        return order

    def update(self, instance, validated_data):
        selections_data = validated_data.pop('selections', None)

        # آپدیت فیلدهای ساده سفارش
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # اگر selections ارسال شده بود → به‌روزرسانی آنها
        if selections_data is not None:
            # ابتدا همه انتخاب‌های قبلی حذف شوند (می‌توان سفارشی‌تر هم کرد)
            instance.selections.all().delete()
            for selection in selections_data:
                OrderSelection.objects.create(order=instance, **selection)

        return instance
