from django.forms import ModelForm
from panini.cluster.models import Cluster

class ClusterForm(ModelForm):
    class Meta:
        model = Cluster
