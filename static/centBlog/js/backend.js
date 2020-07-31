var editor = new Simditor({
    textarea: $('#editor'),
    pasteImage: true,
    toolbar: ['title', 'bold', 'italic', 'underline', 'strikethrough',
        'color', 'fontScale', 'ol', 'ul', 'blockquote', 'code', 'table',
        'link', 'image', 'hr', 'indent', 'outdent', 'alignment'],
    pasteIamge: true,
    codeLanguages: [
        {name: 'Bash', value: 'bash'},
        {name: 'C++', value: 'c++'},
        {name: 'C#', value: 'cs'},
        {name: 'CSS', value: 'css'},
        {name: 'Erlang', value: 'erlang'},
        {name: 'Less', value: 'less'},
        {name: 'Sass', value: 'sass'},
        {name: 'Diff', value: 'diff'},
        {name: 'CoffeeScript', value: 'coffeescript'},
        {name: 'HTML,XML', value: 'html'},
        {name: 'JSON', value: 'json'},
        {name: 'Java', value: 'java'},
        {name: 'JavaScript', value: 'js'},
        {name: 'Markdown', value: 'markdown'},
        {name: 'Objective C', value: 'oc'},
        {name: 'PHP', value: 'php'},
        {name: 'Perl', value: 'parl'},
        {name: 'Python', value: 'python'},
        {name: 'Ruby', value: 'ruby'},
        {name: 'SQL', value: 'sql'},
    ],
    defaultImage: '/media/articles/default.png',
    upload: {
        url: '/upload/',
        params: {csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val()},
        fileKey: 'file',
        leaveConfirm: '正在上传文件..',
        connectionCount: 3
    }
});
var edit_model = false;         //  false:new article,   true: modify one
console.log(edit_model)
editor.on('valuechanged', function (e) {
    $('#fonts_count').text($('.simditor-body').text().length);
})

$('#article_submit').click(function () {
    // 修改模块
    if (edit_model) {
        let title_obj = $('#article_title')
        let article_id = title_obj.attr('article_id');
        let article_title = title_obj.val();
        let article_content = editor.getValue();
        let confirm_lock = confirm("确认修改吗？");

        // 修改提示
        if (confirm_lock) {
            $.ajax({
                url: '/modify/',
                type: 'POST',
                data: {
                    csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val(),
                    mode: 'modify',
                    article_id: article_id,
                    article_title: article_title,
                    article_content: article_content
                },
                success: function (args) {
                    if (args.status) {
                        alert("修改成功！")
                        edit_model = false;
                    } else {
                        alert("修改失败")
                    }
                }
            })
        }
        // 新建文章开始
    } else {
        let title_obj = $('#article_title')
        let article_title = title_obj.val();
        let article_content = editor.getValue();
        if (article_title.length < 1) {
            alert("请输入标题！")
            return
        }
        let confirm_lock = confirm("确认发表吗？");
        if (confirm_lock) {
            $.ajax({
                url: '/modify/',
                type: 'POST',
                data: {
                    csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val(),
                    mode: 'release',
                    article_title: article_title,
                    article_content: article_content
                },
                success: function (args) {
                    if (args.status) {
                        alert("发表成功！")
                        location.reload()
                    } else {
                        alert("发表失败")
                    }
                }
            })
        }
    }
})

// 原文
$('.op').click(function () {
    location.href = `/${$(this).attr('author')}/articles/${$(this).attr('article_id')}`
})

// 修改
$('.md').click(function () {
    let article_id = $(this).attr('article_id')
    $.ajax({
        url: '/modify/',
        type: "POST",
        data: {
            csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val(),
            article_id: article_id,
            mode: 'query',        // 0 -> false -> modify
        },
        success: function (data) {
            console.log(data)
            let box = $("[role='presentation']")
            let title = $('#article_title')
            $(box[1]).removeClass('active')
            $('#search_all').removeClass('active in')
            $(box[0]).addClass('active')
            $('#home').addClass('active in')
            title.val(data.title)
            title.attr('article_id', article_id)
            editor.setValue(data.content)
            edit_model = true;
            console.log(edit_model)
        }
    })
})

// 删除
$('.dt').click(function () {
    let this_obj = $(this)
    let article_id = this_obj.attr('article_id')
    let confirm_lock = confirm("确认删除吗？");
    if (confirm_lock) {
        $.ajax({
            url: '/modify/',
            type: "POST",
            data: {
                csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val(),
                article_id: article_id,
                mode: 'delete',
            },
            success: function (data) {
                if (data.status)
                    this_obj.parent().parent().remove();
            }
        })
    }
})

// 暂存
$('.pause_save').click(function () {
    let confirm_lock = confirm("确认改为发表状态吗？");
    let this_obj = $(this)
    let article_id = this_obj.attr('article_id')
    if (confirm_lock) {
        $.ajax({
            url: '/modify/',
            type: "POST",
            data: {
                csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val(),
                article_id: article_id,
                mode: 'saved',
            },
            success: function (data) {
                if (data.status) {
                    alert("已将此文章对他人可见！")
                }
            }
        })
    }
})
