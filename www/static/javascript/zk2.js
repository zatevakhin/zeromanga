/**
 * Created by zatevaxin on 03.02.17.
 */

let zk = {

    active_listeners: {},
    backup_listeners: {},
    keydown_timeout: null,

    bind: function (name) {
        let listener = this.backup_listeners[name];
        this.active_listeners[listener.key] = listener.func;
    },

    unbind: function (keybind) {
        delete this.active_listeners[keybind];
    },

    set: function (name, obj) {
        this.backup_listeners[name] = obj;
    },

    get: function (name) {
        return this.backup_listeners[name];
    },

    del: function (key) {
        delete this.active_listeners[key];

        for (let i in this.backup_listeners) {
            if (this.backup_listeners.hasOwnProperty(i)) {
                if (this.backup_listeners[i].key === key) {
                    delete this.backup_listeners[i];
                    return;
                }
            }
        }
    },

    listen: function ( ) {
        let self = this;
        document.addEventListener("keydown", function (e) {
            console.debug(e);
            let k = e.key.toLowerCase();

            if (self.active_listeners[k]) {
                if (self.keydown_timeout) {
                    clearTimeout(self.keydown_timeout);
                }

                self.keydown_timeout = setTimeout(function () {
                    self.active_listeners[k](e);
                }, 200);
            }
            return false;
        });

    }
};