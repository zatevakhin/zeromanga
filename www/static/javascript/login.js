"use strict";

class ZeroMangaLogin {
    constructor() {
        this.errors = {
            "E1":{"status": "Error", "msg": "Login is empty!"},
            "E2":{"status": "Error", "msg": "Password is empty!"},
            "E3":{"status": "Error", "msg": "Incorrect login or password!"}
        }
    }

    getError() {
        let error = this.errors[cookie.get("code")];
        cookie.remove("code");
        return error;
    }

    run() {

        if (cookie.get("code")) {
            let error = this.getError();
            Notify.show(error.status, error.msg, 5);
        }

        $('body .form form').on('submit', () => {
            let login = $("body input.form__login").val();
            let password = $("body input.form__passwd").val();

            if (!login) {
                Notify.show("Error", "Enter your login!", 5);
                return false;
            }

            if (!password) {
                Notify.show("Error", "Enter your password!", 5);
                return false;
            }
        });
    }
}


$(() => {
    let app = new ZeroMangaLogin();
    app.run();
});
