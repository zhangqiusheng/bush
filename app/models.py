# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Plateform(models.Model):
    userId = models.ForeignKey(User)
    createdAt = models.DateTimeField("创建的时间", auto_now_add=True)
    name = models.CharField('平台名称', max_length=255, unique=True)
    description = models.TextField('平台描述', blank=True, null=True)

class Project(models.Model):
    user = models.ForeignKey(User)
    plateform = models.ForeignKey(Plateform)
    createdAt = models.DateTimeField("创建的时间", auto_now_add=True)
    name = models.CharField('项目名称', max_length=255, unique=True)
    description = models.TextField('项目描述', blank=True, null=True)
    owner = models.IntegerField(blank=True, null=True)

class ProjectGroup(models.Model):
    user = models.ForeignKey(User)
    project = models.ForeignKey(Project)
    createdAt = models.DateTimeField("创建的时间",auto_now_add=True)
    name = models.CharField('项目组名称', max_length=255, unique=True)
    description = models.TextField('项目组描述', blank=True, null=True)

class Case(models.Model):
    #user = models.ForeignKey(User)
    #progect_group = models.ForeignKey(ProjectGroup)
    name = models.CharField('用例名称', max_length=255, unique=True)
    description = models.TextField('用例描述', blank=True, null=True)
    script = models.TextField('脚本', blank=True, null=True)
    command = models.TextField('命令', max_length=255, null=True)
    param = models.TextField('参数', max_length=255, null=True)
    createdAt = models.DateTimeField("创建的时间", auto_now_add=True)

