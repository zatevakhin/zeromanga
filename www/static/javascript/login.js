let codes = {
    "0x00": {"title": "Ошибка", "msg": "Неизвестная ошибка.",            "time": 15},
    "0x01": {"title": "Ошибка", "msg": "Сессия не авторизирована!",      "time": 10},
    "0x02": {"title": "Ошибка", "msg": "Неправельный логин или пароль.", "time": 10},
    "0x03": {"title": "Ошибка", "msg": "Введите логин.",                 "time": 10},
    "0x04": {"title": "Ошибка", "msg": "Введите пароль.",                "time": 10}
};


function ALogin() {
    this.regexErrorCode = new RegExp("^0x([a-f0-9]{2})$", "gi");
}


ALogin.prototype.run = function () {
    let self = this;

    if (self.regexErrorCode.test(cookie.get("ecode"))) {
        self.showErrorByCode(cookie.get("ecode"));
        cookie.del("ecode");
    }

    $('#form').on('submit', function () {
        if (!$("input[type=password]").val()) {
            self.showErrorByCode("0x03");
            return false;
        }

        if (!$("input[type=text]").val()) {
            self.showErrorByCode("0x04");
            return false;
        }
    })

};


ALogin.prototype.showErrorByCode = function (code) {
    if (code && code in codes) {
        Notify.show(codes[code].title, codes[code].msg, codes[code].time);
    } else {
        Notify.show(codes["000"].title, codes["000"].msg, codes["000"].time);
    }
};


$(function () {
    let alApp = new ALogin();
    alApp.run();
});