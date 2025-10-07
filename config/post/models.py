from django.db import models
from unidecode import unidecode
from django.template import defaultfilters
from django.core.files.base import ContentFile
from PIL import Image, ImageFilter
import io, os, mimetypes
import cv2
import numpy as np
from django.core.exceptions import ValidationError
import mimetypes
# Create your models here.


class Post(models.Model):
    user_account = models.ForeignKey('useraccount.UserAccount', on_delete=models.CASCADE, verbose_name="User")
    caption = models.TextField(max_length=1500, blank=True, null=True, verbose_name='Caption')
    plan = models.ForeignKey('plan.Plan', on_delete=models.PROTECT, blank=True, null=True, verbose_name="Plan")
    is_open_to_comment = models.BooleanField(default=True, verbose_name='Is Open to Write Comment?')
    likes = models.ManyToManyField("like.PostLike", related_name="liked_posts", verbose_name="Likes")
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name='Creation Date')
    update_date = models.DateTimeField(auto_now=True, verbose_name='Update Date')

    class Meta:
        ordering = ("-creation_date",)

def user_directory_path(instance, filename):
    slug = defaultfilters.slugify(unidecode(str(instance.post.pk)))
    return 'images/post/{0}/{1}'.format(slug, filename)

def blurred_user_directory_path(instance, filename):
    slug = defaultfilters.slugify(unidecode(str(instance.post.pk)))
    return 'images/post_blurred/{0}/{1}'.format(slug, filename)


def validate_file_type(value):
    mime, _ = mimetypes.guess_type(value.name)
    if not mime or (not mime.startswith("image") and not mime.startswith("video")):
        raise ValidationError("Only image and video files are allowed.")
    
    # Check file extension
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.avi', '.mkv', '.webm']
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError(f"Unsupported file extension '{ext}'. Allowed: {', '.join(valid_extensions)}")


class PostFileContent(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='files', verbose_name='Post')
    file = models.FileField(upload_to=user_directory_path, validators=[validate_file_type])
    blurred_file = models.ImageField(upload_to=blurred_user_directory_path, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name='Creation Date')
    update_date = models.DateTimeField(auto_now=True, verbose_name='Update Date')


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.file and not self.blurred_file:
            self.generate_blurred_preview()
            super().save(update_fields=["blurred_file"])

    def generate_blurred_preview(self):
        """Generate a blurred preview (image or first frame of video)."""
        try:
            mime, _ = mimetypes.guess_type(self.file.name)

            if mime and mime.startswith("image"):
                self._generate_blurred_from_image()
            elif mime and mime.startswith("video"):
                self._generate_blurred_from_video()
        except Exception as e:
            print("Error generating blurred preview:", e)

    def _generate_blurred_from_image(self):
        """Blur the uploaded image."""
        img = Image.open(self.file)
        img = img.convert("RGB")
        blurred = img.filter(ImageFilter.GaussianBlur(17))

        buffer = io.BytesIO()
        blurred.save(buffer, format="JPEG", quality=70)
        buffer.seek(0)

        base, _ = os.path.splitext(os.path.basename(self.file.name))
        blurred_name = f"{base}_blurred.jpg"
        self.blurred_file.save(blurred_name, ContentFile(buffer.read()), save=False)

    def _generate_blurred_from_video(self):
        """Extract first frame of video, blur it, and save."""
        cap = cv2.VideoCapture(self.file.path)
        success, frame = cap.read()
        cap.release()

        if not success:
            print("Could not read first frame of video")
            return

        # Convert OpenCV BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img = img.convert("RGB")
        blurred = img.filter(ImageFilter.GaussianBlur(17))

        buffer = io.BytesIO()
        blurred.save(buffer, format="JPEG", quality=70)
        buffer.seek(0)

        base, _ = os.path.splitext(os.path.basename(self.file.name))
        blurred_name = f"{base}_preview_blurred.jpg"
        self.blurred_file.save(blurred_name, ContentFile(buffer.read()), save=False)
