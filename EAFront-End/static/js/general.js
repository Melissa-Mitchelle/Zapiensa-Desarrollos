let table;

$(document).ready(function () {

        $(document)
    .ajaxStart(function() {
        $('#overlay').show();
    })
    .ajaxStop(function() {
        $('#overlay').hide();
    })
    //$('#data thead tr').clone(true).appendTo('#data thead');
    $('#data thead tr:eq(0) th').each(function (i) {
        if(firstSearchableCol <= i && i < lastSearchableCol){
            var title = $(this).text();
            $(this).html('<input type="text" placeholder="Buscar ' + title + '" />');

            $('input', this).on('keyup change', function () {
                if (table.column(i).search() !== this.value) {
                    table
                        .column(i)
                        .search(this.value)
                        .draw();
                }
            });
        }
    });
    table = $('#data').DataTable({
        orderCellsTop: true,
        fixedHeader: true,
        "pageLength": 10,
        "ordering": true,
        "language": {
            "url": "https://cdn.datatables.net/plug-ins/1.10.20/i18n/Spanish.json",
        },
        "columnDefs": [
            //{ "orderable": false, "targets": [ 3 ] }
        ]
    });
        $('#overlay').hide()

    $(".aaction").on("click", function (event) {
        event.preventDefault()
        let id = $(this).data('id');
        let metodo = $(this).data('metodo');
        let rowSelector = $(this).closest('tr');
        $.ajax({
            type: "POST",
            url: "/modificacion",
            datatype: "html",
            data: {
                metodo: metodo,
                id: id
            },
            success: function (data) {
                table.row(rowSelector).remove().draw();
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                alert("Ocurrio un error " + textStatus + errorThrown);
            }
        });
    });
    $(".notificationa a").on("click", function (event) {
        event.preventDefault()
        let id = $(this).closest('tr').data('id');
        let id_receiver_event = $(this).closest('tr').data('id-receiver-event');
        let notification = $(this).data('notification');
        let thisA = $(this);
        let data = {
            id_receiver_event: id_receiver_event
        };
        if (notification === 'confirmado') {
            data['notificated'] = true;
        } else {
            data['notification_no'] = notification;
        }
        if (id !== '') {
            data['id_follow'] = id
        }

        $.ajax({
            type: "POST",
            url: "/seguimiento",
            datatype: "html",
            data: data,
            success: function (data) {
                $(thisA[0]).parent().parent().prev().html($(thisA[0]).html() + '<span class="caret"></span>');
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                alert("Ocurrio un error " + textStatus + errorThrown);
            }
        });
    });
    $(".attendancea").on("click", function (event) {
        event.preventDefault()
        let id = $(this).closest('tr').data('id');
        let id_receiver_event = $(this).closest('tr').data('id-receiver-event');
        let attendance = $(this).is(":checked");
        let thisA = $(this);
        let data = {
            id_receiver_event: id_receiver_event,
            attendance: attendance
        };

        if (id !== '') {
            data['id_follow'] = id
        }

        $.ajax({
            type: "POST",
            url: "/seguimiento",
            datatype: "html",
            data: data,
            success: function (data) {
                $(thisA[0]).prop('checked', !$(thisA[0]).prop('checked'))
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                alert("Ocurrio un error " + textStatus + errorThrown);
            }
        });
    });

;
});
