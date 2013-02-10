
function drawCharts(collected) {
  drawColumnChart(collected);
  //drawPieChart();
  //drawGaugeChart();
}

function drawColumnChart(collected) {

  var options = {
    title: 'Alumni Data Collection by batch',
    titlePosition: 'out',
    titleTextStyle: {color: 'black'},
    hAxis: {title: 'Year of graduation', titleTextStyle: {color: 'red'}},
    animation: {duration: 2000, easing: 'out'},
    isStacked: true,
    bar: {groupWidth: '90%'},
    chartArea: {width: '70%', height: '70%'},
    backgroundColor: '#ffeeff',
    vAxis: {title: 'Number of profiles collected so far', minValue:0, maxValue:100}
  };

  var chart = new google.visualization.ColumnChart(document.getElementById('column_chart'));

  var data = new google.visualization.DataTable();
  data.addColumn('string', 'year');
  data.addColumn('number', 'Collected'); 

  console.log("In");
  console.log(collected);

  for(var year in collected)
  {
    value = Math.round(parseInt(collected[year])*0.1);
    data.addRow([year, value]);
  }
  chart.draw(data, options);

  var row, newvalue;
  for(i=1; i<=10; i++)
  {
    row = 0, newvalue=0;
    for(var year in collected)
    {
      newvalue = Math.round(parseInt(collected[year])*0.1*i); 
      data.setValue(row, 1, newvalue);
      row++;
    }
    chart.draw(data, options);
  }
}

/*function drawPieChart() {

  var options = {
    title: 'Alumni Data Collection Progress',
    animation: {duration: 2000, easing: 'out'},
    chartArea: {width: '60%', height: '70%'},
    backgroundColor: '#ffeeff',
    is3D: true
  };

  var chart = new google.visualization.PieChart(document.getElementById('pie_chart'));
  
  var data = new google.visualization.DataTable();
  data.addColumn('string', 'Category');
  data.addColumn('number', 'Number');
  data.addRow(['Collected', {{ totalalumdata }}]);
  data.addRow(['Remaining', {{ remainingalumdata }}]);

  chart.draw(data, options);
}*/

/*function drawGaugeChart() {

  var options = {
    width: 250, height: 250,
    minorTicks: 5,
    animation: {duration: 2000, easing: 'linear'},
    max: 30000
  };

  var chart = new google.visualization.Gauge(document.getElementById('gauge'));

  var data = google.visualization.arrayToDataTable([
    ['Label', 'Value'],
    ['Collected', 0]
  ]);
  chart.draw(data, options);

  data = google.visualization.arrayToDataTable([
    ['Label', 'Value'],
    ['Collected', {{ totalalumdata }}]
  ]);
  chart.draw(data, options);

}*/
