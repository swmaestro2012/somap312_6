from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from django.core.exceptions import ValidationError
from panini import commons
from panini.settings import NOVA_CONTROLLER
from panini.cluster.models import Cluster, Server
from panini.cluster.forms import ClusterForm
import httplib, json
import base64
import re

def add_cluster(request):
    if not commons.logged_in(request):
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        cluster_form = ClusterForm(request.POST)
        if cluster_form.is_valid():
            cluster_form.save()
    return HttpResponseRedirect('/')

def delete_cluster(request, cluster):
    if not commons.logged_in(request):
        return HttpResponseRedirect('/')
    curr_cluster = Cluster.objects.get(name=cluster)
    server_set = []
    for server in Server.objects.filter(cluster=curr_cluster):
        server_set.append(server.name)
    servers = get_servers(request)
    for server in servers:
        if server['name'] in server_set:
            delete_server(request, curr_cluster, server['name'], server['id'])
    curr_cluster.delete()
    return HttpResponseRedirect('/')

def add_server(request, curr_cluster):
    if not commons.logged_in(request):
        return HttpResponseRedirect('/')

    if 'name' in request.POST and 'flavor' in request.POST and 'image' in request.POST:
        name = request.POST['name']

        server = Server(name=name, cluster=Cluster.objects.get(name=curr_cluster))
        try:
            server.full_clean()
            server.save()
            launch(request)
        except ValidationError:
            pass

    if request.method == 'POST':
        return HttpResponseRedirect('/cluster/'+curr_cluster+'/')
    flavors = get_flavors(request)
    images = get_images(request)

    t = loader.get_template('launch.html')
    c = { 
        'curr_cluster': curr_cluster,
        'flavors': flavors,
        'images': images,
    }   
    c.update(csrf(request))
    c = Context(c)
    return HttpResponse(t.render(c))

def delete_server(request, curr_cluster, server_name, server_id):
    if not commons.logged_in(request):
        return HttpResponseRedirect('/')

    Server.objects.filter(name=server_name, cluster=Cluster.objects.get(name=curr_cluster)).delete()

    if server_id != None: 
        header = {'X-Auth-Token': request.session['access']['token']['id']}
        body = {}

        nova_api(request, 'DELETE', '/v2/%(tenant_id)s/servers/'+server_id, header, body)

    return HttpResponseRedirect('/cluster/')

def launch(request):
    if not commons.logged_in(request):
        return HttpResponseRedirect('/')

    f = open('user_data.txt', 'r')
    user_data = f.read()
    f.close()

    header = {'Content-type': 'application/json',
              'X-Auth-Token': request.session['access']['token']['id']}
    body = {'server': {'name': request.POST['name'],
                       'flavorRef': request.POST['flavor'],
                       'imageRef': request.POST['image'],
                       'user_data': base64.b64encode(user_data)
                      }}

    nova_api(request, 'POST', '/v2/%(tenant_id)s/servers', header, body)

def servers(request, curr_cluster):
    if not commons.logged_in(request):
        return HttpResponseRedirect('/')

    servers = get_servers(request)
    flavors = get_flavors(request)
    images = get_images(request)

    servers_dict = {}
    for server in servers:
        servers_dict[server['name']] = server
    flavors_dict = {}
    for flavor in flavors:
        flavors_dict[flavor['id']] = flavor
    images_dict = {}
    for image in images:
        images_dict[image['id']] = image

    servers = []
    for server in Cluster.objects.get(name=curr_cluster).server_set.all():
        if server.name in servers_dict:
            s = servers_dict[server.name]
            s['flavor'] = flavors_dict[s['flavor']['id']]
            s['image'] = images_dict[s['image']['id']]
            s['is_master'] = server.is_master
            s['is_slave'] = server.is_slave
            if not server.is_ready:
                console_log = get_console_log(request, s['id'])
                if re.search(r'^cloud\-init boot finished', console_log, re.M) != None:
                    server.is_ready = True
                    server.save()
            s['is_ready'] = server.is_ready
        else:
            s = {'name': server.name, 'flavor': {'vcpus': '0', 'ram': '0', 'disk': '0'}, 'status': 'NOT EXIST', 'is_master': False, 'is_slave': False}
        servers.append(s)

    t = loader.get_template('servers.html')
    c = {
            'curr_cluster': curr_cluster,
            'servers': servers,
            'flavors': flavors,
            'images': images,
        }
    c.update(csrf(request))
    c = Context(c)
    return HttpResponse(t.render(c))

