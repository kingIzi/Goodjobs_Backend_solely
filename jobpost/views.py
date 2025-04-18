import json
import datetime
import traceback
from django.db import transaction
from django.db.models import Q
from firebaseapp.models import FirebaseApp, UserNotification
from myauthentication.models import CustomUser
from utilities.notification_logic import create_user_notification
from .serializers import *
from django.http import JsonResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import UserProfile, JobPost,notify_users_on_new_job
from .serializers import JobPostSerializer
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from decimal import Decimal



from myauthentication.validators import FetchUsersValidator,AddJobCategoryForm,AddJobPostForm
from utilities.file_uploader import upload_file


@csrf_exempt
def fetch_job_posts(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        # Pagination parameters
        page = request.POST.get('page', 1)  # Default to first page if not provided
        page_size = 50  # Number of items per page

        try:
            user_profile = UserProfile.objects.get(user_id=user_id)
            user_categories = user_profile.preferred_categories.all()

            if user_categories.exists():
                jobs = JobPost.objects.filter(categories__in=user_categories)
            else:
                jobs = JobPost.objects.all()

            if not jobs.exists():
                return JsonResponse({'status': 'error', 'message': 'No job posts found', 'status_code': 404},
                                    status=404)

            # Apply pagination
            paginator = Paginator(jobs, page_size)
            try:
                jobs_page = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                jobs_page = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                jobs_page = paginator.page(paginator.num_pages)

            job_serializer = JobPostSerializer(jobs_page, many=True).data
            return JsonResponse({
                'status': 'success',
                'message': 'Job posts fetched successfully',
                'status_code': 200,
                'data': job_serializer,
                'pagination': {
                    'page': int(page),
                    'page_size': page_size,
                    'total': paginator.count,
                    'num_pages': paginator.num_pages,
                }
            }, status=200)

        except UserProfile.DoesNotExist:
            jobs = JobPost.objects.all()
            paginator = Paginator(jobs, page_size)
            try:
                jobs_page = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                jobs_page = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                jobs_page = paginator.page(paginator.num_pages)

            job_serializer = JobPostSerializer(jobs_page, many=True).data
            return JsonResponse({
                'status': 'success',
                'message': 'Job posts fetched successfully',
                'status_code': 200,
                'data': job_serializer,
                'pagination': {
                    'page': int(page),
                    'page_size': page_size,
                    'total': paginator.count,
                    'num_pages': paginator.num_pages,
                }
            }, status=200)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method', 'status_code': 400}, status=400)


@csrf_exempt
def apply_to_job(request):
    user_id = request.POST.get("user_id")
    user = CustomUser.objects.get(id=user_id)
    job_id = request.POST.get('job_id')
    # Check if the user has a CV in their profile
    user_profile, created = UserProfile.objects.get_or_create(user=user)
    if not user_profile.cv:
        return JsonResponse(
            {'status': "error", 'message': 'You need to upload a CV before you can apply', "status_code": 400},
            status=400)

    # Get the job instance
    try:
        job = JobPost.objects.get(id=job_id)
    except JobPost.DoesNotExist:
        return JsonResponse({'error': 'Job not found'}, status=404)

    # Check if the user has already applied
    if JobApplication.objects.filter(user=user, job=job).exists():
        return JsonResponse({'status': "error", 'message': 'You have already applied for this job', "status_code": 400},
                            status=400)

    # Create a new job application
    job_application = JobApplication(
        user=user,
        job=job,
        cv=user_profile
    )
    # # Assuming the cover letter is sent in the request
    # cover_letter = request.data.get('cover_letter', '')
    # if cover_letter:
    #     job_application.cover_letter = cover_letter

    job_application.save()
    # serializer = JobApplicationSerializer(job_application)
    return JsonResponse(
        {'status': 'success', 'message': "You've applied for this job successfully.", "status_code": 200})


@csrf_exempt
def upload_cv(request):
    try:
        if request.method != "POST": raise 'NOT FOUND'
        user_id = request.POST.get('user_id')
        user = CustomUser.objects.get(id=user_id)
        if 'cv' not in request.FILES:
            return JsonResponse({'error': 'No CV file was provided.'}, status=400)

        cv_file = request.FILES['cv']
        if cv_file.size > 1024 * 1024 * 5:  # Limit file size to 5MB
            return JsonResponse({'error': 'The CV file is too large.'}, status=400)

        # Create or update the user profile with the new CV
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        user_profile.cv.save(f'{request.user.username}_{cv_file.name}', cv_file, save=True)
        user_profile_serializer = UserProfileSerializer(user_profile).data
        try:
            user_token = FirebaseApp.objects.get(user=user).token
            data = {
                "title": "CV Uploaded",
                "body": f"{user.username} your cv has been uploaded successfully.",
                "token": user_token
            }
            create_user_notification(data)
            UserNotification.objects.create(user=user, title="CV Uploaded", message=f"{user.username} your cv has "
                                                                                    f"been uploaded successfully.")
        except:
            pass

        return JsonResponse({'status': 'success', 'status_code': 200, 'message': 'CV uploaded successfully.',
                             'data': user_profile_serializer}, status=200, )
    except:
        return JsonResponse({'status': "error", 'message': 'Something went wrong', "status_code": 404},
                            status=404)


@csrf_exempt
def fetch_user_profiles(request):
    try:
        if request.method != "POST": raise 'NOT FOUND'
        
        #user_id = request.POST.get('user_id')
        form = FetchUsersValidator(request.POST)
        if not form.is_valid(): return JsonResponse({'message': form.errors},status=400)
        user_id = form.cleaned_data['user_id']
        
        requesting_user = CustomUser.objects.get(id=user_id)
        # Ensure the requesting user has the necessary permissions to fetch all users
        if not requesting_user.has_perm('paymentorder.view_transactions'):
            return JsonResponse(
                {'status': 'error', 'message': "You don't have permission to perform this action", 'status_code': 403},
                status=403)
        else:
            user_profiles = UserProfile.objects.exclude(cv='')
            user_profile_serializer = UserProfileSerializer(user_profiles, many=True).data
            return JsonResponse(
                {'status': "success", 'message': 'UserProfiles pulled successfully', "data": list(user_profile_serializer),
                "status_code": 200},
                status=200)
    except:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method', 'status_code': 400}, status=400)


@csrf_exempt
def check_cv_available(request):
    user_id = request.POST.get('user_id')
    user_cv = UserProfile.objects.filter(user__id=user_id)
    if user_cv.exists():
        user_profile_serializer = UserProfileSerializer(user_cv.first()).data
        return JsonResponse({'status': 'success', 'status_code': 200, 'message': 'CV available successfully.',
                             'data': user_profile_serializer}, status=200)

    else:
        return JsonResponse({'status': "error", 'message': 'CV not available', "status_code": 404},
                            status=404)


@csrf_exempt
def save_job_post(request):
    user_id = request.POST.get("user_id")
    job_id = request.POST.get("job_id")

    job_post = SavedJobPost.objects.filter(user__id=user_id, job_post__id=job_id)
    if job_post.exists():
        return JsonResponse({'status': "error", 'message': 'Job Already Saved', "status_code": 400},
                            status=400)
    else:
        job = JobPost.objects.get(id=job_id)
        user = User.objects.get(id=user_id)
        new_saved_job = SavedJobPost(user=user, job_post=job)
        new_saved_job.save()
        return JsonResponse({'status': "success", 'message': 'Job post saved successfully', "status_code": 200},
                            status=200)


@csrf_exempt
def unsave_job_post(request):
    user_id = request.POST.get("user_id")
    job_id = request.POST.get("job_id")
    try:
        job_post = SavedJobPost.objects.get(user__id=user_id, job_post__id=job_id)

        job_post.delete()
        return JsonResponse({'status': "success", 'message': 'Job  UnSaved successfully', "status_code": 200},
                            status=200)
    except:
        return JsonResponse({'status': "error", 'message': 'No such saved job', "status_code": 400},
                            status=400)


@csrf_exempt
def fetch_saved_job_post(request):
    user_id = request.POST.get("user_id")

    job_post = SavedJobPost.objects.filter(user__id=user_id, )

    job_post_serializer = SavedJobPostSerializer(job_post, many=True).data
    return JsonResponse(
        {'status': "success", 'message': 'JobSaved pulled successfully', "data": list(job_post_serializer),
         "status_code": 200},
        status=200)


@csrf_exempt
def fetch_job_categories(request):
    try:
        if request.method != 'POST': raise 'NOT POST'
        job_category = JobCategory.objects.all()
        job_category_serializer = JobCategorySerializer(job_category, many=True).data
        return JsonResponse(
            {'status': "success", 'message': 'JobCategory pulled successfully', "data": list(job_category_serializer),
            "status_code": 200},
            status=200)
    except: 
        return JsonResponse({'status': 'error', 'message': 'Invalid request method', 'status_code': 400}, status=400)
    


@csrf_exempt
def add_job_category(request):
    try:
        if request.method != 'POST': raise 'NOT POST'
        form = AddJobCategoryForm(request.POST)
        if not form.is_valid(): return JsonResponse({'message': form.errors},status=400)
        name = form.cleaned_data['name']
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'You must provide a thumbnail'}, status=400)
        image = request.FILES['image']
        job_category,created = JobCategory.objects.get_or_create(name=name,image=image)
        job_category_serializer = JobCategorySerializer(job_category).data
        return JsonResponse({'status': 'success', 'status_code': 200, 'message': 'CV uploaded successfully.',
                             'data': job_category_serializer}, status=200, )
    except: 
        return JsonResponse({'status': 'error', 'message': 'Invalid request method', 'status_code': 400}, status=400)



