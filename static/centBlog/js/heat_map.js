am4core.ready(function () {

// Themes begin
    am4core.useTheme(am4themes_animated);
// Themes end

    var heat_map = am4core.create("heat_map", am4charts.RadarChart);
    heat_map.innerRadius = am4core.percent(30);
    heat_map.fontSize = 11;

    var xAxis = heat_map.xAxes.push(new am4charts.CategoryAxis());
    var yAxis = heat_map.yAxes.push(new am4charts.CategoryAxis());
    yAxis.renderer.minGridDistance = 5;

    xAxis.renderer.labels.template.location = 0.5;
    xAxis.renderer.labels.template.bent = true;
    xAxis.renderer.labels.template.radius = 5;

    xAxis.dataFields.category = "hour";
    yAxis.dataFields.category = "weekday";

    xAxis.renderer.grid.template.disabled = true;
    xAxis.renderer.minGridDistance = 10;

    yAxis.renderer.grid.template.disabled = true;
    yAxis.renderer.inversed = true;

// this makes the y axis labels to be bent. By default y Axis labels are regular AxisLabels, so we replace them with AxisLabelCircular
// and call fixPosition for them to be bent
    var yAxisLabel = new am4charts.AxisLabelCircular();
    yAxisLabel.bent = true;
    yAxisLabel.events.on("validated", function (event) {
        event.target.fixPosition(-90, am4core.math.getDistance({x: event.target.pixelX, y: event.target.pixelY}) - 5);
        event.target.dx = -event.target.pixelX;
        event.target.dy = -event.target.pixelY;
    })
    yAxis.renderer.labels.template = yAxisLabel;

    var series = heat_map.series.push(new am4charts.RadarColumnSeries());
    series.dataFields.categoryX = "hour";
    series.dataFields.categoryY = "weekday";
    series.dataFields.value = "value";
    series.sequencedInterpolation = true;

    var columnTemplate = series.columns.template;
    columnTemplate.strokeWidth = 2;
    columnTemplate.strokeOpacity = 1;
    columnTemplate.stroke = am4core.color("#ffffff");
    columnTemplate.tooltipText = "{weekday}, {hour}: {value.workingValue.formatNumber('#.')}";
    columnTemplate.width = am4core.percent(100);
    columnTemplate.height = am4core.percent(100);

    heat_map.seriesContainer.zIndex = -5;

    columnTemplate.hiddenState.properties.opacity = 0;

// heat rule, this makes columns to change color depending on value
    series.heatRules.push({
        target: columnTemplate,
        property: "fill",
        min: am4core.color("#96ffab"),
        max: am4core.color("#0067f8")
    });

// heat legend

    var heatLegend = heat_map.bottomAxesContainer.createChild(am4charts.HeatLegend);
    heatLegend.width = am4core.percent(100);
    heatLegend.series = series;
    heatLegend.valueAxis.renderer.labels.template.fontSize = 9;
    heatLegend.valueAxis.renderer.minGridDistance = 30;

// heat legend behavior
    series.columns.template.events.on("over", function (event) {
        handleHover(event.target);
    })

    series.columns.template.events.on("hit", function (event) {
        handleHover(event.target);
    })

    function handleHover(column) {
        if (!isNaN(column.dataItem.value)) {
            heatLegend.valueAxis.showTooltipAt(column.dataItem.value)
        } else {
            heatLegend.valueAxis.hideTooltip();
        }
    }

    series.columns.template.events.on("out", function (event) {
        heatLegend.valueAxis.hideTooltip();
    })

    var read_amt_obj_lst = []
    var data = []

    $.ajax({
        url: '/get_heatmap_data/',
        type: 'POST',
        dataType: 'JSON',
        traditional: true,
        async: false,
        data: {
            csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val(),
        },
        success: function (args) {
            read_amt_obj_lst = args;
        }
    })

    for (let i = 0; i < read_amt_obj_lst.length; i++) {
        data.push({
            "hour": new Date(read_amt_obj_lst[i].sumup_date).getMonth(),
            "weekday": new Date(read_amt_obj_lst[i].sumup_date).getDay(),
            "value": new Date(read_amt_obj_lst[i].sumup_read_amt).getDay(),
        })
    }


    heat_map.data = data

}); // end am4core.ready()