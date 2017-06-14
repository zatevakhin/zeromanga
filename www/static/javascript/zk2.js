/**
 * Created by zatevaxin on 03.02.17.
 */

let zk = {

    active_listeners: {},
    backup_listeners: {},
    keydown_timeout: null,

    bind: function () {
        Array.from(arguments).map((e) => {
            let listener = this.backup_listeners[e];
            this.active_listeners[listener.key] = listener.func;
        });
    },

    unbind: function () {
        Array.from(arguments).map((e) => {
            delete this.active_listeners[e];
        });
    },

    set: function (name, key, func) {
        this.backup_listeners[name] = {key: key, func: func};
    },

    get: function (name) {
        return this.backup_listeners[name];
    },

    remove: function (key) {
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
        document.addEventListener("keydown", (e) => {
            console.debug(e);
            let k = e.key.toLowerCase();

            if (this.active_listeners[k]) {
                if (this.keydown_timeout) {
                    clearTimeout(this.keydown_timeout);
                }

                this.keydown_timeout = setTimeout(() => {
                    this.active_listeners[k](e);
                }, 200);
            }
            return false;
        });
    }
};
