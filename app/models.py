from django.db import models
from django.utils import timezone
from cloudinary_storage.storage import RawMediaCloudinaryStorage
from django.contrib.auth.models import User

class ApplicationLog(models.Model):
    message = models.TextField()
    logger_name = models.CharField(max_length=100)
    interacted_by = models.CharField(max_length=150, null=False, default="")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"[{self.logger_name}] {self.interacted_by}: {self.message[:50]}..."


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class ProjectStatus(models.TextChoices):
    NEW = 'NEW', 'New'
    ACCEPTED = 'ACCEPTED', 'Accepted'
    REJECTED = 'REJECTED', 'Rejected'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    COMPLETED = 'COMPLETED', 'Completed'


class ProjectPriority(models.TextChoices):
    HIGH = 'HIGH', 'High'
    MEDIUM = 'MEDIUM', 'Medium'
    LOW = 'LOW', 'Low'


class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deadline = models.DateField(default=timezone.now)

    sender_name = models.CharField(max_length=150)
    contact_email = models.EmailField()

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(
        max_length=15,
        choices=ProjectStatus.choices,
        default=ProjectStatus.NEW
    )
    priority = models.CharField(
        max_length=10,
        choices=ProjectPriority.choices,
        default=ProjectPriority.MEDIUM
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    accepted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="accepted_projects")
    started_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="started_projects")
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name="completed_projects")

    def __str__(self):
        return f"{self.title} ({self.status}, Priority: {self.priority})"

    def save(self, *args, **kwargs):
        if self.deadline < timezone.now().date():
            raise ValueError("The deadline cannot be in the past.")
        super().save(*args, **kwargs)


class Attachment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/', storage=RawMediaCloudinaryStorage())
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment #{self.id} for {self.project.title}"


class ProjectComment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author_name = models.CharField(max_length=150)

    def __str__(self):
        return f"Comment by {self.author_name} on {self.project.title}"
