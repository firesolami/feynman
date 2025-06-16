from dotenv import load_dotenv
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

load_dotenv()


@login_required
def index(request):
    return render(request, "index.html")


@csrf_exempt
def generate_summary(request):
    if request.method == "POST" and request.FILES.get("media"):
        uploaded_file = request.FILES["media"]

        if not is_valid_media_file(uploaded_file):
            return JsonResponse(
                {"error": "Invalid file type. " "Only audio and video files are allowed."},
                status=400,
            )

        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
            api_key=os.getenv("CLOUDINARY_API_KEY"),
            api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        )

        response = cloudinary.uploader.upload(uploaded_file, resource_type="video")

        aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(response["secure_url"])
        cloudinary.uploader.destroy(response["public_id"])
        summary_content = generate_summary_from_transcription(transcript.text)
        request.session["generated_content"] = summary_content

        return JsonResponse({"content": summary_content})
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)


def is_valid_media_file(file):
    valid_mime_types = ["audio/", "video/"]
    return any(file.content_type.startswith(mime_type) for mime_type in valid_mime_types)


@csrf_exempt
def save_summary(request):
    if request.method == "POST":
        summary_title = request.POST["text"]
        generated_content = request.session["generated_content"]
        summary = Summary(
            user=request.user,
            summary_title=summary_title,
            generated_content=generated_content,
        )
        summary.save()

        return redirect("/summary-list/")
    else:
        return redirect("/")


def delete_summary(request, pk):
    summary = Summary.objects.get(id=pk)
    if request.user == summary.user:
        summary.delete()
        return redirect("/summary-list/")
    else:
        return redirect("/")


def generate_summary_from_transcription(transcription):
    API_KEY = os.getenv("GENAI_API_KEY")

    genai.configure(api_key=API_KEY)

    text_to_summarize = (
        "Based on the following transcript from a "
        "lecture audio, write a lecture summary, write it based on the "
        "transcript, make it look like a summary with all the key points "
        "mentioned, do not add points that were not mentioned in the transcript, "
        "List out everything said in the transcript first then show the summary "
        f"separately:\n\n{transcription}\n\n Summary:"
    )

    model = genai.GenerativeModel("gemini-2.0-flash")

    response = model.generate_content(text_to_summarize)

    generated_content = response.text

    # print(generated_content)

    return format_text_for_frontend(generated_content)


def format_text_for_frontend(text):
    # Remove markdown-style headers
    text = text.replace("#", "")

    # Split into lines for processing
    lines = text.split("\n")[0:]
    formatted_lines = []
    current_list_items = []

    for line in lines:
        line = line.strip()

        # Skip empty lines but preserve them for paragraph breaks
        if not line:
            # If we have accumulated list items, close the list
            if current_list_items:
                formatted_lines.append('<ul style="margin-bottom: 15px; padding-left: 20px; list-style-type: disc;">')
                formatted_lines.extend(current_list_items)
                formatted_lines.append("</ul>")
                current_list_items = []
            formatted_lines.append("")
            continue

        # Handle bold text (markdown style)
        if line.startswith("**"):
            bold_text = line.strip().replace("**", "")
            formatted_lines.append(f'<strong style="font-weight: bold;">{bold_text}</strong>')

        # Handle section headers (lines ending with colon and typically capitalized)
        elif line.endswith(":") and len(line) > 3 and any(word[0].isupper() for word in line.split() if word):
            # Close any open list first
            if current_list_items:
                formatted_lines.append('<ul style="margin-bottom: 15px; padding-left: 20px; list-style-type: disc;">')
                formatted_lines.extend(current_list_items)
                formatted_lines.append("</ul>")
                current_list_items = []
            formatted_lines.append(f'<h4 style="margin-top: 20px; margin-bottom: 10px; font-size: 1.2em;">{line}</h4>')

        # Handle bullet points (lines starting with * or -)
        elif line.startswith("* ") or line.startswith("- "):
            bullet_text = line[2:].strip()
            current_list_items.append(f'<li style="margin-bottom: 8px; line-height: 1.6;">{bullet_text}</li>')

        # Handle numbered points (1. 2. etc.)
        elif len(line) > 3 and line[0:3].replace(".", "").replace(")", "").replace(" ", "").isdigit() and (". " in line or ") " in line):
            # Close any open unordered list first
            if current_list_items:
                formatted_lines.append('<ul style="margin-bottom: 15px; padding-left: 20px; list-style-type: disc;">')
                formatted_lines.extend(current_list_items)
                formatted_lines.append("</ul>")
                current_list_items = []
            formatted_lines.append(f'<p style="margin-bottom: 10px; line-height: 1.6; padding-left: 20px;"><strong>{line}</strong></p>')

        # Regular paragraphs
        else:
            # Close any open list first
            if current_list_items:
                formatted_lines.append('<ul style="margin-bottom: 15px; padding-left: 20px; list-style-type: disc;">')
                formatted_lines.extend(current_list_items)
                formatted_lines.append("</ul>")
                current_list_items = []
            formatted_lines.append(f'<p style="margin-bottom: 15px; line-height: 1.6; text-align: justify;">{line}</p>')

    # Close any remaining open list
    if current_list_items:
        formatted_lines.append('<ul style="margin-bottom: 15px; padding-left: 20px; list-style-type: disc;">')
        formatted_lines.extend(current_list_items)
        formatted_lines.append("</ul>")

    # Join lines and clean up
    formatted_text = "\n".join(formatted_lines)

    # Remove excessive empty paragraphs
    formatted_text = formatted_text.replace('<p style="margin-bottom: 15px; line-height: 1.6; text-align: justify;"></p>', "")

    # Add overall container styling
    formatted_text = f'<div style="font-family: system-ui, -apple-system, sans-serif; color: #374151; max-width: 100%; line-height: 1.6;">{formatted_text}</div>'

    return formatted_text


def summary_list(request):
    summaries = Summary.objects.filter(user=request.user)
    return render(request, "all-summaries.html", {"summaries": summaries})


def summary_details(request, pk):
    summary_detail = Summary.objects.get(id=pk)
    if request.user == summary_detail.user:
        return render(request, "summary-detail.html", {"summary_detail": summary_detail})
    else:
        return redirect("/")


def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            error_message = "Invalid username or password"
            return render(request, "login.html", {"error_message": error_message})

    return render(request, "login.html")


def user_signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        repeatPassword = request.POST["repeatPassword"]

        if password == repeatPassword:
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
                login(request, user)
                return redirect("/")
            except Exception:
                error_message = "Error creating account"
                return render(request, "signup.html", {"error_message": error_message})
        else:
            error_message = "Password do not match"
            return render(request, "signup.html", {"error_message": error_message})

    return render(request, "signup.html")


def user_logout(request):
    logout(request)
    return redirect("/")


def ping(request):
    return JsonResponse({"data": "pong"})
