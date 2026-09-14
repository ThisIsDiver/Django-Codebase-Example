from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from requestdataapp.forms import UserBioForm, UploadFileForm

# Create your views here.

def process_get_query(request: HttpRequest) -> HttpResponse:
    a = request.GET.get('a', "")
    b = request.GET.get('b', "")

    result = a + b
    context = {
        "a": a,
        "b": b,
        "result": result,
    }

    return render(request, "requestdataapp/request-query-params.html", context=context)

def user_form(request: HttpRequest) -> HttpResponse:

    context = {
        "form": UserBioForm()
    }

    return render(request, "requestdataapp/user-bio-form.html", context=context)

def handle_file_upload(request: HttpRequest) -> HttpResponse:
    max_size = 10 * 1024 * 1024
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            myfile = form.cleaned_data["file"]
            if myfile.size > max_size:
                return render(
                    request,
                    "requestdataapp/file-upload.html",
                    {
                    "error": "File bigger then 10 Mb. Please, upload smaller file"
                    }
                )
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            print(f"saved {filename}")
    else:
        form = UploadFileForm()

    context = {
        "form": form
    }
    return render(request, "requestdataapp/file-upload.html", context=context)