from rest_framework import serializers
from .models import AttributeGroup, Attribute, AttributeOption, ConditionalRule


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