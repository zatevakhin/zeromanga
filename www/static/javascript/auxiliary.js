
JSON.isjson = function(s) {
    try {
        JSON.parse(s);
    } catch (e) {
        return false;
    }
    return true;
};

String.prototype.cut = function (l) {
    if (this.length > l) {
        return this.slice(0, l) + "…";
    }
    return this;
};

Array.prototype.rand = function () {
    return this[Math.floor(Math.random() * (this.length - 1))];
};

let aux = {
    range: function (begin, end) {
        let range = [];
        for (let i = begin; i < end; ++i) {
            range.push(i);
        }
        return range;
    },
    template: function(templateid, data) {
        return document.getElementById(templateid).innerHTML.replace(/{(\w*)}/g, function(m, key) {
          return data.hasOwnProperty(key) ? data[key] : "";
        });
    }
};

String.prototype.trim = function () {
    return String(this).replace(/^[\n\s]+|[\n\s]+$/g, '');
};

String.prototype.strip = function (s) {
    if (!s) {
        throw new Error("Missing first argument!");
    }
    let regex = new RegExp("^[{1}]+|[{0}]+$".format(s, s), "gi");
    return String(this).replace(regex, '');
};
