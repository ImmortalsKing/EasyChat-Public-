from django.db import models

from account_module.models import User, Group


class Message(models.Model):
    from_who = models.ForeignKey(User,on_delete=models.PROTECT,default=None,related_name='from_user')
    to_who = models.ForeignKey(User,on_delete=models.PROTECT,default=None,related_name='to_user',null=True,blank=True)
    group = models.ForeignKey(Group,on_delete=models.CASCADE,verbose_name='Group',related_name='messages',null=True,blank=True)
    message = models.TextField(null=True,blank=True)
    image = models.ImageField(upload_to='images/uploads',null=True,blank=True)
    file = models.FileField(upload_to='files/uploads',null=True,blank=True)
    date = models.DateField(null=True)
    time = models.TimeField(null=True)
    has_been_seen = models.BooleanField(null=True,default=False)


class UserChannel(models.Model):
    user = models.ForeignKey(User,on_delete=models.PROTECT,default=None)
    channel_name = models.TextField()


class GalleryRoom(models.Model):
    title = models.CharField(max_length=100,verbose_name='Title')
    featured_image = models.ImageField(upload_to='images/gallery_main',verbose_name='Featured Image')
    by_who = models.ForeignKey(User,on_delete=models.PROTECT,verbose_name='By Who')
    slug = models.SlugField(max_length=200, db_index=True, unique=True, verbose_name='Slug')
    is_active = models.BooleanField(default=False,verbose_name='Active / Inactive')

    class Meta:
        verbose_name = 'Gallery Room'
        verbose_name_plural = 'Gallery Rooms'

    def __str__(self):
        return f'{self.title} / {self.by_who}'

class Gallery(models.Model):
    image = models.ImageField(upload_to='images/gallery',verbose_name='Image')
    caption = models.CharField(max_length=200,verbose_name='Caption')
    room = models.ForeignKey(GalleryRoom,on_delete=models.CASCADE,verbose_name='Gallery Room')
    date = models.DateTimeField(auto_now_add=True,verbose_name='Date')

    class Meta:
        verbose_name = 'Gallery'
        verbose_name_plural = 'Galleries'

    def __str__(self):
        return self.caption