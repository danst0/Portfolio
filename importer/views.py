
# Create your views here.



from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from importer.models import Document
from importer.forms import DocumentForm

def list(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile=request.FILES['docfile'], user=request.user)
            newdoc.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('importer.views.list'))
    else:
        form = DocumentForm() # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.filter(user=request.user)

    # Render list page with the documents and the form
    return render_to_response(
        'list.html',
        {'block_title': 'Minimal Django File Upload Example',
         'documents': documents,
         'form': form},
        context_instance=RequestContext(request)
    )