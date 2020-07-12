/*-------------------------------------------------------------
*
*
*           This module has been done in 2020-07-11
*
*
*
*       Just do it, and you can find your own way to go.
*                                            ———— Dandelion
*
*
*   Note: This status is debug, if you want to release, please
*                      CANCEL ALL COMMENTS.
*
*-----------------------------------------------------------*/



am4core.ready(function () {
    var read_amount = am4core.create("read_amount", am4charts.XYChart);
    var read_amt_obj_lst = []
    var data = [];
    var price1, price2;
    var quantity;

        $.ajax({
            url: '/get_readamt_data/',
            type: 'POST',
            dataType:'JSON',
            traditional:true,
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
            date1: read_amt_obj_lst[i].sumup_date,
            price1:  read_amt_obj_lst[i].sumup_read_amt
        });
        data.push({
            date2: read_amt_obj_lst[i].sumup_date,
            price2:  read_amt_obj_lst[i].sumup_credit_value
        });
    }

    read_amount.data = data;

    let dateAxis = read_amount.xAxes.push(new am4charts.DateAxis());
    dateAxis.renderer.grid.template.location = 0;
    dateAxis.renderer.labels.template.fill = am4core.color("#e59165");

    let dateAxis2 = read_amount.xAxes.push(new am4charts.DateAxis());
    dateAxis2.renderer.grid.template.location = 0;
    dateAxis2.renderer.labels.template.fill = am4core.color("#dfcc64");

    let valueAxis = read_amount.yAxes.push(new am4charts.ValueAxis());
    valueAxis.tooltip.disabled = true;
    valueAxis.renderer.labels.template.fill = am4core.color("#e59165");

    valueAxis.renderer.minWidth = 60;

    let valueAxis2 = read_amount.yAxes.push(new am4charts.ValueAxis());
    valueAxis2.tooltip.disabled = true;
    valueAxis2.renderer.labels.template.fill = am4core.color("#dfcc64");
    valueAxis2.renderer.minWidth = 60;
    valueAxis2.syncWithAxis = valueAxis;

    let series = read_amount.series.push(new am4charts.LineSeries());
    series.name = "积分";
    series.dataFields.dateX = "date1";
    series.dataFields.valueY = "price1";
    series.tooltipText = "{valueY.value}";
    series.fill = am4core.color("#e59165");
    series.stroke = am4core.color("#e59165");
    //series.strokeWidth = 3;

    var series2 = read_amount.series.push(new am4charts.LineSeries());
    series2.name = "浏览量";
    series2.dataFields.dateX = "date2";
    series2.dataFields.valueY = "price2";
    series2.yAxis = valueAxis2;
    series2.xAxis = dateAxis2;
    series2.tooltipText = "{valueY.value}";
    series2.fill = am4core.color("#dfcc64");
    series2.stroke = am4core.color("#dfcc64");
    //series2.strokeWidth = 3;

    read_amount.cursor = new am4charts.XYCursor();
    read_amount.cursor.xAxis = dateAxis2;

    let scrollbarX = new am4charts.XYChartScrollbar();
    scrollbarX.series.push(series);
    read_amount.scrollbarX = scrollbarX;

    read_amount.legend = new am4charts.Legend();
    read_amount.legend.parent = read_amount.plotContainer;
    read_amount.legend.zIndex = 100;

    valueAxis2.renderer.grid.template.strokeOpacity = 0.07;
    dateAxis2.renderer.grid.template.strokeOpacity = 0.07;
    dateAxis.renderer.grid.template.strokeOpacity = 0.07;
    valueAxis.renderer.grid.template.strokeOpacity = 0.07;

}); // end am4core.ready()