"use strict";


function UsersControl() {
    this.groups = [];
}

UsersControl.prototype.run = function () {
    let self = this;

    self.load_users();
    self.load_groups();

    $("table.users")
        .on("click", '.action-remove', function (e) {
            self.user_remove(e);
        })
        .on("click", '.action-edit', function (e) {
            self.popup_edit_user(e);
        });

    $("table.groups")
      .on("click", '.action-remove', function (e) {
          self.group_remove(e);
      })
      .on("click", '.action-edit', function (e) {
          self.group_edit(e);
      });

    $("#controls")
        .on("click", 'span[data-action=add-user]', function (e) {
            self.popup_add_user(e);
        })
        .on("click", 'span[data-action=add-group]', function (e) {
            self.popup_add_group(e);
        });

};

UsersControl.prototype.load_users = function () {
    let users_t = $("table.users tbody");

    $.post("/users", {'action': 'get-users'})
        .done(function (data) {
            if (JSON.isjson(data)) {
                users_t.empty();
                JSON.parse(data).map(function (e) {
                    users_t.append(aux.template("template-user", e));
                });
            }
        });

};

UsersControl.prototype.load_groups = function () {
    let self = this;
    let groups_t = $("table.groups tbody");

    $.post("/users", {'action': 'get-groups'})
        .done(function (data) {
            if (JSON.isjson(data)) {
                data = JSON.parse(data);
                self.groups = data;

                groups_t.empty();
                data.map(function (e) {
                    groups_t.append(aux.template("template-group", e));
                });
            }
        });

};

UsersControl.prototype.popup_add_user = function () {
    let self = this;
    let body = $("body");
    body.append(aux.template('template-user-add'));

    let popup = $("#popup-main");

    popup.find("select[name=group]").append(self.groups.map(function (e) {
        return $("<option/>", {"value": e.id, "text": e.name});
    }));

    body.on('click', 'div.popup-centred input[data-action=user-add]', function () {


        let login = popup.find("input[name=login]").val();
        let passwd = popup.find("input[name=passwd]").val();
        let group = popup.find("select[name=group]").val();

        if (!login) {
            Notify.show("Ошибка", "Логин не задан!", 2);
            return;
        }

        if (!passwd) {
            Notify.show("Ошибка", "Пароль не задан!", 2);
            return;
        }

        if (parseInt(group) <= 0) {
            Notify.show("Ошибка", "Группа не выбрана!", 2);
            return;
        }

        $.post("/users", {'action': 'user-add', "login": login, "passwd": passwd, "group": group})
            .done(function () {
                self.load_users();
            });

        body.off("click");
        popup.remove();
    });

    body.on('click', 'div.popup-centred input[data-action=popup-cancel]', function () {
        body.off("click");
        popup.remove();
    });

};

UsersControl.prototype.popup_edit_user = function (e) {
    let self = this;

    let tr = $(e.target).parents('tr');

    let body = $("body");

    let gid = tr.data("gid");
    let uid = tr.data("uid");

    body.append(aux.template('template-user-edit', {
        'login': tr.data("login"),
        'passwd': tr.data("passwd"),
        'gid': gid
    }));

    let popup = $("#popup-main");

    popup.find("select[name=group]").append(self.groups.map(function (e) {
        console.log(e.id, gid,  e.id === gid);
        return $("<option/>", {"value": e.id, "text": e.name, "selected": e.id === gid});
    }));

    body.on('click', 'div.popup-centred input[data-action=user-edit]', function () {
        let login = popup.find("input[name=login]").val();
        let passwd = popup.find("input[name=passwd]").val();
        let group = popup.find("select[name=group]").val();

        $.post("/users", {'action': 'user-edit', "id": uid, "login": login, "passwd": passwd, "group": group})
            .done(function () {
                self.load_users();
            });
        body.off("click");
        popup.remove();
    });

    body.on('click', 'div.popup-centred input[data-action=popup-cancel]', function () {
        body.off("click");
        popup.remove();
    });
};


UsersControl.prototype.popup_add_group = function () {
    let self = this;
    let body = $("body");
    body.append(aux.template('template-group-add'));

    let popup = $("#popup-main");

    body.on('click', 'div.popup-centred input[data-action=group-add]', function () {

        let name = popup.find("input[name=name]").val();

        if (!name) {
            Notify.show("Ошибка", "Не задано название группы!", 2);
            return;
        }

        $.post("/users", {'action': 'group-add', "name": name})
            .done(function () {
                self.load_groups();
            });

        body.off("click");
        popup.remove();
    });

    body.on('click', 'div.popup-centred input[data-action=popup-cancel]', function () {
        body.off("click");
        popup.remove();
    });
};

UsersControl.prototype.group_edit = function (e) {
    let self = this;

    let tr = $(e.target).parents('tr');

    let body = $("body");

    let gid = tr.data("gid");

    body.append(aux.template('template-group-add', {'name': tr.data("name")}));

    let popup = $("#popup-main");

    body.on('click', 'div.popup-centred input[data-action=group-add]', function () {
        let name = popup.find("input[name=name]").val();

        $.post("/users", {'action': 'group-edit', "id": gid, "name": name})
            .done(function () {
                self.load_groups();
                self.load_users();
            });
        body.off("click");
        popup.remove();
    });

    body.on('click', 'div.popup-centred input[data-action=popup-cancel]', function () {
        body.off("click");
        popup.remove();
    });
};

UsersControl.prototype.group_remove = function (e) {
    let self = this;

    let tr = $(e.target).parents('tr');
    $.post('/users', {'action': 'group-remove', 'id': tr.data('gid')})
        .done(function () {
            self.load_groups();
        });
};

UsersControl.prototype.user_remove = function (e) {
    let self = this;

    let tr = $(e.target).parents('tr');
    $.post('/users', {'action': 'user-remove', 'id': tr.data('uid')})
        .done(function () {
            self.load_users();
        });
};

$(function () {
    let app = new UsersControl();
    app.run();
});
