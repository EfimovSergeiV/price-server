from django.db import models
from django.utils import timezone


class ProductModel(models.Model):
    """ Модель продукта """

    list_brands = (
        ( 'fubag', 'Fubag' ),
        ( 'svarog', 'Svarog' ),
        ( 'telwin', 'Telwin' ),
    )

    vcode = models.CharField(verbose_name="Артикул", max_length=150, null=True, blank=True)
    name = models.CharField(verbose_name="Наименование", max_length=600, null=True, blank=True)
    old_name = models.CharField(verbose_name="Старое наименование", max_length=600, null=True, blank=True)
    brand = models.CharField(verbose_name="Производитель", max_length=300, null=True, choices=list_brands, blank=True)
    price = models.IntegerField(verbose_name="Стоимость", null=True, blank=True)
    latest_updated = models.DateTimeField(verbose_name="Последнее обновление", default=timezone.now)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name