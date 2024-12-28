from django.utils.translation import gettext_lazy as _


class Messages:
    USERNAME_PASSWORD_MISMATCH = {
        "message": _("اسم المستخدم و / أو كلمة المرور التي حددتها غير صحيحة."),
        "code": "username_password_mismatch"
    }

    PHONE_IN_USE = {
        "message": _("رقم الهاتف موجود مسبقا."),
        "code": "phone_unique"
    }

    USERNAME_IN_USE = {
        "message": _("إسم المستخدم موجود مسبقا."),
        "code": "username_unique"
    }

    EMAIL_IN_USE = {
        "message": _("البريد الإلكتروني موجود مسبقا."),
        "code": "email_unique"
    }

    EMAIL_NOT_FOUND = {
        "message": _("البريد الإلكتروني غير مرتبط بحساب."),
        "code": "email_not_found"
    }

    INVALID_CODE = {
        "message": _("الرمز المدخل غير صحيح."),
        "code": "invalid_code"
    }

    EMAIL_IS_VERIFIED = {
        "message": _("البريد الإلكتروني قد تم تفعيله مسبقا.ً"),
        "code": "email_is_verified"
    }

    EXPONENT_PUSH_TOKEN_FORMAT_ERROR = {
        "message": _("الصيغة المدخلة غير صحيحة، الرجاء إدخال صيغة صحيحة ExponentPushToken[token]."),
        "code": "exponent_push_token_format_error"
    }

    EXPONENT_PUSH_TOKEN_MIN_LENGTH_ERROR = {
        "message": _("الرجاء ادخل قيمة صحيحة للتوكن."),
        "code": "exponent_push_token_min_length_error"
    }

    SERVICE_TIME_ERROR_FORMAT = {
        "message": _("الرجاء ادخل وقت صالح للخدمة، قم بتحديد عدد ساعات ودقائق الخدمة شكل صحيح."),
        "code": "service_time_error_format"
    }

    SERVICE_IN_USE = {
        "message": _("إسم الخدمة قم تم إضافتها مسبقا.ً"),
        "code": "service_unique"
    }

    EMPLOYEE_IN_USE = {
        "message": _("إسم الموظف قم تم إضافته مسبقاً."),
        "code": "employee_unique"
    }

    BANK_IN_USE = {
        "message": _("إسم البنك قم تم إضافته مسبقا.ً"),
        "code": "employee_unique"
    }

    TIME_FROM_AND_TO_ENTRY = {
        "message": _("يجب إدخال قيمة كل من time from و .time to"),
        "code": "time_from_and_to_entry"
    }

    TIME_FROM_AND_TO_FORMAT = {
        "message": _('صيغة الوقت المدخل غير صحيحة.'),
        "code": "time_from_and_to_format"
    }

    DATE_LESS_THAN_CURRENT_DATE = {
        "message": _('يجب ان يكون التاريخ المدخل اكبر او يساوي التاريخ الحالي.'),
        "code": "date_less_than_current_date"
    }

    TOTAL_TIME_EQUAL_OR_LESS_THAN_SERVICE_TOTAL_TIME = {
        "message": _("يجب ان يكون وقت العمل مناسب مع وقت الخدمة ومضاعفته."),
        "code": "total_time_equal_service_total_time"
    }

    EMPLOYEE_ALREADY_EXISTS_AVAILABILITY = {
        "message": _("الموظف موجد مسبقا في خدمة أخرى بهذا التوقيت."),
        "code": "employee_already_exists_availability"
    }

    SERVICE_ALREADY_EXISTS_AVAILABILITY = {
        "message": _("الخدمة موجوده مسبقا بهذا التاريخ {} - {} - {}في جدول ألإتاحة."),
        "code": "service_already_exists_availability"
    }

    CODE_ALREADY_EXISTS = {
        "message": _("الكود المدخل مرتبط بمستخدم اخر."),
        "code": "code_already_exists"
    }

    ORDER_ITEM_EMPTY_ERROR = {
        "message": _("يجب إدخال قيم الى عناصر الطلب."),
        "code": "order_item_empty_error"
    }

    OFFER_EXPIRE_ERROR = {
        "message": _("كود الخصم المدخل غير صالح."),
        "code": "offer_expire_error"
    }

    EMPLOYEE_EMPTY_ERROR = {
        "message": _("يجب إدخال اسم الموظف الذي يقوم بالخدمة."),
        "code": "employee_empty_error"
    }

    START_LESS_THAN_END_ERROR = {
        "message": _("يجب ان يكون تاريخ البداية اصغر من تاريخ النهاية."),
        "code": "start_less_than_end_error"
    }

    CHANGE_ORDER_STATUS_ERROR = {
        "message": _("لا يمكنك تعديل حالة هذا الطالب."),
        "code": "change_order_status_error"
    }

    ORDER_AVAILABILITY_LESS_THAN_CURRENT_DATE_ERROR = {
        "message": _("لا يمكنك الحجز في هذا التاريخ. يجب ان يكون التاريخ المرسل اكبر من التاريخ الحالي."),
        "code": "order_availability_less_than_current_date_error"
    }

    ORDER_AVAILABILITY_UNIQUE_ERROR = {
        "message": _("لا يمكنك الحجز بهذا التاريخ، الخدمة غير متاحة."),
        "code": "order_availability_unique_error"
    }

    ORDER_PAY_BALANCE_LESS_THAN_PRICE_ERROR = {
        "message": _("لا يمكنك الدفع المبلغ المرسل اقل من قيمة الخدمة"),
        "code": "order_pay_balance_less_than_price_error"
    }

    WALLET_WITHDRAW_ERROR = {
        "message": _("فشلت عملية السحب المبلغ المسحوب اكبر من الرصيد."),
        "code": "wallet_withdraw_error"
    }

    GET_PAYMENT_PAGE_ERROR = {
        "message": _("فشلت عملية الحصول على رابط الصفحة الرجاء المحاولة لاحقاً"),
        "code": "get_payment_page_error_error"
    }

    PAYMENT_HANDLE_ERROR = {
        "message": _("فشلت عملية الدفع الرجاء المحاولة لاحقاً"),
        "code": "payment_handle_error"
    }

    ADDRESS_REQUIRED_ERROR = {
        "message": _("الرجاء إدخال عنوانك ليتم تحديده للبائع"),
        "code": "address_required_error"
    }

    OFFER_FORMAT_ERROR = {
        "message": _("يجب أن  يكون الكود مزيجًا من الأحرف الأبجدية والأرقام"),
        "code": "offer_format_error"
    }

    PAY_VIA_WALLET_ERROR = {
        "message": _("لا يمكنك إكمال الدفع عبر الراجحي، المحفظة تحتوي على المبلغ الكافي"),
        "code": "pay_via_wallet_error"
    }

    COMMENT_OBJECT_ERROR = {
        "message": _("الرجاء تمرير قيمة صحيحة للـ comment_object"),
        "code": "comment_object_error"
    }
