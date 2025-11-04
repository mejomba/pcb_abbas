from django.contrib import admin
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.urls import path
from django.utils.safestring import mark_safe

from .models import AttributeGroup, Attribute, AttributeOption, ConditionalRule, Order, OrderSelection, Attribute, \
    AttributeOption, OrderReadOnly, OrderPayment
from django.contrib.contenttypes.admin import GenericTabularInline

import nested_admin
from dal import autocomplete
from django.http import HttpResponse, JsonResponse
import pandas as pd
from io import BytesIO
from django.utils.html import format_html
from django.urls import reverse



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
        'created_at',
        'updated_at',
    )
    list_filter = ('status', 'created_at')
    search_fields = ('user__phone', 'id', 'status')
    # search_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderSelectionInline]
    ordering = ('-created_at',)
    list_per_page = 25
    autocomplete_fields = ['user']
    change_list_template = "pcb/order/change_list.html"

    def save_model(self, request, obj, form, change):
        if change:
            original_obj = Order.objects.get(pk=obj.pk)
            if not original_obj.quotation.name and obj.quotation.name:
                if obj.status != self.model.OrderStatus.QUOTATION:
                    obj.status = self.model.OrderStatus.QUOTATION

        super().save_model(request, obj, form, change)

    def get_search_results(self, request, queryset, search_term):
        # جستجوی سفارشی
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        matching_statuses = [
            key for key, display_name in Order.OrderStatus.choices
            if search_term in display_name
        ]

        if matching_statuses:
            status_qs = Order.objects.filter(status__in=matching_statuses)
            queryset |= status_qs
        try:
            search_term_as_int = int(search_term)
            queryset |= self.model.objects.filter(id=search_term_as_int)
        except ValueError:
            pass
        return queryset, use_distinct

    def user_display(self, obj):
        return obj.user.phone if obj.user else "کاربر حذف‌شده"
    user_display.short_description = "کاربر"

    # نمایش رنگی وضعیت‌ها در لیست
    def colored_status(self, obj):
        color_map = {
            self.model.OrderStatus.PENDING: '#e6b800',     # زرد
            self.model.OrderStatus.QUOTATION: '#6325a1',     # بنفش
            self.model.OrderStatus.PROCESS: '#3253a8',  # آبی
            self.model.OrderStatus.PENDING_DELIVERY: '#007bff',  # آبی
            self.model.OrderStatus.DELIVER: '#32a852',   # سبز
            self.model.OrderStatus.CANCELED: '#a12525',   # قرمز
        }
        color = color_map.get(obj.status, 'black')
        return mark_safe(f'<b style="color:{color}">{obj.get_status_display()}</b>')

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('ajax-search/', self.admin_site.admin_view(self.ajax_search), name='order_ajax_search'),
        ]
        return custom_urls + urls

    def ajax_search(self, request):
        """Ajax endpoint برای جستجو در سفارش‌ها"""
        query = request.GET.get('q', '')

        f = Q(user__phone__icontains=query)
        queryset = Order.objects.filter(f)

        matching_statuses = [
            key for key, display_name in self.model.OrderStatus.choices
            if query in display_name
        ]
        if matching_statuses:
            status_qs = Order.objects.filter(status__in=matching_statuses)
            queryset |= status_qs

        results = list(queryset.values(
            'id', 'user__phone', 'status', 'created_at', 'updated_at'
        )[:20])  # محدود به 20 نتیجه
        for d in results:
            d['status_display'] = dict(Order.OrderStatus.choices).get(d['status'], d['status'])
        return JsonResponse({'results': results})

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


class ReadOnlyOrderSelectionInline(admin.TabularInline):
    """
    نمایش فقط‌خواندنی انتخاب‌های سفارش
    """
    model = OrderSelection
    extra = 0
    fields = ('attribute', 'selected_option', 'value')
    autocomplete_fields = ('attribute', 'selected_option')
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class PostFileInline(admin.TabularInline):
    model = OrderPayment
    extra = 0
    readonly_fields = ['file']
    fields = ['file']

    def file_link(self, obj):
        if obj.file:
            return mark_safe(f"<a href='{obj.file.url}' target='_blank'>دانلود</a>")
        return "-"
    file_link.short_description = "فایل"


