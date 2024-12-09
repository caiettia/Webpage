from django.shortcuts import render, redirect
from django.core.mail import send_mail
from .forms import ContactForm

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Check honeypot field
            if form.cleaned_data['honeypot']:
                return redirect('contact')  # Redirect if honeypot is filled

            # Send email
            send_mail(
                f"Contact Form Submission from {form.cleaned_data['name']}",
                form.cleaned_data['message'],
                form.cleaned_data['email'],
                ['andrew.caietti@gmail.com'],  # Replace with your email
            )
            return redirect('contact')  # Redirect after successful submission
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})