@csrf_exempt
def add_user_categories(request):
    if request.method == 'POST':
        # Parse the request body as JSON
        data = json.loads(request.body)
        user_id = data.get('user_id')
        # Ensure category_ids is interpreted as a list
        category_ids = data.get('category_ids')  # Provides an empty list as default

        try:
            user = User.objects.get(id=user_id)
            user_profile, created = UserProfile.objects.get_or_create(user=user)

            for category_id in category_ids:
                try:
                    category = JobCategory.objects.get(id=category_id)
                    user_profile.preferred_categories.add(category)
                except JobCategory.DoesNotExist:
                    return JsonResponse({'status': "error", 'error': f'Category ID {category_id} not found.'},
                                        status=404)

            return JsonResponse({'status': "success", 'message': 'Categories added successfully.', "status_code": 200},
                                status=200)

        except UserProfile.DoesNotExist:
            return JsonResponse({'status': "error", 'error': 'UserProfile not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'This endpoint only supports POST requests.'}, status=400)


@csrf_exempt
def update_user_categories(request):
    if request.method == 'POST':
        # Parse the request body as JSON
        data = json.loads(request.body)
        user_id = data.get('user_id')
        category_ids = data.get('category_ids',
                                [])  # Ensure category_ids is interpreted as a list and default to empty if not provided

        try:
            user = User.objects.get(id=user_id)
            user_profile, created = UserProfile.objects.get_or_create(user=user)

            # Clear existing preferred categories before adding new ones
            user_profile.preferred_categories.clear()

            for category_id in category_ids:
                try:
                    category = JobCategory.objects.get(id=category_id)
                    user_profile.preferred_categories.add(category)
                except JobCategory.DoesNotExist:
                    return JsonResponse({'status': "error", 'error': f'Category ID {category_id} not found.'},
                                        status=404)

            return JsonResponse(
                {'status': "success", 'message': 'Categories updated successfully.', "status_code": 200},
                status=200)

        except UserProfile.DoesNotExist:
            return JsonResponse({'status': "error", 'error': 'UserProfile not found.'}, status=404)
        except User.DoesNotExist:
            return JsonResponse({'status': "error", 'error': 'User not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def fetch_search(request):
    search_query = request.POST.get('search_query')
    job_post = JobPost.objects.filter(Q(job_title__icontains=search_query))
    if job_post.exists():

        jobpost_serializer = JobPostSerializer(job_post, many=True).data

        return JsonResponse({'status': 'success', 'message': 'JobPost search successfully', 'status_code': 200,
                             'data': list(jobpost_serializer)}, status=200)
    else:
        return JsonResponse({'status': 'error', 'message': 'JobPost search not found', 'status_code': 404, 'data': []})


@csrf_exempt
def add_job_company(request):
    name = request.POST.get("name")
    about_company = request.POST.get("about_company")

    try:
        if 'company_image' not in request.FILES:
            return JsonResponse({'error': 'No CV file was provided.'}, status=400)

        company_image = request.FILES['company_image']

        Company.objects.create(name=name, about_company=about_company, image=company_image)
        return JsonResponse({'status': 'success', 'status_code': 200, 'message': 'Company Added  successfully.',
                             }, status=200, )
    except:
        return JsonResponse({'status': "error", 'message': 'Something went wrong', "status_code": 404},
                            status=404)


@csrf_exempt
def fetch_job_company(request):
    try:
        if request.method != "POST": raise "NOT POST"
        companies = Company.objects.all()
        company_serializer = CompanySerializer(companies, many=True).data
        return JsonResponse({'status': 'success', 'status_code': 200, 'message': 'Company Fetched successfully.',
                            'data': list(company_serializer)}, status=200, )
    except:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method', 'status_code': 400}, status=400)


@csrf_exempt
def add_job_post(request):
    try:
        if request.method != 'POST': raise 'NOT FOUND'

        # Parse the JSON body of the request
        data = json.loads(request.body)

        # try:
        company_id = data.get("company_id")
        location = data.get("location")
        job_title = data.get("job_title")
        job_type = data.get("job_type")
        salary_min = data.get("salary_min")
        salary_max = data.get("salary_max")
        job_post_url = data.get("job_post_url")
        job_description = data.get("job_description")
        deadline = data.get("deadline")
        category_id = data.get("category_id")  # This should be a list of category IDs

        company = Company.objects.get(id=company_id)
        
        # with transaction.atomic():

        #     # datetime.datetime.strptime(deadline, "%Y-%m-%d").date()
        #     job_post,created = JobPost.objects.create(
        #         company=company, location=location, job_title=job_title, job_type=job_type,
        #         salary_min=Decimal(salary_min).quantize(Decimal("0.01")) if salary_min else None, 
        #         salary_max=Decimal(salary_max).quantize(Decimal("0.01")) if salary_max else None, job_description=job_description,
        #         job_post_url=job_post_url, deadline_day=datetime.datetime.strptime(deadline, "%Y-%m-%d").date(), datetime_posted=timezone.now(),
        #     )

        #     print("GOING THROUGH")

        #     # Link the job post with categories
        #     #category = JobCategory.objects.get(id=category_id)
        #     #job_post.categories.add(category)            
            


        #     transaction.on_commit(lambda: notify_users_on_new_job(JobPost,created=True))

        #     return JsonResponse({'status': 'success', 'status_code': 200, 'message': 'JobPost Added successfully.'},
        #                         status=200)

        try:
            job_post = JobPost.objects.create(
                company=company, location=location, job_title=job_title, job_type=job_type,
                salary_min=Decimal(salary_min).quantize(Decimal("0.01")) if salary_min else None, 
                salary_max=Decimal(salary_max).quantize(Decimal("0.01")) if salary_max else None, job_description=job_description,
                job_post_url=job_post_url, deadline_day=deadline,
            )
        except: 
            pass

        filtered_job_post = JobPost.objects.filter(
                company=company, location=location, job_title=job_title, job_type=job_type,
                salary_min=Decimal(salary_min).quantize(Decimal("0.01")) if salary_min else None, 
                salary_max=Decimal(salary_max).quantize(Decimal("0.01")) if salary_max else None, job_description=job_description,
                job_post_url=job_post_url, deadline_day=deadline,
        )

        if filtered_job_post.exists():
            job_categories = JobPostCategories.objects.create(job_post=filtered_job_post[0],
                                                              job_category_id=JobCategory.objects.get(id=category_id))
            return JsonResponse({'status': 'success', 'status_code': 200, 'message': 'JobPost Added successfully.'},
                                    status=200)

        return JsonResponse({'status': 'error', 'message': 'Failed to add job post', 'status_code': 400}, status=400)
    except Exception as e:
        print("Error occurred:", e) 
        return JsonResponse({'status': 'error', 'message': 'Invalid request method', 'status_code': 400}, status=400)


@csrf_exempt
def delete_job_post(request):
    job_id = request.POST.get("job_id")
    try:
        job_post = JobPost.objects.get(id=job_id)
        job_post.delete()
        return JsonResponse({'status': "success", 'message': 'JobPost Deleted successfully', "status_code": 200},
                            status=200)
    except:
        return JsonResponse({'status': "error", 'message': 'No such job post', "status_code": 400},
                            status=400)