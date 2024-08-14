function makeMove(cellId) {
    $.ajax({
        url: '/make-move/',
        type: 'POST',
        data: {
            cell: cellId,
            csrfmiddlewaretoken: document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        success: function(response) {
            document.getElementById('board').innerHTML = response.board_html;
        },
        error: function(error) {
            console.error("Error making move:", error);
        }
    });
}
