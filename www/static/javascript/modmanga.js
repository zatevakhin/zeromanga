"use strict";


function AAModManga() {

}

AAModManga.prototype.run = function () {

    let self = this;

    $("table tr").on('click', 'td[data-action]', self.clickAction);

};

AAModManga.prototype.clickAction = function () {
    let self = this;

    let uhash = $(this).parent("tr").data("uhash");

    let jqxhr = $.post('/uqueue', { action: $(this).data("action"), uhash: uhash });

    jqxhr.done(function (data) {
       console.debug(data)
    });

    jqxhr.fail(function (e) {
        console.debug(e);
    });

    // jqxhr.success((obj) => {
    //     if (!obj.IsJson()) {
    //         console.debug(obj);
    //         return;
    //     }
    //
    //     let jsobj = JSON.parse(obj);
    //
    //     if (jsobj.status == "ok") {
    //         Notify.show("Выполнено", jsobj.msg, 3, {"background": "black"});
    //         return;
    //     }
    //
    //     if (jsobj.status == "error") {
    //         Notify.show("Ошибка", jsobj.msg, 3, {"background": "black"});
    //         return;
    //     }
    //
    //     console.debug(jsobj);
    // });



};


$(function () {
    let app = new AAModManga();
    app.run();
});
