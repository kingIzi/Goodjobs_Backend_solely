from django.urls import path, include, re_path

from api.views import trigger_error
from firebaseapp.views import get_user_notifications, create_update_firebase
from jobpost.views import *
from myauthentication.views import *
from subscription.views import *
from paymentorder.views import *
from tips.views import *
from analytics.views import user_transaction_summary
from django.contrib import admin





urlpatterns = [
    path('user_transaction_summary/', user_transaction_summary),
    path('create_update_firebase/',create_update_firebase),
    path('get_user_notifications/', get_user_notifications),
    path('fetch_search/',fetch_search),
    path('check_exists_company/',check_exists_company),
    path('add_job_company/',add_job_company),
    path('fetch_job_company/', fetch_job_company),
    path('fetch_job_company_second/', fetch_job_company_second),
    path('add_job_post/',add_job_post),
    path('delete_job_post/',delete_job_post),
    path('add_user_categories/',add_user_categories),
    path('update_user_categories/',update_user_categories),
    path('fetch_job_categories/',fetch_job_categories),
    path('fetch_saved_job_post/', fetch_saved_job_post),
    path('save_job_post/',save_job_post),
    path('unsave_job_post/',unsave_job_post),
    path('fetch_tips/',fetch_tips),
    path('add_tip/',add_tip),
    path('apply_to_job/', apply_to_job),
    path('add_job_category/', add_job_category),
    path('upload_cv/', upload_cv),
    path('check_cv_available/', check_cv_available),
    path('fetch_user_profiles/', fetch_user_profiles),
    path('fetch_job_posts/',fetch_job_posts),
    path('webhook_payment_endpoint/', webhook_payment_endpoint),
    path('create_subscription/', create_subscription),
    path('tutume_create_order/',tutume_create_order),
    path('fetch_subscriptions/', fetch_subscriptions),
    path('fetch_user_subscription/', fetch_user_subscription),
    path('fetch_subscribers/', fetch_subscribers),
    path('fetch_transactions/',fetch_transactions),
    path('fetch_plans/', fetch_plans),
    path('auth/signup/', signup),
    path('auth/resend_otp_code/', resend_otp_code),
    path('auth/login/', login),
    path('auth/pull_user_details/', pull_user_details),
    path('auth/fetch_users/', fetch_users),
    path('auth/update_user_profile/', update_user_profile),
    path('auth/change_current_password/', change_current_password),
    path('auth/forget_password_send_0TP/', forget_password_send_0TP),
    path('auth/verify_forget_password_otp/', verify_forget_password_otp),
    path('auth/verify_signup_otp/', verify_signup_otp),
    path('auth/verify_login_otp/', verify_login_otp),
    path('auth/change_forget_password/', change_forget_password),
    path('auth/verify_user_send_otp/', verify_user_send_OTP),
    path('auth/delete_user_data/', delete_user_data),
    path('rest/', include('rest_framework.urls')),
    path('is_monetization_on/', is_monetization_on),

    # Sentry debug
    path('sentry-debug/', trigger_error),
]