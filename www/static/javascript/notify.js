"use strict";

if (!String.prototype.format) {
    String.prototype.format = function () {
        let args = arguments;
        return this.replace(/{(\d+)}/g, function (match, number) {
            return typeof args[number] != 'undefined' ? args[number] : match;
        });
    };
}

let unixtime = function () {
    return Math.round(new Date().getTime() / 1000);
};

let Notify = {
    show: function (title, msg, timeout, obj) {
        let msgid = unixtime();
        $("<div/>", {
            "class": "notify-msg",
            "id": "notify-{0}".format(msgid),
            "css": (obj ? obj : {}),
            "html": [
                $("<div/>", {
                    "class": "notify-msg-title",
                    "html": title
                }),
                $("<div/>", {
                    "class": "notify-msg-body",
                    "html": msg
                })
            ]
        }).appendTo('body');

        // $('body').append('<div class="notify-msg" id="notify-{2}">\
        //             <div class="notify-msg-title">{0}</div>\
        //             <div class="notify-msg-body">{1}</div>\
        //             </div>'.format(title, msg, msgid));

        $('#notify-{0}'.format(msgid)).fadeIn(200);


        setTimeout(function () {
            $('#notify-{0}'.format(msgid)).fadeOut(200);

            // -----------------------------------------------------------------------
            setTimeout(function () {
                $('#notify-{0}'.format(msgid)).remove();
            }, 300);

        }, (timeout * 1000));
    }
    //,
    // notifyPool: function() {
    //   $('body').append('<div id="notify-pool" class="notify-pool-collapsed"></div>');
    //   $('body').append('<div id="notify-pool" class="notify-pool-expanded"></div>');
    // }
};
