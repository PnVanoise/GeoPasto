from django.contrib.gis.db import models


class AuditFieldsMixin(models.Model):
    created_by = models.CharField(max_length=150, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    modified_by = models.CharField(max_length=150, null=True, blank=True)
    modified_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
