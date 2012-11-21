from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from django.core.exceptions import ValidationError
from panini import commons
from panini.settings import NOVA_CONTROLLER, CHEF_SERVER, CHEF_PORT, ROOT_PASSWORD
from panini.cluster.models import Cluster, Server
from panini.cluster.forms import ClusterForm
import httplib, json
import base64
import re
import chef
import paramiko
import os

def add_cluster(request):
    if not commons.logged_in(request):
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        if len(Cluster.objects.filter(name=request.POST['name'])) == 0:
            cluster = Cluster.objects.create(name=request.POST['name'], master=None)
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

        server = Server(name=name, server_id='', ip='', cluster_in=Cluster.objects.get(name=curr_cluster))
        try:
            server.full_clean()
            data = launch(request)
            server.server_id = data['server']['id']
            server.save()
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

    server = Server.objects.get(name=server_name, cluster_in=Cluster.objects.get(name=curr_cluster))
    try:
        delete_databag(server)
    except Exception:
        pass
    try:
        delete_chef_client(server_name)
    except Exception:
        pass
    server.delete()

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

    return nova_api(request, 'POST', '/v2/%(tenant_id)s/servers', header, body)

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

    has_master = True if Cluster.objects.get(name=curr_cluster).master != None else False

    t = loader.get_template('servers.html')
    c = {
            'curr_cluster': curr_cluster,
            'has_master': has_master,
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

def get_server(request, server_id):
    if not commons.logged_in(request):
        return {}

    header = {'X-Auth-Token': request.session['access']['token']['id']}
    body = {}

    data = nova_api(request, 'GET', '/v2/%(tenant_id)s/servers/'+server_id, header, body)

    return data['server']

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

def get_chef_api():
    api = chef.autoconfigure()
    # chef.ChefAPI
    return api

def trigger_chef_client(hostname, port=22):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=hostname, port=port, username="root", password=ROOT_PASSWORD)
    ssh.exec_command("killall -USR1 chef-client")

def delete_chef_client(server_name):
    api = get_chef_api()
    api.api_request('DELETE', '/clients/'+server_name+'.novalocal')
    node = chef.Node(server_name+".novalocal", api)
    node.delete(api)

def is_installed(server_name, role):
    api = get_chef_api()
    node = chef.Node(server_name+".novalocal", api)
    return "role["+role+"]" in node.run_list

def install(request, curr_cluster, server_name, role):
    if not commons.logged_in(request):
        return HttpResponseRedirect('/cluster/'+curr_cluster+'/')
    server = Server.objects.get(name=server_name)
    if server.ip == '':
        server_data = get_server(request, server.server_id)
        for ip in server_data['addresses']['private']:
            if ip['version'] == 4:
                server.ip = ip['addr']
                server.save()
                os.system('echo '+server.ip+' '+server.name+'.novalocal >> /etc/hosts')
                break
    api = get_chef_api()
    node = chef.Node(server_name+".novalocal", api)
    if "role["+role+"]" not in node.run_list:
        if role == 'vm-master':
            if server.cluster_in.master != None: 
                return HttpResponseRedirect('/cluster/'+curr_cluster+'/')
            server.cluster_in.master = server
            server.cluster_in.save()
            update_databag(server, '1')
            if 'role[vm-slave]' in node.run_list:
                node.run_list.remove("role[vm-slave]")
            node.run_list.append("role[vm-master]")
            server.is_master = True
            server.is_slave = False
            node.save()
            server.save()
            trigger_chef_client(server_name)
        elif role == 'vm-slave':
            update_databag(server, '0')
            if 'role[vm-master]' in node.run_list:
                node.run_list.remove("role[vm-master]")
            node.run_list.append("role[vm-slave]")
            server.is_master = False
            server.is_slave = True
            node.save()
            server.save()
            trigger_chef_client(server_name)
            trigger_chef_client(server.cluster_in.master.name)
    return HttpResponseRedirect('/cluster/'+curr_cluster+'/')

def get_databag():
    api = get_chef_api()
    databag = chef.DataBag('multi_node', api)
    return databag['hd-cluster-setting']
    '''
    f = open('multi_node.json', 'r')
    raw = f.read()
    f.close()
    return json.loads(raw)
    '''

def set_databag(item):
    item.save()
    '''
    f = open('multi_node.json', 'w')
    f.write(json.dumps(item))
    f.close()
    os.system('knife data bag from file multi_node multi_node.json')
    '''

def update_databag(server, is_master):
    item = get_databag()
    for hadoop_node in item['hadoop_nodes']:
        if hadoop_node['name'] == server.name:
            hadoop_node['is_master'] = is_master
            set_databag(item)
            return
    item['hadoop_nodes'].append({'name': server.name, 'ip': server.ip, 'is_master': is_master})
    set_databag(item)

def delete_databag(server):
    item = get_databag()
    for hadoop_node in item['hadoop_nodes']:
        if hadoop_node['name'] == server.name:
            item['hadoop_nodes'].remove(hadoop_node)
            set_databag(item)
            return
