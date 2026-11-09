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
        verbose_name = 'Каталог'
        verbose_name_plural = 'Каталоги'

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
    age = models.IntegerField(null=True, blank=True)
    nick = models.CharField(max_length=255, db_index=True, unique=True)
    vk_id = models.IntegerField(null=True, blank=True)
    ava = models.TextField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)
    time_last_active = models.DateTimeField(null=True)

    step1 = models.BooleanField(default=False, db_index=True)
    step2_parsed = models.BooleanField(default=False, db_index=True)
    step2_good = models.BooleanField(default=False, db_index=True)
    step2_continue = models.IntegerField(null=True, blank=True, db_index=True)
    step3_parsed = models.BooleanField(default=False, db_index=True)
    step3_good = models.BooleanField(default=False, db_index=True)

    class Meta:
        verbose_name = 'Элемент'
        verbose_name_plural = 'Элементы'
        constraints = [
            # models.UniqueConstraint(
            #     name="%(app_label)s_%(class)s_name_unique",
            #     fields=["name"],
            # ),
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_nick_not_empty",
                check=models.Q(nick__length__gt=0),
            ),
        ]
