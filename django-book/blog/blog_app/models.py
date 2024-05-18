from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from taggit.managers import TaggableManager

# Nos permite hacer querys especificas, con este modelo solo seleccionamos las del campo publish
class PublishManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset() \
            .filter(status=Post.Status.PUBLISHED)


class Post(models.Model):
    # It’s a good practice to define choices inside the model class and use the enumeration types. 
    class Status(models.TextChoices):
        DRAFT = "DF", 'Draft'
        PUBLISHED = 'PB', 'Published'
    
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250,
                            unique_for_date='publish')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='blog_posts') # user.blog_posts

    
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2, 
                              choices=Status.choices, 
                              default=Status.DRAFT)
    tags = TaggableManager()
    
    # model manager
    objects = models.Manager()
    published = PublishManager()
    
    
    class Meta: # La clase meta controla aspectos del comportamiento del modelo
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish']),
        ]
        
        
        
    def __str__(self):
        return self.title
    
    # Los "Canonical URLs" (URLs canónicas) son URLs que se utilizan para identificar la versión preferida o principal de una página web cuando hay múltiples URLs que apuntan al mismo contenido o recurso.
    # Ejemplos: 
    # Por ejemplo, supongamos que tienes una página de producto en tu sitio web que se puede acceder a través de las siguientes URLs:
    # https://example.com/products/product-1
    # https://www.example.com/products/product-1
    # https://example.com/products/product-1/
    # https://www.example.com/products/product-1/?ref=123
    def get_absolute_url(self):
        return reverse("blog_app:post_detail", # blog_app namespace defined in the main urls.py                
                       args=[self.publish.year,
                             self.publish.month,
                             self.publish.day,
                             self.slug])
        
        
class Comment(models.Model):
    post = models.ForeignKey(Post, 
                             on_delete=models.CASCADE,
                             related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    
    
    class Meta: 
        ordering = ['created']
        indexes = [
            models.Index(fields=['created'])
        ]
        
    def __str__(self):
        return f'Comment by {self.name} on {self.post}'
    