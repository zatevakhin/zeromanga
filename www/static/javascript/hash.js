/**
 * Created by zatevaxin on 31.01.17.
 */
"use strict";

let Hash = {

    parse: function() {
        let obj = {};
        let hash = window.location.hash;

        if (!hash || !hash.startsWith("#")) {
            return obj;
        }

        let list = hash.substring(1).split("/");

        for (let index in list) {
            if (list.hasOwnProperty(index)) {
                if (list[index].indexOf(":") > 0) {
                    let element =  list[index].split(":");
                    obj[ element[0] ] = element[1];
                }
            }
        }

        return obj;
    },

    get: function (key) {
        let hash = this.parse();
        
        if (key && key instanceof String) {
            return hash[key];
        }

        return hash;
    },

    set: function(obj) {
        let items = [];

        for (let index in obj) {
            if (obj.hasOwnProperty(index)) {
                items.push(`${index}:${obj[index]}`);
            }
        }

        window.location.hash = items.join("/");
    },

    add: function(key, val) {
        let hash = this.parse();
        hash[key] = val;
        this.set(hash);
    },

    remove: function(key) {
        let hash = this.parse();
        delete hash[key];
        this.set(hash);
    },

    clear: function() {
        window.history.pushState('', document.title, window.location.pathname);
    }

};