from django.contrib import admin
from django import forms
from django.contrib.contenttypes.models import ContentType

from .models import AttributeGroup, Attribute, AttributeOption, ConditionalRule, Order, OrderSelection, Attribute, AttributeOption
from django.contrib.contenttypes.admin import GenericTabularInline

import nested_admin
from dal import autocomplete


class ConditionalRuleForm(forms.ModelForm):
    class Meta:
        model = ConditionalRule
        fields = '__all__'
        widgets = {
            'target_content_type': autocomplete.ModelSelect2(url='pcb:target-content-type-autocomplete'),
            'target_object_id': autocomplete.ListSelect2(url='pcb:target-object-id-autocomplete', forward=['target_content_type']),
        }
        # widgets = {
        #     'target_content_type': autocomplete.ModelSelect2(
        #         url='content-type-autocomplete',
        #         forward=['object_id']
        #     ),
        #     'target_object_id': autocomplete.ModelSelect2(
        #         url='object-autocomplete',
        #         forward=['content_type']
        #     )
        # }


class ConfigItemFilter(admin.SimpleListFilter):
    title = 'Config Item Type'
    parameter_name = 'target_content_type'

    def lookups(self, request, model_admin):
        return [
            (ct.id, ct.model_class()._meta.verbose_name_plural)
            for ct in ContentType.objects.filter(
                model__in=['attributegroup', 'attribute', 'attributeoption']
            )
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(content_type_id=self.value())
        return queryset


# class AttributeOptionInline(admin.TabularInline):
#     """
#     اجازه می‌دهد گزینه‌های هر ویژگی را مستقیماً در صفحه ویرایش آن ویژگی اضافه یا ویرایش کنیم.
#     """
#     model = AttributeOption
#     extra = 1  # نمایش یک فیلد خالی برای افزودن گزینه جدید


# @admin.register(Attribute)
# class AttributeAdmin(admin.ModelAdmin):
#     list_display = ('display_name', 'name', 'group', 'control_type', 'display_order')
#     list_filter = ('group', 'control_type')
#     search_fields = ('display_name', 'name')
#     inlines = [AttributeOptionInline] # اضافه کردن اینلاین گزینه‌ها


class AttributeInline(admin.TabularInline):
    """
    اجازه می‌دهد ویژگی‌های هر گروه را در صفحه ویرایش همان گروه مدیریت کنیم.
    """
    model = Attribute
    extra = 0


# @admin.register(AttributeGroup)
# class AttributeGroupAdmin(admin.ModelAdmin):
#     list_display = ('display_name', 'name', 'display_order')
#     search_fields = ('display_name', 'name')
#     inlines = [AttributeInline] # اضافه کردن اینلاین ویژگی‌ها


class ConditionalRuleInline(GenericTabularInline):
    """
    اجازه می‌دهد قوانین شرطی را مستقیماً در صفحه گزینه‌ای که فعال‌کننده آن است، مدیریت کنیم.
    """
    model = ConditionalRule
    fk_name = 'trigger_option' # مشخص کردن کلید خارجی اصلی این اینلاین
    extra = 0
    # برای اینکه GenericForeignKey در ادمین نمایش داده شود، باید مدل‌ها را محدود کنیم
    ct_field = 'target_content_type'
    ct_fk_field = 'target_object_id'


# @admin.register(AttributeOption)
# class AttributeOptionAdmin(admin.ModelAdmin):
#     list_display = ('display_name', 'attribute', 'value', 'is_default')
#     search_fields = ('display_name', 'value')
#     inlines = [ConditionalRuleInline] # اضافه کردن اینلاین قوانین


# فراموش نکنید مدل ConditionalRule را هم ثبت کنید تا به صورت مستقل هم قابل ویرایش باشد
@admin.register(ConditionalRule)
class ConditionalRuleAdmin(admin.ModelAdmin):
    form = ConditionalRuleForm
    list_display = ('name', 'trigger_option', 'action_type', 'target_object')
    list_filter = ('action_type',)


# به جای admin.TabularInline از nested_admin.NestedTabularInline استفاده می‌کنیم
class AttributeOptionInline(nested_admin.NestedTabularInline):
    model = AttributeOption
    extra = 0
    sortable_field_name = "display_order" # قابلیت drag-and-drop برای مرتب‌سازی

# به جای admin.TabularInline از nested_admin.NestedStackedInline استفاده می‌کنیم
class AttributeInline(nested_admin.NestedStackedInline):
    model = Attribute
    extra = 0
    sortable_field_name = "display_order"
    # این خط جادویی، اینلاین تو در تو را ممکن می‌کند
    inlines = [AttributeOptionInline]

# به جای admin.ModelAdmin از nested_admin.NestedModelAdmin استفاده می‌کنیم
@admin.register(AttributeGroup)
class AttributeGroupAdmin(nested_admin.NestedModelAdmin):
    list_display = ('display_name', 'name', 'display_order')
    # حالا اینلاین Attribute را که خودش حاوی اینلاین Option است، اضافه می‌کنیم
    inlines = [AttributeInline]


class OrderSelectionInline(admin.TabularInline):
    """
    نمایش و ویرایش انتخاب‌های هر سفارش (OrderSelection)
    به صورت inline در صفحه‌ی سفارش
    """
    model = OrderSelection
    extra = 0  # تعداد فرم خالی برای افزودن ردیف جدید
    fields = ('attribute', 'selected_option', 'value')
    autocomplete_fields = ('attribute', 'selected_option')
    show_change_link = True  # لینک ورود به صفحه‌ی جزئیات رکورد


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    پنل پیشرفته مدیریت سفارش‌ها
    """
    list_display = (
        'id',
        'user_display',
        'colored_status',
        'quantity',
        'created_at',
        'updated_at',
    )
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email', 'id')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderSelectionInline]
    ordering = ('-created_at',)
    list_per_page = 25

    def user_display(self, obj):
        return obj.user.username if obj.user else "کاربر حذف‌شده"
    user_display.short_description = "کاربر"

    # نمایش رنگی وضعیت‌ها در لیست
    def colored_status(self, obj):
        color_map = {
            'pending': '#e6b800',     # زرد
            'processing': '#007bff',  # آبی
            'completed': '#28a745',   # سبز
            'canceled': '#dc3545',    # قرمز
        }
        color = color_map.get(obj.status, 'black')
        return f'<b style="color:{color}">{obj.get_status_display()}</b>'
    colored_status.allow_tags = True
    colored_status.short_description = "وضعیت سفارش"


@admin.register(OrderSelection)
class OrderSelectionAdmin(admin.ModelAdmin):
    """
    صفحه جداگانه برای مشاهده و مدیریت OrderSelection‌ها (اختیاری)
    """
    list_display = (
        'id',
        'order_display',
        'attribute_display',
        'selected_option_display',
        'value',
    )
    list_filter = ('attribute',)
    search_fields = (
        'order__id',
        'attribute__display_name',
        'selected_option__display_name',
        'value',
    )
    autocomplete_fields = ('order', 'attribute', 'selected_option')
    ordering = ('-id',)

    def order_display(self, obj):
        return f"#{obj.order.id}"
    order_display.short_description = "شناسه سفارش"

    def attribute_display(self, obj):
        return obj.attribute.display_name
    attribute_display.short_description = "ویژگی"

    def selected_option_display(self, obj):
        return obj.selected_option.display_name if obj.selected_option else "-"
    selected_option_display.short_description = "گزینه انتخابی"


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    search_fields = ['display_name']
    list_display = ['id', 'display_name']


@admin.register(AttributeOption)
class AttributeOptionAdmin(admin.ModelAdmin):
    search_fields = ['display_name']
    list_display = ['id', 'display_name', 'attribute']
    autocomplete_fields = ['attribute']
