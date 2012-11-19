from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from panini.settings import NOVA_CONTROLLER
import httplib, json
import panini.cluster.views
from panini import commons
from panini.cluster.models import Cluster
from panini.cluster.forms import ClusterForm

def index(request):
    return HttpResponseRedirect('/login/')

def login(request):
    if commons.logged_in(request):
        return HttpResponseRedirect('/cluster/')
    if 'username' in request.POST and 'password' in request.POST:
        (username, password) = (request.POST['username'], request.POST['password'])
        header = {'Content-type': 'application/json'}
        body = {'auth': {'passwordCredentials': {'username': username, 'password': password},
                         'tenantName': username}}
        conn = httplib.HTTPConnection(NOVA_CONTROLLER, 35357)
        conn.request('POST', '/v2.0/tokens', json.dumps(body), header)
        response = conn.getresponse()
        # TODO: Error Handling
        data = json.loads(response.read())
        conn.close()
        request.session['access'] = data['access']
        return HttpResponseRedirect('/cluster/')
    else:
        t = loader.get_template('login.html')
        c = {}
        c.update(csrf(request))
        c = Context(c)
        return HttpResponse(t.render(c))

def logout(request):
    if commons.logged_in(request):
        try:
            del request.session['access']
        except KeyError:
            pass
    return HttpResponseRedirect('/')

def cluster(request, curr_cluster):
    if not commons.logged_in(request):
        return HttpResponseRedirect('/')
    if Cluster.objects.filter(name=curr_cluster).count() == 0:
        clusters = Cluster.objects.all()
        for cluster in clusters:
            return HttpResponseRedirect('/cluster/'+cluster.name+'/')
        if curr_cluster != "":
            return HttpResponseRedirect('/cluster/')
    cluster_form = ClusterForm()
    clusters = Cluster.objects.filter()
    t = loader.get_template('cluster.html')
    c = {
        'cluster_form': cluster_form,
        'clusters': clusters,
        'curr_cluster': curr_cluster,
    }
    c.update(csrf(request))
    c = Context(c)
    return HttpResponse(t.render(c))
