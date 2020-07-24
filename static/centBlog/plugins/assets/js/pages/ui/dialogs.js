$(function () {
    $('.js-sweetalert').on('click', function () {
        var type = $(this).data('type');
        if (type === 'basic') {
            showBasicMessage();
        }
        else if (type === 'with-title') {
            showWithTitleMessage();
        }
        else if (type === 'success') {
            showSuccessMessage();
        }
        else if (type === 'confirm') {
            showConfirmMessage();
        }
        else if (type === 'cancel') {
            showCancelMessage();
        }
        else if (type === 'with-custom-icon') {
            showWithCustomIconMessage();
        }
        else if (type === 'html-message') {
            showHtmlMessage();
        }
        else if (type === 'autoclose-timer') {
            showAutoCloseTimerMessage();
        }
        else if (type === 'prompt') {
            showPromptMessage();
        }
        else if (type === 'ajax-loader') {
            showAjaxLoaderMessage();
        }
    });
});

//These codes takes from http://t4t5.github.io/sweetalert/
function showBasicMessage() {
    swal("Here's a message!");
}

function showWithTitleMessage() {
    swal("Here's a message!", "It's pretty, isn't it?");
}

function showSuccessMessage() {
    swal("Good job!", "You clicked the button!", "success");
}

function showConfirmMessage() {
    swal({
        title: "Are you sure?",
        text: "You will not be able to recover this imaginary file!",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#dc3545",
        confirmButtonText: "Yes, delete it!",
        closeOnConfirm: false
    }, function () {
        swal("Deleted!", "Your imaginary file has been deleted.", "success");
    });
}

function showCancelMessage() {
    swal({
        title: "确定创建吗？",
        text: "创建之后你将无法更改关于博客站点的信息",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#dc3545",
        confirmButtonText: "是的，创建！",
        cancelButtonText: "不了，再想想",
        closeOnConfirm: false,
        closeOnCancel: false
    }, function (isConfirm) {
        if (isConfirm) {
            let null_check = false;     // 定义是否为空的检查者变量
            let title = $('#site_title').val()
            let name = $('#site_name').val()
            let theme = $('#site_theme').val()
            let desc = $('#site_desc').val()
            if ($.trim(title) === "" || $.trim(name) === "" || $.trim(theme) === "" || $.trim(desc) === "") {  // 未填或空格符检查
                alert("所填选项不能为空！")
                return
            } else {
                null_check = true
            }
            if (null_check && $("input[type='checkbox']").is(':checked')) {     // 是否认同协议并通过检查
                $.ajax({
                url: '/create_blog/',
                type: 'POST',
                data: {
                    'site_title': title,
                    'site_name':  name,
                    'site_theme': theme,
                    'site_desc':  desc,
                    'csrfmiddlewaretoken': $("[name='csrfmiddlewaretoken']").val(),
                },
                success: function () {
                    swal("完成", "你的博客已成功创建", "success");
                    if(isConfirm){
                        location.href = "/"
                    }
                }
            })
            } else {
                alert("请检查未填选项.")
            }
        } else {
            swal("已取消", "你可以再一次修改站点信息", "error");
        }
    });
}

function showWithCustomIconMessage() {
    swal({
        title: "Sweet!",
        text: "Here's a custom image.",
        imageUrl: "https://via.placeholder.com/128x128"
    });
}

function showHtmlMessage() {
    swal({
        title: "HTML <small>Title</small>!",
        text: "A custom <span style=\"color: #CC0000\">html<span> message.",
        html: true
    });
}

function showAutoCloseTimerMessage() {
    swal({
        title: "Auto close alert!",
        text: "I will close in 2 seconds.",
        timer: 2000,
        showConfirmButton: false
    });
}

function showPromptMessage() {
    swal({
        title: "An input!",
        text: "Write something interesting:",
        type: "input",
        showCancelButton: true,
        closeOnConfirm: false,
        animation: "slide-from-top",
        inputPlaceholder: "Write something"
    }, function (inputValue) {
        if (inputValue === false) return false;
        if (inputValue === "") {
            swal.showInputError("You need to write something!"); return false
        }
        swal("Nice!", "You wrote: " + inputValue, "success");
    });
}

function showAjaxLoaderMessage() {
    swal({
        title: "Ajax request example",
        text: "Submit to run ajax request",
        type: "info",
        showCancelButton: true,
        closeOnConfirm: false,
        showLoaderOnConfirm: true,
    }, function () {
        setTimeout(function () {
            swal("Ajax request finished!");
        }, 2000);
    });
}