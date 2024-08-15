from django.shortcuts import render, redirect
from django.http import FileResponse
from .forms import AudioUploadForm
from .models import AudioFile
from upload.static.convert_mp3_to_mp4.google_colab import convert
import hashlib
import os

# Hàm băm
def SHA256(file_path):
    with open (file_path,'rb') as file:
        file_data = file.read()
    
    # Tạo đối tượng băm SHA256
    sha256_hash = hashlib.sha256()
    
    # Cập nhật dữ liệu vào đối tượng băm
    sha256_hash.update(file_data)
    
    # Lấy mã băm dưới dạng hex
    hex_digest = str(sha256_hash.hexdigest())
    
    return hex_digest

def upload_audio(request):
    if request.method == 'POST':
        form = AudioUploadForm(request.POST, request.FILES)
        if form.is_valid():
            print(request.FILES)
            audio_file = form.save()
            return redirect('convert_audio', audio_file_id=audio_file.id)
    else:
        form = AudioUploadForm()
    return render(request, 'upload.html', {'form': form})


def convert_audio(request,audio_file_id):
    audio_file = AudioFile.objects.get(id=audio_file_id)
    mp3_path = audio_file.mp3_file.path
    
    hash_file = SHA256(mp3_path)
    
    # # Mẫu thử
    # mp4_path = f'static/convert_mp3_to_mp4/files/sample/video/example.mp4'
    
    mp4_path = f'static/convert_mp3_to_mp4/files/{hash_file}/video/{hash_file}.mp4'
    
    # Chuyển mp3 thành mp4
    convert(mp3_path)
    
    # # Cập nhật trường mp4_file trong cơ sở dữ liệu
    audio_file.mp4_file.name = os.path.relpath(mp4_path)
    audio_file.save()
    return redirect('display_video', audio_file_id=audio_file.id)
    
    
def display_video(request, audio_file_id):
    if request.method == 'POST':
        return redirect('upload_audio')
    audio_file = AudioFile.objects.get(id=audio_file_id)
    return render(request, 'display_video.html', {'audio_file': audio_file})
    