# Generated by Django 5.0.4 on 2024-08-15 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('upload', '0004_remove_audiofile_uploaded_at_audiofile_mp4_file_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audiofile',
            name='mp3_file',
            field=models.FileField(upload_to='upload/static/convert_mp3_to_mp4/files'),
        ),
        migrations.AlterField(
            model_name='audiofile',
            name='mp4_file',
            field=models.FileField(blank=True, null=True, upload_to='upload/static/convert_mp3_to_mp4/files'),
        ),
    ]
