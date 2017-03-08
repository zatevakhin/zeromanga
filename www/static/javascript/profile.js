"use strict";


function Menu() {
    this.actions = {};
}

Menu.prototype.run = function () {
    let self = this;
    self.bind();
};

Menu.prototype.addAction = function (name, callback) {
    this.actions[name] = callback;
};


Menu.prototype.bind = function () {
    let self = this;
    $("#controls").on('click', 'span[data-action]', function (evt) {

        let action = evt.target.getAttribute("data-action");
        if (self.actions.hasOwnProperty(action)) {
            self.actions[action](self);
        }

    });
};


function MCUserProfile() {
    this.menu = new Menu();
}

MCUserProfile.prototype.run = function () {

    let self = this;
    self.menu.run();


    self.menu.addAction("add", function () {

        zk.set("popup-close", {key:"escape", func: function () {
            $("#x-modal").remove();
            zk.unbind("escape");
        }});


        let paragraph1 = $("<p/>", {
            "html": [
                'На данный момент поддерживаются следующие сайты:<br/>',
                `<ul>
                  <li><a href="http://mintmanga.com">http://mintmanga.com</a></li>
                  <li><a href="http://readmanga.me">http://readmanga.me</a></li>
                </ul>`,
            ]
        });

        let input = $("<input/>", {
            "type": "text", "class": "add-new-manga",
            "placeholder": "ссылка на мангу, прим: http://mintmanga.com/octave",
        });

        let button = $("<input/>", {"type": "button", "class": "add-new-manga-button", "value": "Добавить"});

        let close = $("<span/>", {"class": "x-form-modal-close", "text": "❌"});

        // ---------------------------------------------------------------------------
        close.on("click", function () {
            $("#x-modal").remove();
            zk.unbind("escape");
        });

        // ---------------------------------------------------------------------------
        button.on("click", function () {
            let url = input.val();

            if (!url.match(/http\:\/\/\w+[.][come]{2,3}\/\w{2,}[^/]/i)) {
                Notify.show("Ошибка", "эта ссылка не поддерживается!", 2);
                return;
            }

            $.post("/profile", {"action": "add-manga", "url": url}, function () {
                Notify.show("Инфо", "Ссылка была добавлена в очередь на проверку.", 2);

                $("#x-modal").remove();
                zk.unbind("escape");
            });



        });

        let form = $("<div/>", {
            "class": "x-form-modal",
            "html": [paragraph1, input, button, close]
        });


        $("<div/>", {

            "id": "x-modal",
            "html": [form]

        }).appendTo("body");

    });


};


$(function () {
    let mcApp = new MCUserProfile();
    mcApp.run();
});
