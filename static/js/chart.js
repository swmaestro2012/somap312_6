google.load("visualization", "1", {packages:["corechart"]});
google.setOnLoadCallback(drawChart);
function drawCPUChart() {
    if (cpu_data.length == 1) return;
    var data = google.visualization.arrayToDataTable(pivot(cpu_data));
    var options = { title: 'CPU' };
    var chart = new google.visualization.ColumnChart(document.getElementById('cpu_chart'));
    chart.draw(data, options);
}
function drawRAMChart() {
    if (ram_data.length == 1) return;
    var data = google.visualization.arrayToDataTable(pivot(ram_data));
    var options = { title: 'RAM' };
    var chart = new google.visualization.ColumnChart(document.getElementById('ram_chart'));
    chart.draw(data, options);
}
function drawDiskChart() {
    if (disk_data.length == 1) return;
    var data = google.visualization.arrayToDataTable(disk_data);
    var options = { title: 'Disk' };
    var chart = new google.visualization.PieChart(document.getElementById('disk_chart'));
    chart.draw(data, options);
}
function drawChart() {
    drawCPUChart();
    drawRAMChart();
    drawDiskChart();
}
function pivot(array) {
    var n = array.length;
    var m = array[0].length;
    var new_array = new Array(m);
    for (var i = 0; i < m; i++) {
        new_array[i] = new Array(n);
        for (var j = 0; j < n; j++)
            new_array[i][j] = array[j][i];
    }
    return new_array;
}
