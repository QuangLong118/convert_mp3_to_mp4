# Hàm băm
import hashlib

def SHA256(file_data):
    # Tạo đối tượng băm SHA256
    sha256_hash = hashlib.sha256()
    
    # Cập nhật dữ liệu vào đối tượng băm
    sha256_hash.update(file_data)
    
    # Lấy mã băm dưới dạng hex
    hex_digest = str(sha256_hash.hexdigest())
    
    return hex_digest

# Chia file audio
from pydub import AudioSegment
import math

def split_mp3(input_file,hash_file):
    # Load file MP3
    audio = AudioSegment.from_mp3(input_file)

    # Độ dài của mỗi đoạn (10 giây = 30000 milliseconds)
    chunk_length_ms = 10 * 1000

    # Tính toán số đoạn cần cắt
    num_chunks = math.ceil(len(audio) / chunk_length_ms)

    # Vòng lặp cắt file âm thanh thành nhiều đoạn
    for i in range(num_chunks):
        start_time = i * chunk_length_ms
        end_time = min((i + 1) * chunk_length_ms, len(audio))
        chunk = audio[start_time:end_time]
        
        # Đặt tên cho file đầu ra
        output_file = f"upload/static/convert_mp3_to_mp4/files/{hash_file}/mp3_split_folder/mp3_split_{i + 1}.mp3"
        
        # Lưu file MP3 đã cắt
        chunk.export(output_file, format="mp3")
        # print(f"Đã lưu {output_file}")
    
    print("Hoàn thành cắt file âm thanh.")
    return num_chunks
    
#Chuyển audio thành text
import requests
import time

# Đọc file âm thanh
def read_file(file_path, chunk_size=5242880):
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            yield data
            
def convert_mp3_to_text(audio_file_path):
    # API endpoint và API key
    upload_endpoint = "https://api.assemblyai.com/v2/upload"
    transcribe_endpoint = "https://api.assemblyai.com/v2/transcript"
    api_key = "2e9ba3f7635f4df68e601c27fb7309fa"
    
    # Bước 1: Tải file lên AssemblyAI
    headers = {'authorization': api_key}
    upload_response = requests.post(upload_endpoint, headers=headers, data=read_file(audio_file_path))
    audio_url = upload_response.json()['upload_url']

    # Bước 2: Yêu cầu nhận diện giọng nói
    transcript_request = {
        'audio_url': audio_url,
        'language_code': 'vi'
    }
    transcript_response = requests.post(transcribe_endpoint, json=transcript_request, headers=headers)
    transcript_id = transcript_response.json()['id']

    # Bước 3: Chờ và lấy kết quả
    polling_endpoint = f"{transcribe_endpoint}/{transcript_id}"
    while True:
        polling_response = requests.get(polling_endpoint, headers=headers)
        status = polling_response.json()['status']
        
        if status == 'completed':
            return str(polling_response.json()['text'])
        elif status == 'failed':
            return None
        else:
            print("Processing...")
            time.sleep(5)
            
#Dịch từ tiếng Việt sang tiếng Anh
from googletrans import Translator

def translate(text):
    # Khởi tạo đối tượng Translator
    translator = Translator()

    # Dịch sang tiếng Anh
    translated = translator.translate(text, src='vi', dest='en')

    # # In kết quả dịch
    # print("Original Text:", text)
    # print("Translated Text:", translated.text)
    return translated.text


#Tạo ảnh từ text
from diffusers import StableDiffusionPipeline
import torch
from PIL import Image

def create_image_from_text(prompt,hash_file,i):
    # Khởi tạo pipeline với mô hình Stable Diffusion
    pipe = StableDiffusionPipeline.from_pretrained("CompVis/stable-diffusion-v1-4", torch_dtype=torch.float16)
    pipe = pipe.to("cuda")

    # Sinh ảnh từ văn bản
    image = pipe(prompt).images[0]

    # Lưu ảnh vào file
    image.save(f"upload/static/convert_mp3_to_mp4/files/{hash_file}/image_folder/image_{i + 1}.png")

    # # Hiển thị ảnh
    # image.show()

# Tạo video từ những ảnh và audio tương ứng
from moviepy.editor import *

# Danh sách các ảnh và âm thanh
def create_video_from_image_and_audio(hash_file,num_chunks):
    # Danh sách ảnh    
    images = []
    for i in range(num_chunks):
        images.append(f"upload/static/convert_mp3_to_mp4/files/{hash_file}/image_folder/image_{i+1}.png")
    # Danh sách audio
    audios = []
    for i in range(num_chunks):
        audios.append(f"upload/static/convert_mp3_to_mp4/files/{hash_file}/mp3_split_folder/mp3_split_{i+1}.mp3")
    # Danh sách các đoạn video đã ghép
    video_clips = []

    for img, audio in zip(images, audios):
        # Tạo đoạn video từ ảnh
        image_clip = ImageClip(img).set_duration(AudioFileClip(audio).duration)
        
        # Thêm âm thanh vào đoạn video
        audio_clip = AudioFileClip(audio)
        video_clip = image_clip.set_audio(audio_clip)
        
        # Thêm đoạn video vào danh sách
        video_clips.append(video_clip)

    # Ghép các đoạn video lại thành một video hoàn chỉnh
    final_video = concatenate_videoclips(video_clips, method="compose")

    # Lưu video ra file
    final_video.write_videofile(f"upload/static/convert_mp3_to_mp4/files/{hash_file}/video/{hash_file}.mp4", fps=24)

    print("Video đã được tạo thành công.")

# Chương trình chính : Tạo video từ audio
import os
def convert(file_path):
    with open (file_path,'rb') as file:
        data = file.read()
        
    hash_file = SHA256(data)

    os.makedirs(f"upload/static/convert_mp3_to_mp4/files/{hash_file}/mp3_split_folder")
    os.makedirs(f"upload/static/convert_mp3_to_mp4/files/{hash_file}/image_folder")
    os.makedirs(f"upload/static/convert_mp3_to_mp4/files/{hash_file}/video")

    num_chunks = split_mp3(file_path,hash_file)

    for i in range(num_chunks):
        text = convert_mp3_to_text(f"upload/static/convert_mp3_to_mp4/files/{hash_file}/mp3_split_folder/mp3_split_{i+1}.mp3")
        prompt = translate(text)
        create_image_from_text(prompt,hash_file,i)
        
    create_video_from_image_and_audio(hash_file,num_chunks)

    print("Tạo video thành công")
    print("Đường dẫn đến file :"+ os.path.abspath(f"upload/static/convert_mp3_to_mp4/files/{hash_file}/video/{hash_file}.mp4") )