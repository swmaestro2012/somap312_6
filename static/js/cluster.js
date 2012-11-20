function show_add_cluster() {
    document.getElementById("add_cluster").style.display = "block";
}
function add_cluster() {
    var form = document.getElementById("add_cluster").children[0];
    var csrf_token = form.getElementsByTagName("input")[0].getAttribute("value");
    var new_cluster = form.elements["name"].value;
    var body = "name="+new_cluster;
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("POST", "/add-cluster/", false);
    xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xmlhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xmlhttp.send(body);
    document.location.reload(true);
}
function delete_cluster(cluster) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("GET", "/delete-cluster/"+cluster+"/", false);
    xmlhttp.send();
    document.location.reload(true);
}
function update_server() {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("GET", "/cluster/"+curr_cluster+"/servers/", false);
    xmlhttp.send();
    document.getElementById("servers").innerHTML = xmlhttp.responseText;
    eval(document.getElementById("servers").getElementsByTagName("script")[0].innerText);
}
function update_add_server() {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("GET", "/cluster/"+curr_cluster+"/add-server/", false);
    xmlhttp.send();
    document.getElementById("add-server").innerHTML = xmlhttp.responseText;
}
function show_add_server() {
    document.getElementById("add-server").style.display = "block";
}
function hide_add_server() {
    document.getElementById("add-server").style.display = "none";
}
function add_server() {
    var form = document.getElementById("add-server").children[0];
    var csrf_token = form.getElementsByTagName("input")[0].getAttribute("value");
    var name = form.elements["name"].value;
    form.elements["name"].value = "";
    var image = form.elements["image"].value;
    var flavor = form.elements["flavor"].value;
    var body = "name="+name+"&image="+image+"&flavor="+flavor;
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("POST", "/cluster/"+curr_cluster+"/add-server/", false);
    xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xmlhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xmlhttp.send(body);
    update_server();
}
function delete_server(server_name, server_id) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("GET", "/cluster/"+curr_cluster+"/delete-server/"+server_name+"/"+server_id+"/", false);
    xmlhttp.send();
    update_server();
}
function install_role(server_name, role) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("GET", "/cluster/"+curr_cluster+"/server/"+server_name+"/install/"+role+"/", false);
    xmlhttp.send();
    update_server();
}
function uninstall_role(server_name, role) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("GET", "/cluster/"+curr_cluster+"/server/"+server_name+"/uninstall/"+role+"/", false);
    xmlhttp.send();
    update_server();
}
function init() {
    update_server();
    update_add_server();
}