def nova_api(request, method, uri, header, body, debug=False):
    if not commons.logged_in(request):
        return {}

    conn = httplib.HTTPConnection(NOVA_CONTROLLER, 8774)
    conn.request(method,
                 uri % {'tenant_id': request.session['access']['token']['tenant']['id']},
                 json.dumps(body), header)
    response = conn.getresponse()
    if debug:
        res = response.read()
        print res
        return res
    # TODO: Error Handling
    data = {}
    try:
        data = json.loads(response.read())
    except Exception:
        data = {}
    conn.close()
    return data

def get_servers(request):
    if not commons.logged_in(request):
        return {}

    header = {'X-Auth-Token': request.session['access']['token']['id']}
    body = {}

    data = nova_api(request, 'GET', '/v2/%(tenant_id)s/servers/detail', header, body)

    return data['servers']

def get_flavors(request):
    if not commons.logged_in(request):
        return {}

    header = {'X-Auth-Token': request.session['access']['token']['id']}
    body = {}

    data = nova_api(request, 'GET', '/v2/%(tenant_id)s/flavors/detail', header, body)

    return data['flavors']

def get_images(request):
    if not commons.logged_in(request):
        return {}

    header = {'X-Auth-Token': request.session['access']['token']['id']}
    body = {}

    data = nova_api(request, 'GET', '/v2/%(tenant_id)s/images/detail', header, body)

    return data['images']

def get_console_log(request, server_id):
    if not commons.logged_in(request):
        return {}

    header = {'Content-type': 'application/json',
              'X-Auth-Token': request.session['access']['token']['id']}
    body = {'os-getConsoleOutput': {}}

    data = nova_api(request, 'POST', '/v2/%(tenant_id)s/servers/'+server_id+'/action', header, body)

    if 'output' not in data:
        return ''
    return data['output']

def chef_client_trigger(hostname, port=22):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=hostname, port=port, username="ubuntu")
    ssh.exec_command("echo %s | sudo killall -USR1 chef-client" % ROOT_PASSWORD)

def install(request, server_id):
    if "access" not in request.session:
        return {}

    server = get_server(request, server_id)
    node_name = server["name"]+".novalocal"

    api = chef.autoconfigure()
    node = chef.Node(node_name, api)
    roles = request.GET.getlist("role")
    for role in roles:
        node.run_list.append("role["+role+"]")
    node.save()

    chef_client_trigger(server["name"])

    return HttpResponseRedirect("/servers/show/"+server_id+"/")

def uninstall(request, server_id):
    if "access" not in request.session:
        return {}
    
    server = get_server(request, server_id)
    node_name = server["name"]+".novalocal"

    api = chef.autoconfigure()
    node = chef.Node(node_name, api)
    roles = request.GET.getlist("role")
    for role in roles:
        node.run_list.remove("role["+role+"]")
    node.save()

    chef_client_trigger(server["name"])

    return HttpResponseRedirect("/servers/show/"+server_id+"/")

def installed_packages(request, server_id):
    if "access" not in request.session:
        return {}

    server = get_server(request, server_id)

    api = chef.api.autoconfigure()
    node = api.api_request("GET", "/nodes/"+server["name"]+".novalocal")

    installed_roles = []
    for role in node["run_list"]:
        m = re.match(r"^role\[(.*)\]$", role)
        if m is not None:
            installed_roles.append(m.group(1))

    roles = api.api_request("GET", "/roles")
    uninstalled_roles = [role for role in roles.keys() if role not in installed_roles]

    return (installed_roles, uninstalled_roles)
