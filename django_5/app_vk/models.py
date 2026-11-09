from django.db import models
from django.db.models.functions import Length
from django.urls import reverse

from lib.tree_manager import TreeManager

models.CharField.register_lookup(Length)


class Sections(models.Model):
    id = models.AutoField(primary_key=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    code = models.CharField(max_length=255, db_index=True, unique=True)
    sort = models.IntegerField(default=0)
    name = models.CharField(max_length=255)
    desc = models.TextField(null=True, blank=True)

    objects = models.Manager()
    tree = TreeManager()

    class Meta:
        verbose_name = 'Каталог (vk)'
        verbose_name_plural = 'Каталоги (vk)'

    # noinspection DuplicatedCode
    def get_absolute_url(self):
        path = Sections.tree.get()['paths'].get(self.pk)
        if path is None:
            return reverse('section', kwargs={'section_code': self.code})
        else:
            path_list = []
            for el_id in path:
                path_list.append(Sections.tree.get_el(el_id)['el'].code)
            return reverse('section', kwargs={
                'section_code': self.code,
                'section_path': '/'.join(path_list),
            })


class Elements(models.Model):
    id = models.AutoField(primary_key=True)
    sections = models.ManyToManyField(Sections, blank=True)
    name = models.CharField(max_length=255)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Элемент (vk)'
        verbose_name_plural = 'Элементы (vk)'


class VKItem(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=255, db_index=True, unique=True)
    profile_id = models.IntegerField(null=True, blank=True)
    is_private_profile = models.BooleanField(null=True, blank=True)
    is_parsed = models.BooleanField(null=True, blank=True)
    detailed_information_html = models.TextField(null=True, blank=True)
    profile_more_html = models.TextField(null=True, blank=True)
    photo_page_html = models.TextField(null=True, blank=True)
    friends_moscow_all_links = models.TextField(null=True, blank=True)
    friends_moscow_girl_links = models.TextField(null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Элемент (parser)'
        verbose_name_plural = 'Элементы (parser)'
        constraints = [
            # models.UniqueConstraint(
            #     name="%(app_label)s_%(class)s_name_unique",
            #     fields=["name"],
            # ),
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_url_not_empty",
                check=models.Q(url__length__gt=0),
            ),
        ]

class VKProfile(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=255, db_index=True, unique=True)
    gender = models.CharField(max_length=1, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Элемент (parser profiles)'
        verbose_name_plural = 'Элементы (parser profiles)'
        constraints = [
            # models.UniqueConstraint(
            #     name="%(app_label)s_%(class)s_name_unique",
            #     fields=["name"],
            # ),
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_url_not_empty",
                check=models.Q(url__length__gt=0),
            ),
        ]

