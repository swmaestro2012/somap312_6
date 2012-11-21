from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from panini.settings import ROOT_PASSWORD
from panini.cluster.models import Cluster, Server
import os
import subprocess
import paramiko

def launch(request, curr_cluster):
    if request.method == 'POST':
        job = request.POST['class']
        fin = request.POST['input']
        fout = request.POST['output']
        jar = request.FILES['jar']
        jar_name = '/tmp/'+jar.name
        f = open(jar_name, 'w')
        f.write(jar.read())
        f.close()
        jar.close()
        master = Cluster.objects.get(name=curr_cluster).master
        subprocess.Popen(['scp',jar_name,'root@'+master.ip+':'+jar_name]).wait()

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(master.ip, username='root', password=ROOT_PASSWORD)
        ssh.exec_command('. /opt/hadoop/conf/hadoop-env.sh')
        ssh.exec_command('/opt/hadoop/bin/hadoop jar '+jar_name+' '+job+' '+fin+' '+fout)
        ssh.close()
        return HttpResponseRedirect('/cluster/'+curr_cluster+'/')

    t = loader.get_template('mapreduce.html')
    c = {
    }
    c.update(csrf(request))
    return HttpResponse(t.render(Context(c)))
