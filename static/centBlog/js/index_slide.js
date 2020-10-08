let all_childrens = $('#slide_boxes').children()
let next_index = 0
let current_index = 0


function autoPlay(curr_index) {
    setInterval(function () {
        curr_index = next_index
        next_index = curr_index + 1

        if (next_index === all_childrens.length) {
            next_index = 0
        }

        setTimeout(function () {
            $(all_childrens[curr_index]).hide(1000)
            $(all_childrens[next_index]).fadeIn(1000)
            // $($(all_childrens[next_index]).children()).children().fadeIn(2000)
        }, 4000)
    }, 4500)
}

$(function () {
    autoPlay(current_index)
})