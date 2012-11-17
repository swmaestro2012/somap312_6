from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from panini.settings import NOVA_CONTROLLER
import httplib, json

def logged_in(request):
    return 'access' in request.session
def logged_out(request):
    return 'access' not in request.session

def index(request):
    return HttpResponseRedirect('/login/')

def login(request):
    if logged_in(request):
        return HttpResponseRedirect('/main/')
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
        return HttpResponseRedirect('/main/')
    else:
        t = loader.get_template('login.html')
        c = {}
        c.update(csrf(request))
        c = Context(c)
        return HttpResponse(t.render(c))

def logout(request):
    if logged_in(request):
        try:
            del request.session['access']
        except KeyError:
            pass
    return HttpResponseRedirect('/')

def main(request):
    if logged_out(request):
        return HttpResponseRedirect('/')
    t = loader.get_template('main.html')
    c = Context({
        'debug': request.session['access'],
    })
    return HttpResponse(t.render(c))
