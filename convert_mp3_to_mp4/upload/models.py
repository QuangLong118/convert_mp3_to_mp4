from django.db import models
from django.db import models
import hashlib
# Create your models here.


class AudioFile(models.Model):
    mp3_file = models.FileField(upload_to='upload/static/convert_mp3_to_mp4/files')
    mp4_file = models.FileField(upload_to='upload/static/convert_mp3_to_mp4/files', null=True, blank=True)

