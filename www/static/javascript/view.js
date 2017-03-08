"use strict";


function MangaView() {
    this.mangaid = $("#article").data("mangaid");

    this.chash = undefined;

    zk.listen();
}


MangaView.prototype.run = function () {
    let self = this;

    $("#article").on('click', 'div.chaptlist > div', function (e) {
        zk.bind("view-chapter-escape");
        self.chash = e.target.getAttribute("data-chaptid");
        self.show_thumbnails(self.chash);
    });

    $("body").on('click', 'div.chapt-thumb', function (e) {
        zk.bind("manga-page-escape");
        self.show_page(parseInt(e.target.getAttribute("data-image")));
    });


    zk.set("view-chapter-escape", {
        key: "escape", func: function (e) {
            zk.unbind("escape");

            zk.unbind("arrowdown");
            zk.unbind("arrowup");
            zk.unbind("arrowleft");
            zk.unbind("arrowright");

            self.chash = undefined;

            $("#chapt-view").fadeOut("fast", function () {
                $("#chapt-view").remove();
            });
        }
    });

    zk.set("manga-page-escape", {
        key: "escape", func: function (e) {

            zk.unbind("escape");
            zk.unbind("arrowdown");
            zk.unbind("arrowup");

            zk.unbind("arrowleft");
            zk.unbind("arrowright");

            zk.unbind("home");
            zk.unbind("end");

            zk.bind("view-chapter-escape");

            zk.bind("evt-chapter-prev");
            zk.bind("evt-chapter-next");
            zk.bind("evt-chapter-prev-left");
            zk.bind("evt-chapter-next-right");

            $('.manga-page').remove();
        }
    });

    let cover = $("div.cover");
    let current_n = parseInt(cover.data('current'));
    let covers_n = parseInt(cover.data('covers'));

    cover.append(aux.template("template-coverlist", {text: `${current_n} / ${covers_n}`}));

    let coverslist = cover.children("div.covers-list");

    coverslist.on("click", "div.covers-arrow-left", function (e) {
        current_n = parseInt(cover.data('current')) - 1;
        if (current_n > 0 && current_n <= covers_n) {
            cover.css("background-image", `url('/m/${self.mangaid}/c/${current_n}')`);
            cover.data("current", current_n);
            $('div.covers-text').text(`${current_n} / ${covers_n}`);
        }
    });

    coverslist.on("click", "div.covers-arrow-right", function (e) {
        current_n = parseInt(cover.data('current')) + 1;
        if (current_n > 0 && current_n <= covers_n) {
            cover.css("background-image", `url('/m/${self.mangaid}/c/${current_n}')`);
            cover.data("current", current_n);
            $('div.covers-text').text(`${current_n} / ${covers_n}`);
        }
    });
};


