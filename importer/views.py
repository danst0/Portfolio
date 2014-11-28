
# Create your views here.



from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from importer.models import Document
from importer.forms import DocumentForm
from django.http import HttpResponse


@login_required
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
    return render_to_response('list.html',
                              {'block_title': 'Import',
                               'active_nav': '#nav_import',
                               'documents': documents,
                               'form': form},
                              context_instance=RequestContext(request))

def do_update(request):
    documents = Document.objects.all()
    # print(documents)
    Document.objects.filter(imported=True).delete()
    for document in documents:
        document.update()
        document.imported = True
        document.save()
    return HttpResponse('')
