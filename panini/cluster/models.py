from django.db import models

class Cluster(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __unicode__(self):
        return self.name

class Server(models.Model):
    name = models.CharField(max_length=30)
    cluster = models.ForeignKey(Cluster)

    def __unicode__(self):
        return self.name+' in '+unicode(self.cluster)

    class Meta:
        unique_together = ('name', 'cluster')
