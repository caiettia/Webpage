from django.contrib import admin
from .models import Project, Tag
from django.http import HttpResponseRedirect
from django.urls import path
from django.shortcuts import render
from .forms import UploadFileForm

@admin.action(description='Upload new records')
def upload_records(modeladmin, request, queryset):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Handle file upload and create new Project records
            # Example: process the uploaded file and create Project instances
            # ...
            return HttpResponseRedirect(request.get_full_path())
    else:
        form = UploadFileForm()
    return render(request, 'admin/upload_form.html', {'form': form})

class ProjectAdmin(admin.ModelAdmin):
    actions = [upload_records]

admin.site.register(Project, ProjectAdmin)
admin.site.register(Tag)