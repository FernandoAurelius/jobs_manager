# kanban.py

import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from workflow.models import Job

def kanban_view(request):
    jobs = Job.objects.all()
    context = {
        'jobs': jobs,
        'status_choices': Job.STATUS_CHOICES,
        'status_tooltips': Job.STATUS_TOOLTIPS,
    }
    return render(request, 'workflow/kanban_board.html', context)


@csrf_exempt
def update_job_status(request, pk):
    if request.method == 'POST':
        try:
            job = Job.objects.get(pk=pk)
            try:
                payload = json.loads(request.body)
                new_status = payload.get('status')
            except json.JSONDecodeError:
                return JsonResponse({'success': False, 'error': 'Invalid JSON'})

            if new_status:
                job.status = new_status
                job.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid status'})
        except Job.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Job not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def fetch_jobs(request, status):
    max_jobs = int(request.GET.get('max_jobs', 10))  # Default to 10 if not provided
    jobs = Job.objects.filter(status=status)[:max_jobs]
    total_jobs = Job.objects.filter(status=status).count()
    displayed_jobs_count = jobs.count()  # x

    job_data = [{
        'id': job.id,
        'name': job.name,
        'description': job.description
    } for job in jobs]

    return JsonResponse({'jobs': job_data, 'total': total_jobs})