@admin.register(OrderReadOnly)
class ReadOnlyOrderAdmin(admin.ModelAdmin):
    """
    پنل فقط‌خواندنی برای سفارش‌ها (OrderReadOnly)
    """
    list_display = (
        'id',
        'user_display',
        'colored_status',
        'created_at',
        'updated_at',
        'download_excel_button'
    )
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email', 'id')
    inlines = [ReadOnlyOrderSelectionInline, PostFileInline]
    ordering = ('-created_at',)
    list_per_page = 25

    def download_excel_button(self, obj):
        is_seen = obj.is_seen
        background = '32a852' if is_seen else 'cccccc'
        url = reverse('admin:order_download_excel', args=[obj.id])
        return format_html(
            f'''<a class="button" onclick="this.style.backgroundColor='#32a852'" href="{url}" '
            style="background:#{background};color:white;padding:4px 8px;
            border-radius:4px;text-decoration:none;">📄 دانلود اکسل
            {obj.download_count}
            </a>
            ''',
        )
    download_excel_button.short_description = "اکسل"


    change_form_template = "pcb/admin/order_change_form.html"

    def render_change_form(self, request, context, *args, **kwargs):
        order_id = kwargs.get('object_id')
        context['obj'] = kwargs.get('obj')
        # if order_id:
        #     download_url = reverse('admin:order_download_excel', args=[order_id])
        #     context['adminform'].form.fields['created_at'].help_text = format_html(
        #         f'<a class="button" href="{download_url}" '
        #         f'style="background:#{background};color:white;padding:6px 10px;border-radius:4px;text-decoration:none;">'
        #         f'📄 دانلود اکسل انتخاب‌ها</a>'
        #     )
        return super().render_change_form(request, context, *args, **kwargs)

    # 🔹 مسیر (URL) سفارشی برای ساخت فایل اکسل
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:order_id>/download_excel/',
                self.admin_site.admin_view(self.download_excel),
                name='order_download_excel',
            ),
        ]
        return custom_urls + urls

    # 🔹 تابع تولید فایل اکسل
    def download_excel(self, request, order_id):
        order = Order.objects.get(pk=order_id)
        selections = OrderSelection.objects.filter(order=order)

        data = [
            {
                "attribute_name": s.attribute.display_name,
                "selected_option_name": s.selected_option.display_name if s.selected_option else "",
            }
            for s in selections
        ]

        df = pd.DataFrame(data)
        buffer = BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)

        filename = f"order_{order.id}_selections.xlsx"
        response = HttpResponse(
            buffer,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        order.is_seen = True
        order.download_count += 1
        order.save()
        return response

    # جلوگیری از افزودن، حذف و ویرایش
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        # اجازه مشاهده جزئیات ولی بدون امکان تغییر
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        # تمام فیلدها فقط خواندنی باشند
        return [f.name for f in self.model._meta.fields]

    def user_display(self, obj):
        return obj.user.phone if obj.user else "کاربر حذف‌شده"
    user_display.short_description = "کاربر"

    def colored_status(self, obj):
        color_map = {
            'pending': '#e6b800',
            'processing': '#007bff',
            'completed': '#28a745',
            'canceled': '#dc3545',
        }
        color = color_map.get(obj.status, 'black')
        return mark_safe(f'<b style="color:{color}">{obj.get_status_display()}</b>')
    colored_status.allow_tags = True
    colored_status.short_description = "وضعیت سفارش"



@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    search_fields = ['display_name']
    list_display = ['id', 'display_name']


@admin.register(AttributeOption)
class AttributeOptionAdmin(admin.ModelAdmin):
    search_fields = ['display_name']
    list_display = ['id', 'display_name', 'attribute']
    autocomplete_fields = ['attribute']
