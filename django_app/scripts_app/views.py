# scripts_app/views.py (completa las dos vistas)

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Script
import subprocess
import os
from django.conf import settings

@login_required
def home(request):
    scripts = Script.objects.all()
    return render(request, 'scripts_app/home.html', {'scripts': scripts})

@login_required
def run_script(request, script_id):
    script = get_object_or_404(Script, id=script_id)
    script_path = script.file_path

    try:
        result = subprocess.run(['python', script_path], capture_output=True, text=True, timeout=60)
        output = result.stdout
        error = result.stderr
    except Exception as e:
        output = ''
        error = str(e)

    return render(request, 'scripts_app/output.html', {
        'script': script,
        'output': output,
        'error': error,
    })