MangaView.prototype.show_page = function (imageid) {
    let self = this;

    if (!this.chash || (typeof this.chash) !== "string") {
        console.error("Var `chash` is undefined or not string: ", this.chash);
        return;
    }

    zk.set("page-first", {
        key: "home", func: function (e) {
            let newid = 1;
            if ($(`div.chapt-thumb[data-image=${newid}]`).length) {
                self.show_page(newid);
            }
        }
    });

    zk.set("page-last", {
        key: "end", func: function (e) {
            let last = $("div.chapt-thumb[data-image]").last().data("image");

            let newid = parseInt(last);

            if ($(`div.chapt-thumb[data-image=${newid}]`).length) {
                self.show_page(newid);
            }
        }
    });

    zk.set("page-next-down", {
        key: "arrowdown", func: function (e) {
            let newid = imageid + 1;
            if ($(`div.chapt-thumb[data-image=${newid}]`).length) {
                self.show_page(newid);
                return;
            }

            let index = $(`div.chaptlist div[data-chaptid=${self.chash}]`).data("index");

            index = parseInt(index);

            let chapter = $(`div.chaptlist div[data-index=${index + 1}]`);

            if (chapter.length) {
                self.chash = chapter.data("chaptid");
                self.show_thumbnails(self.chash);
                self.show_page(1);
            }

        }
    });

    zk.set("page-prev-up", {
        key: "arrowup", func: function (e) {
            let newid = imageid - 1;
            if ($(`div.chapt-thumb[data-image=${newid}]`).length) {
                self.show_page(newid);
                return;
            }

            let index = $(`div.chaptlist div[data-chaptid=${self.chash}]`).data("index");

            index = parseInt(index);

            let chapter = $(`div.chaptlist div[data-index=${index - 1}]`);

            if (chapter.length) {
                self.chash = chapter.data("chaptid");
                self.show_thumbnails(self.chash);

                setTimeout(function () {

                    let last = $("div.chapt-thumb[data-image]").last().data("image");

                    last = parseInt(last);

                    self.show_page(last);

                }, 500);

            }

        }
    });

    zk.set("page-prev-left", {key: "arrowleft", func: zk.get("page-prev-up").func});
    zk.set("page-next-right", {key: "arrowright", func: zk.get("page-next-down").func});

    zk.unbind("arrowdown");
    zk.unbind("arrowup");

    zk.unbind("arrowleft");
    zk.unbind("arrowright");

    zk.bind("page-next-down");
    zk.bind("page-prev-up");

    zk.bind("page-next-right");
    zk.bind("page-prev-left");

    zk.bind("page-first");
    zk.bind("page-last");


    let image = new Image();
    image.src = `/p/${this.mangaid}/${this.chash}/${imageid}`;

    if (!$('.manga-page').length) {
        $("body").append(aux.template("template-page", {src: image.src}));
        $('.manga-page img').height($(document).height() - 10);
    } else {
        $('.manga-page img').attr("src", image.src);
    }

    image.onload = function () {
        // console.log(arguments);

        if ($('.manga-page img').width() >= $(document).width()) {
            $('.manga-page img').height($(document).height() - 10);
        }


        $('.manga-page').off("wheel", "img");
        $('.manga-page').on("wheel", "img", function (evt) {
            self.wheelHandle(evt, $(this), image)
        });

        if (cookie.get("dfsid")) {
            $(`div.chapt-thumb[data-image='${imageid}']`).attr("data-readed", 1);

            let all = $("div.chapt-flexbox div.chapt-thumb").length;
            let readed = $("div.chapt-flexbox div.chapt-thumb[data-readed]").length;

            $(`div[data-chaptid=${self.chash}] span.viewer_chapts_reading`).text(`${readed} / ${all}`);
        }
    };

    $('.manga-page img').draggable({
        stop: function (event, ui) {

            let direct = ui.originalPosition.left > ui.position.left ? 'left' : 'right';
            let elem = $(this);
            let dwidth = $(document).width();

            if (direct && direct == "left" && ui.originalPosition.left > (ui.position.left + (dwidth / 3.5))) {
                zk.get("page-next-down").func();
                elem.animate({"left": (-1) * dwidth, opacity: "hide"}, "fast", "linear", function () {
                    elem.css({"left": `${(dwidth)}px`});
                    elem.animate({"left": 0, opacity: "show"}, "fast", "linear");
                });

            } else if (direct && direct == "right" && ui.originalPosition.left < (ui.position.left - (dwidth / 3.5))) {
                zk.get("page-prev-up").func();
                elem.animate({"left": dwidth, opacity: "hide"}, "fast", "linear", function () {
                    elem.css({"left": `${((-1) * dwidth)}px`});
                    elem.animate({"left": 0, opacity: "show"}, "fast", "linear");
                });

            } else if (direct && ($(this).width() + 100) <= dwidth) {
                $(this).animate({"left": 0}, "fast", "linear");
            }

        }
    });
};


MangaView.prototype.show_thumbnails = function (chash) {
    let self = this;

    let index = $(`div.chaptlist div[data-chaptid=${chash}]`).data("index");

    zk.set("evt-chapter-prev", {
        key: "arrowup", func: function (e) {
            let chapter = $(`div.chaptlist div[data-index=${index - 1}]`);
            if (chapter.length) {
                self.show_thumbnails(chapter.data("chaptid"));
            }
        }
    });

    zk.set("evt-chapter-next", {
        key: "arrowdown", func: function (e) {
            let chapter = $(`div.chaptlist div[data-index=${index + 1}]`);
            if (chapter.length) {
                self.show_thumbnails(chapter.data("chaptid"));
            }
        }
    });

    zk.set("evt-chapter-prev-left", {key: "arrowleft", func: zk.get("evt-chapter-prev").func});
    zk.set("evt-chapter-next-right", {key: "arrowright", func: zk.get("evt-chapter-next").func});

    zk.bind("evt-chapter-prev");
    zk.bind("evt-chapter-next");
    zk.bind("evt-chapter-prev-left");
    zk.bind("evt-chapter-next-right");


    let jqxhr = $.post(`/manga/${this.mangaid}`, {"action": "get.thumbnails", "chash": chash});

    jqxhr.done(function (data) {

        let chapter_view = $("#chapt-view");

        if (!chapter_view.length) {
            $("body").append(aux.template("template-chapter", {
                mhash: self.mangaid,
                chash: data.chash
            }));

            chapter_view = $("#chapt-view");
        } else {
            chapter_view.children("div.chapt-blur").css({
                "background-image": `url('/r/${self.mangaid}/${data.chash}')`
            })
        }

        chapter_view.on('click', '.chapt-flexbox', function (e) {
            if (e.target !== this) {
                return;
            }

            zk.get("view-chapter-escape").func();
        });

        let chapt_flexbox = $("div.chapt-flexbox");

        chapt_flexbox.empty();
        for (let i = 1; i <= data.pages; ++i) {
            chapt_flexbox.append(aux.template("template-thumbnail", {
                mhash: self.mangaid,
                chash: data.chash,
                image: i
            }));
        }

        if (data["readed"] && typeof data["readed"] == 'object') {
            data["readed"].forEach(function (item) {
                $(`div.chapt-thumb[data-image='${item}']`).attr("data-readed", 1);
            });
        }


    });


};


