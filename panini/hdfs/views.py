from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from panini.cluster.models import Cluster, Server
import httplib, json
import string

def show(request, curr_cluster, path):
    path = path[:-1]

    status = get_status(request, curr_cluster, path if len(path) > 1 else '/')
    if 'type' in status:
        if status['type'] == 'DIRECTORY':
            path = path.split('/')

            (path_link, path_accum) = get_path_link(curr_cluster, path)
            files = get_list(request, curr_cluster, path_accum)

            t = loader.get_template('list.html')
            c = {
                'path': path_link,
                'path_accum': path_accum,
                'files': files,
                'curr_cluster': curr_cluster,
            }
            c.update(csrf(request))
            return HttpResponse(t.render(Context(c)))
        elif status['type'] == 'FILE':
            data = get_file(request, curr_cluster, path)

            path = path.split('/')

            (path_link, path_accum) = get_path_link(curr_cluster, path)

            t = loader.get_template('show.html')
            c = Context({
                'path': path_link,
                'path_accum': path_accum,
                'file': data,
                'curr_cluster': curr_cluster,
            })
            return HttpResponse(t.render(c))

def mkdir(request, curr_cluster, path):
    path_accum = path + request.POST['dir']
    data = webhdfs_api(request, curr_cluster, 'PUT', '/webhdfs/v1'+path_accum+'?op=MKDIRS&user.name=root', {}, {})
    return HttpResponseRedirect('/cluster/'+curr_cluster+'/')
    return HttpResponseRedirect('/hdfs/'+curr_cluster+'/show'+path)

def put(request, curr_cluster, path):
    master = Cluster.objects.get(name=curr_cluster).master
    f = request.FILES['file']
    path_accum = path + f.name
    method = 'PUT'
    uri = '/webhdfs/v1'+path_accum+'?op=CREATE&overwrite=true&user.name=root'
    header = {}
    body = {}
    conn = httplib.HTTPConnection(master.ip, 50070)
    conn.request(method, uri, json.dumps(body), header)
    response = conn.getresponse()
    location = response.getheader('location')
    conn.close()
    start = len('http://')
    mid = string.find(location, ':', start)
    end = string.find(location, '/', mid)
    data_node = location[start:mid]
    port = location[mid+1:end]
    uri = location[end:]
    body = f.read()
    f.close()
    slave = Server.objects.get(name=data_node)
    conn = httplib.HTTPConnection(slave.ip, int(port))
    conn.request(method, uri, body, header)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return HttpResponseRedirect('/cluster/'+curr_cluster+'/')
    return HttpResponseRedirect('/hdfs/'+curr_cluster+'/show'+path)

def delete(request, curr_cluster, path):
    path_accum = path
    data = webhdfs_api(request, curr_cluster, 'DELETE', '/webhdfs/v1'+path_accum+'?op=DELETE&recursive=true&user.name=root', {}, {})
    path = path[:string.rfind(path[:-1], '/')]
    return show(request, curr_cluster, path)
    return HttpResponseRedirect('/cluster/'+curr_cluster+'/')
    return HttpResponseRedirect('/hdfs/'+curr_cluster+'/show'+path)

def get_path_link(curr_cluster, path):
    path_link = []
    path_accum = ''
    for node in path:
        name = node+'/'
        path_accum += name
        path_link.append({'name': node if node != '' else 'HDFS', 'uri': path_accum})
    return (path_link, path_accum)

def webhdfs_api(request, curr_cluster, method, uri, header, body):
    master = Cluster.objects.get(name=curr_cluster).master
    conn = httplib.HTTPConnection(master.ip, 50070)
    conn.request(method, uri, json.dumps(body), header)
    response = conn.getresponse()
    data = {}
    try:
        data = json.loads(response.read())
    except Exception:
        data = {}
    conn.close()
    return data

def get_list(request, curr_cluster, path_accum):
    data = webhdfs_api(request, curr_cluster, 'GET', '/webhdfs/v1'+path_accum+'?op=LISTSTATUS', {}, {})
    if 'FileStatuses' in data:
        return data['FileStatuses']['FileStatus']
    return {}

def get_status(request, curr_cluster, path_accum):
    data = webhdfs_api(request, curr_cluster, 'GET', '/webhdfs/v1'+path_accum+'?op=GETFILESTATUS', {}, {})
    if 'FileStatus' in data:
        return data['FileStatus']
    return {}

def get_file(request, curr_cluster, path_accum):
    master = Cluster.objects.get(name=curr_cluster).master
    method = 'GET'
    uri = '/webhdfs/v1'+path_accum+'?op=OPEN'
    header = {}
    body = {}
    conn = httplib.HTTPConnection(master.ip, 50070)
    conn.request(method, uri, json.dumps(body), header)
    response = conn.getresponse()
    location = response.getheader('location')
    conn.close()
    start = len('http://')
    mid = string.find(location, ':', start)
    end = string.find(location, '/', mid)
    data_node = location[start:mid]
    port = location[mid+1:end]
    uri = location[end:]
    slave = Server.objects.get(name=data_node)
    conn = httplib.HTTPConnection(slave.ip, int(port))
    conn.request(method, uri, json.dumps(body), header)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data
