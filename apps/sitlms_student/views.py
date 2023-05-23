from django.shortcuts import render
from calendar import monthcalendar
from datetime import datetime, timedelta
import calendar
from django.http import JsonResponse,HttpResponse
from django.template.loader import render_to_string
from dateutil.relativedelta import relativedelta

# Create your views here.


def student_profile(request):
    # Get the current date from the URL parameters
    date_str = request.GET.get('date', datetime.now().strftime('%Y-%m-%d'))
    date = datetime.strptime(date_str, '%Y-%m-%d')

    # Calculate the previous and next month values
    prev_month = date - relativedelta(months=1)
    next_month = date + relativedelta(months=1)

    prev_date = prev_month.replace(day=1).strftime('%Y-%m-%d')
    next_date = next_month.replace(day=1).strftime('%Y-%m-%d')

    # Generate the calendar data for the specified month
    cal = calendar.monthcalendar(date.year, date.month)

    # Get the current month's name and year
    month_name = date.strftime('%B')
    year = date.year

    # Prepare the calendar data with event information
    events = {
        5: ['Meeting 1', 'Meeting 2'],
        12: ['Appointment'],
        20: ['Conference'],
        25: ['Workshop', 'Training'],
    }

    calendar_data = []
    for week in cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append((" ", []))
            else:
                events_for_day = events.get(day, [])
                week_data.append((day, events_for_day))
        calendar_data.append(week_data)

    # Render the calendar template with the calendar data, navigation parameters, month name/year, and events
    return render(request, 'student_module/student.html', {
        'calendar': calendar_data,
        'prev_date': prev_date,
        'next_date': next_date,
        'month_name': month_name,
        'year': year,
        'events': events,
    })


def student_course_details(request):
    
    """ This function renders the student page course details """
    
    return render(request, 'student_module/courses_details.html')


def student_edit_profile(request):
    
    """ This function renders the student edit profile"""
    
    return render(request, 'student_module/edit_profile.html')