MangaView.prototype.show_zipthumbnails = function (chash) {

    let self = this;

    let index = $(`div.chaptlist div[data-chaptid=${chash}]`).data("index");

    zk.set("evt-chapter-prev", {
        key: "arrowup", func: function (e) {
            let chapter = $(`div.chaptlist div[data-index=${index - 1}]`);
            if (chapter.length) {
                self.show_zipthumbnails(chapter.data("chaptid"));
            }
        }
    });

    zk.set("evt-chapter-next", {
        key: "arrowdown", func: function (e) {
            let chapter = $(`div.chaptlist div[data-index=${index + 1}]`);
            if (chapter.length) {
                self.show_zipthumbnails(chapter.data("chaptid"));
            }
        }
    });

    zk.set("evt-chapter-prev-left", {key: "arrowleft", func: zk.get("evt-chapter-prev").func});
    zk.set("evt-chapter-next-right", {key: "arrowright", func: zk.get("evt-chapter-next").func});

    zk.bind("evt-chapter-prev");
    zk.bind("evt-chapter-next");
    zk.bind("evt-chapter-prev-left");
    zk.bind("evt-chapter-next-right");

    let jqxhr = $.post(`/manga/${self.mangaid}`, {"action": "get.thumbnails", "chash": chash});

    jqxhr.done(function (obj) {
        self.cobj = obj;
    });

    JSZipUtils.getBinaryContent(`/z/${this.mangaid}/${chash}`, function (err, data) {
        if(err) {
            throw err; // or handle the error
        }

        let chapter_view = $("#chapt-view");

        if (!chapter_view.length) {
            $("body").append(aux.template("template-chapter", {
                mhash: self.mangaid,
                chash: chash
            }));

            chapter_view = $("#chapt-view");
        } else {
            chapter_view.children("div.chapt-blur").css({
                "background-image": `url('/r/${self.mangaid}/${chash}')`
            })
        }

        chapter_view.on('click', '.chapt-flexbox', function (e) {
            if (e.target !== this) {
                return;
            }

            zk.get("view-chapter-escape").func();
        });

        let chapt_flexbox = $("div.chapt-flexbox");

        chapt_flexbox.empty();

        let zip = new JSZip();
        zip.loadAsync(data).then(function (z) {
            for (let f in z.files) {
                if (z.files.hasOwnProperty(f)) {
                    z.files[f].async("arraybuffer").then(function (x) {

                        chapt_flexbox.append(aux.template("template-zt", {
                            blob: URL.createObjectURL(new Blob([x])),
                            image: f
                        }));

                        if (self.cobj["readed"] && self.cobj["readed"].indexOf(parseInt(f)) >= 0) {
                            $(`div.chapt-thumb[data-image='${f}']`).attr("data-readed", 1);
                        }
                    })
                }
            }
        });

    });

};


MangaView.prototype.wheelHandle = function (evt, jqthis, img) {

    if (evt.originalEvent.deltaY > 0 && jqthis.height() >= 300) {
        let top = parseInt(jqthis.css("top"));
        let bottom = parseInt(jqthis.css("bottom"));

        if (top && top < 0) {
            jqthis.css("top", `${(top + 10)}px`);
        } else if (bottom && bottom < 0) {
            jqthis.css("top", `${(top - 10)}px`);
        }

        jqthis.height(jqthis.height() - 15);

    } else if (evt.originalEvent.deltaY < 0 && jqthis.height() <= (img.height * 2)) {
        jqthis.height(jqthis.height() + 15);
    }

    if (evt.originalEvent.deltaY != 0) {
        if ((jqthis.width() + 100) <= $(document).width()) {

            if (this.dAnimationTimeout != null) {
                clearTimeout(this.dAnimationTimeout);
            }
            this.dAnimationTimeout = setTimeout(function () {
                jqthis.animate({"left": 0}, "fast", "linear");
            }, 100);

        }
        jqthis.css({"width": "auto"});
    }
};

$(function () {
    let app = new MangaView();
    app.run();
});

