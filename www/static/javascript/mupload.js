"use strict";


function MUpload() {
    zk.listen();
}

MUpload.prototype.run = function () {
    let self = this;

    $("table tr").on('click', 'td[data-action]', self.click_action);
    $("body > div.nav").on('click', 'span[data-action=add]', self.add_manga);

};

MUpload.prototype.click_action = function () {
    let uhash = $(this).parent("tr").data("uhash");

    $.post('/mupload', { action: $(this).data("action"), uhash: uhash })
        .done(function (data) {
            Notify.show(data.status, data.msg, 3);
        })
        .fail(function (data) {
            data = data.responseJSON;
            Notify.show(data.status, data.msg, 3);
        });
};


MUpload.prototype.add_manga = function() {
    let popup = aux.template("template-upload", {
        "text": "Поддерживаемые ресурсы:",
        "resources": $("#main").data("resources").split(",").map(function (resource) {
            return `<li><a href='http://${resource}'>http://${resource}</a></li>`;
        }).join("")
    });

    let body = $("body");

    body.append(popup);

    zk.set("popup-close", "escape", function () {
        $("body .popup").remove();
        zk.unbind("escape");
    });

    zk.bind("popup-close");

    $("body .popup")
        .on('click', 'input[data-popup=cancel]', function(e) {
            zk.get("popup-close").func(e);
        })
        .on('click', 'input[data-popup=execute]', function() {
            let url = $('input[name=url]').val();
            
            $.post("/mupload", {"action": "manga-add", "url": url})
                .done(function (data) {
                    Notify.show(data.status, data.msg, 3);
                    $("body .popup").off().remove();
                })
                .fail(function (data) {
                    data = data.responseJSON;
                    Notify.show(data.status, data.msg, 3);
                });
        });
};


$(function () {
    let app = new MUpload();
    app.run();
});
