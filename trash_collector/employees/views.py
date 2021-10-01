from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from datetime import date
from django.apps import apps
from .models import Employee



@login_required
def index(request):
    # The following line will get the logged-in user (if there is one) within any view function
    Customer = apps.get_model('customers.Customer')
    logged_in_user = request.user

    if request.method == "POST":
        today = date.today()
        id_from_form = request.POST.get('id')

        completed_customer = Customer.objects.get(id=id_from_form)
        completed_customer.date_of_last_pickup = today

        completed_customer.balance += 20
        completed_customer.save()

        return HttpResponseRedirect(reverse('employees:index'))

    try:
        # This line will return the customer record of the logged-in user if one exists
        logged_in_employee = Employee.objects.get(user=logged_in_user)
        employee_zip_code = logged_in_employee.zip_code
        today = date.today()

        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        day_of_week = days[today.weekday()]

        customer_match = Customer.objects.filter(zip_code=employee_zip_code)\
            .filter(weekly_pickup=day_of_week)\
            .exclude(date_of_last_pickup=today)\
            .exclude(suspend_start__gte=today)\
            .exclude(suspend_end__lte=today)\
            .exclude(one_time_pickup=today)
        one_day_match = Customer.objects.filter(zip_code=employee_zip_code)\
            .filter(one_time_pickup=today)\
            .exclude(date_of_last_pickup=today)\

        context = {
            'logged_in_employee': logged_in_employee,
            'today': today,
            'day_of_week': day_of_week,
            'customer_match': customer_match,
            'one_day_match': one_day_match
        }
        return render(request, 'employees/index.html', context)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('employees:create'))

@login_required
def create(request):
    logged_in_user = request.user
    if request.method == "POST":
        name_from_form = request.POST.get('name')
        address_from_form = request.POST.get('address')
        zip_from_form = request.POST.get('zip_code')
        new_employee = Employee(name=name_from_form, user=logged_in_user, address=address_from_form, zip_code=zip_from_form)
        new_employee.save()
        return HttpResponseRedirect(reverse('employees:index'))
    else:
        return render(request, 'employees/create.html')

@login_required
def edit_profile(request):
    logged_in_user = request.user
    logged_in_employee = Employee.objects.get(user=logged_in_user)
    if request.method == "POST":
        name_from_form = request.POST.get('name')
        address_from_form = request.POST.get('address')
        zip_from_form = request.POST.get('zip_code')
        logged_in_employee.name = name_from_form
        logged_in_employee.address = address_from_form
        logged_in_employee.zip_code = zip_from_form
        logged_in_employee.save()
        return HttpResponseRedirect(reverse('employees:index'))
    else:
        context = {
            'logged_in_employee': logged_in_employee
        }
        return render(request, 'employees/edit_profile.html', context)


def weekday_pickup_search(request):
    Customer = apps.get_model('customers.Customer')
    logged_in_user = request.user

    logged_in_employee = Employee.objects.get(user=logged_in_user)
    employee_zip_code = logged_in_employee.zip_code

    if request.method == "POST":
        weekday_from_form = request.POST.get('days')

        customer_match = Customer.objects.filter(zip_code=employee_zip_code)\
            .filter(weekly_pickup=weekday_from_form)\

        selected_day = weekday_from_form

        context = {
            'customer_match': customer_match,
            'logged_in_employee': logged_in_employee,
            'selected_day': selected_day,
        }

        return render(request, 'employees/weekday_pickup_search.html', context)
    else:
        today = date.today()

        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        today_weekday = days[today.weekday()]

        customer_match = Customer.objects.filter(zip_code=employee_zip_code)\
            .filter(weekly_pickup=today_weekday)

        selected_day = today_weekday

        context = {
            'customer_match': customer_match,
            'logged_in_employee': logged_in_employee,
            'selected_day': selected_day
        }
        return render(request, 'employees/weekday_pickup_search.html', context)



# TODO: Create a function for each path created in employees/urls.py. Each will need a template as well.


# def index(request):
#     # This line will get the Customer model from the other app, it can now be used to query the db for Customers
#     Customer = apps.get_model('customers.Customer')
#     return render(request, 'employees/index.html')
