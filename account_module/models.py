import secrets

from django.contrib.auth.models import AbstractUser
from django.db import models

from utils.get_default_avatar import get_default_avatar


class Country(models.Model):
    name = models.CharField(max_length=100,db_index=True,verbose_name='Country Name')
    logo = models.ImageField(upload_to='images/countries',verbose_name='Country Logo')

    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'

    def __str__(self):
        return self.name

class User(AbstractUser):
    display_name = models.CharField(max_length=200,db_index=True,verbose_name='Display Name',default='new_user')
    avatar = models.ImageField(upload_to='images/avatars',verbose_name='Avatar',null=True,blank=True)
    about_user = models.TextField(null=True,blank=True,verbose_name='About User')
    country = models.ForeignKey(Country,on_delete=models.PROTECT,null=True,blank=True,verbose_name='Country')
    is_blocked = models.BooleanField(verbose_name='Is Blocked / Is not Blocked',default=False)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.display_name


class InvitationCode(models.Model):
    code = models.CharField(max_length=30,unique=True,db_index=True,verbose_name='Generated Code')
    invited_user = models.OneToOneField(User,null=True,blank=True,on_delete=models.SET_NULL)

    @classmethod
    def generate_code(cls):
        return secrets.token_hex(5)


class Group(models.Model):
    title = models.CharField(max_length=100 , db_index=True , verbose_name='Title')
    avatar = models.ImageField(upload_to='images/group_avatar',null=True,blank=True)
    about = models.TextField(null=True,blank=True,verbose_name='About Group')
    members = models.ManyToManyField(User, verbose_name='members')
    slug = models.SlugField(max_length=255,unique=True,verbose_name='Slug',db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(verbose_name='Active / Inactive',default=True)

    class Meta:
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'

    def __str__(self):
        return self.title
