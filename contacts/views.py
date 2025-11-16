from django.shortcuts import render
from .forms import ContactForm
from .email_service import ContactEmailsService


def contact_view(request):
    success = False

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            success = True
            form = ContactForm()

            ContactEmailsService.send_contact_notification_email(contact)
            ContactEmailsService.send_contact_autoreply_email(contact)
    else:
        form = ContactForm()

    return render(request, "contacts/contact.html", {"form": form, "success": success})
