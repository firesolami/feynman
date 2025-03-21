from dotenv import load_dotenv
load_dotenv()
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Summary
import os
import assemblyai as aai
import google.generativeai as genai
import cloudinary
import cloudinary.uploader
import cloudinary.api

@login_required
def index(request):
    return render(request, 'index.html')

@csrf_exempt
def generate_summary(request):
    if request.method == 'POST' and request.FILES.get('media'):
        uploaded_file = request.FILES['media']

        if not is_valid_media_file(uploaded_file):
            return JsonResponse({'error': 'Invalid file type. Only audio and video files are allowed.'}, status=400)

        cloudinary.config( 
            cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'), 
            api_key = os.getenv('CLOUDINARY_API_KEY'), 
            api_secret = os.getenv('CLOUDINARY_API_SECRET')
        )

        response = cloudinary.uploader.upload(uploaded_file, resource_type="video")

        aai.settings.api_key = os.getenv('ASSEMBLYAI_API_KEY')

        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(response["secure_url"])
        cloudinary.uploader.destroy(response["public_id"])
        summary_content = generate_summary_from_transcription(transcript.text)
        request.session['generated_content'] = summary_content


        return JsonResponse({'content': summary_content})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


def is_valid_media_file(file):
    valid_mime_types = ['audio/', 'video/']
    return any(file.content_type.startswith(mime_type) for mime_type in valid_mime_types)

@csrf_exempt
def save_summary(request):
    if request.method == 'POST':
        summary_title = request.POST['text']
        generated_content = request.session['generated_content']
        summary = Summary(user=request.user, summary_title=summary_title, generated_content=generated_content)
        summary.save()

        return redirect('/summary-list/')
    else:
        return redirect('/')
    
def delete_summary(request, pk):
    summary = Summary.objects.get(id=pk)
    if request.user == summary.user:
        summary.delete()
        return redirect('/summary-list/')
    else:
        return redirect('/')

def generate_summary_from_transcription(transcription):
    API_KEY = os.getenv('GENAI_API_KEY')

    genai.configure(api_key=API_KEY)

    text_to_summarize = f"Based on the following transcript from a lecture audio, write a lecture summary, write it based on the transcript, make it look like a summary with all the key points mentioned, do not add points that were not mentioned in the transcript, I repeat do not add points that were not mentioned in the transcript. List out everything said in the transcript first then show the summary separately:\n\n{transcription}\n\n Summary:"

    model = genai.GenerativeModel('gemini-1.5-flash')

    response = model.generate_content(text_to_summarize)

    generated_content = response.text

    return generated_content.replace("#", "")

def summary_list(request):
    summaries = Summary.objects.filter(user=request.user)
    return render(request, "all-summaries.html", {'summaries': summaries})

def summary_details(request, pk):
    summary_detail = Summary.objects.get(id=pk)
    if request.user == summary_detail.user:
        return render(request, 'summary-detail.html', {'summary_detail': summary_detail})
    else:
        return redirect('/')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            error_message = "Invalid username or password"
            return render(request, 'login.html', {'error_message': error_message})

    return render(request, 'login.html')

def user_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repeatPassword = request.POST['repeatPassword']

        if password == repeatPassword:
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
                login(request, user)
                return redirect('/')
            except:
                error_message = 'Error creating account'
                return render(request, 'signup.html', {'error_message': error_message})
        else:
            error_message = 'Password do not match'
            return render(request, 'signup.html', {'error_message': error_message})

    return render(request, 'signup.html')

def user_logout(request):
    logout(request)
    return redirect('/')

def ping(request):
    return JsonResponse({'data': 'pong'})