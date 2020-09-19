/*
*   This is only public static modle.
*
*   Author: Dandelion
*   Press: 2020 - 07 - 01
*   Status: Final
* */

function sayHello(jquery_elem_id) {
    let now = new Date(); let hour = now.getHours();
    if(hour < 6 && hour > 2)   {$(jquery_elem_id)[0].innerHTML = "美好的一天，准备经历全力以赴吧"}
    else if (hour < 9)         {$(jquery_elem_id)[0].innerHTML = "满满的活力，好心情随叫随到啊"}
    else if (hour < 12)        {$(jquery_elem_id)[0].innerHTML = "年轻的你，会在选择面前变得犹豫吗"}
    else if (hour < 14)        {$(jquery_elem_id)[0].innerHTML = "辛苦了，来一杯下午茶吧，放松一下"}
    else if (hour < 17)        {$(jquery_elem_id)[0].innerHTML = "下午好，这将是一个等待延续的故事"}
    else if (hour < 19)        {$(jquery_elem_id)[0].innerHTML = "夕阳好漂亮啊，一起去看看吧"}
    else if (hour < 23)        {$(jquery_elem_id)[0].innerHTML = "生活总会在意外之间变得美妙，晚安"}
    else                       {$(jquery_elem_id)[0].innerHTML = "有些条路你必须坚持下去，保持清醒"}
}

