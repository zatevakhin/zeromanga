"use strict";

class MangaView {
    constructor() {
        /* Initialize keypress listener */
        zk.listen();

        /* Set keyboard action */
        zk.set("view-escape", "escape", () => {
            zk.unbind("escape", "arrowdown", "arrowup", "arrowleft", "arrowright");

            $("#chapt-view").fadeOut("fast", () => {
                $("#chapt-view").remove();
            });
        });

        zk.set("page-escape", "escape", () => {
            zk.unbind("escape", "arrowdown", "arrowup", "arrowleft", "arrowright");
            zk.bind("chapter-prev-left", "chapter-next-right", "chapter-prev", "chapter-next", "view-escape");

            $(".manga-page").fadeOut("fast", () => {
                $('.manga-page').remove();
            });
        });

        zk.set("page-first", "home", () => {
            let id = 1;
            if ($(`div.chapt-thumb[data-image=${id}]`).length) {
                this.showPage(id);
            }
        });

        zk.set("page-last", "end", () => {
            let last = $("div.chapt-thumb[data-image]").last().data("image");
            let id = parseInt(last);
            if ($(`div.chapt-thumb[data-image=${id}]`).length) {
                this.showPage(id);
            }
        });

        zk.set("page-next-down", "arrowdown", () => {
            let id = this.current.image_id + 1;

            if ($(`div.chapt-thumb[data-image=${id}]`).length) {
                this.showPage(id);
                return;
            }

            let chapter = $(`div.chaptlist div[data-index=${this.current.ch_index + 1}]`);
            if (chapter.length) {
                let chash = this.current.ch_chash;

                this.showChapter(chapter.data("chaptid"));

                let interval_id = setInterval(() => {
                    if (chash !== this.current.ch_chash) {
                        this.showPage(1);
                        clearInterval(interval_id);
                    }
                }, 100);
            }
        });

        zk.set("page-prev-up", "arrowup", () => {
            let id = this.current.image_id - 1;

            if ($(`div.chapt-thumb[data-image=${id}]`).length) {
                this.showPage(id);
                return;
            }

            let chapter = $(`div.chaptlist div[data-index=${this.current.ch_index - 1}]`);
            if (chapter.length) {
                let chash = this.current.ch_chash;

                this.showChapter(chapter.data("chaptid"));

                let interval_id = setInterval(() => {
                    if (chash !== this.current.ch_chash) {
                        this.showPage(this.current.pages);
                        clearInterval(interval_id);
                    }
                }, 100);
            }
        });

        zk.set("page-prev-left", "arrowleft", zk.get("page-prev-up").func);
        zk.set("page-next-right", "arrowright", zk.get("page-next-down").func);

        zk.set("chapter-prev", "arrowup", () => {
            let chapter = $(`div.chaptlist div[data-index=${this.current.ch_index - 1}]`);
            if (chapter.length) {
                this.showChapter(chapter.data("chaptid"));
            }
        });

        zk.set("chapter-next", "arrowdown", () => {
            let chapter = $(`div.chaptlist div[data-index=${this.current.ch_index + 1}]`);
            if (chapter.length) {
                this.showChapter(chapter.data("chaptid"));
            }
        });

        zk.set("chapter-prev-left", "arrowleft", zk.get("chapter-prev").func);
        zk.set("chapter-next-right", "arrowright", zk.get("chapter-next").func);

        $("body").on('click', 'div.chapt-thumb', (e) => {
            zk.bind("page-first", "page-last", "page-next-right", "page-next-down", "page-prev-left", "page-prev-up", "page-escape");
            this.showPage(parseInt(e.target.getAttribute("data-image")));
        });

        /* Define class variabiles */
        let article = $("#article");
        this.mhash = article.data("mangaid");
        this.covers = parseInt(article.find("div.cover").data('covers'));

        /* Object to store some current variabiles */
        this.current = {}
    }

    showChapter(chash) {
        let request = $.post(`/manga/${this.mhash}`, {
            "action": "get.thumbnails", "chash": chash
        });

        if (!$("body #chapt-view").length) {
            $("body").append(aux.template("tt-chapter"));
        }

        let chapter_view = $("#chapt-view");

        chapter_view.find("div.chapt-blur").css({
            "background-image": `url(/r/${this.mhash}/${chash})`
        });

        let chapt_flexbox = $("div.chapt-flexbox");

        request.done((data) => {

            this.current.ch_index = data.index;
            this.current.ch_chash = data.chash;
            this.current.pages = data.pages;

            chapter_view.find(".chapt-nav-current-title").text(data["chapter"]);

            chapter_view.off("click")
                .on("click", '.chapt-nav-prev', zk.get("chapter-prev").func)
                .on("click", '.chapt-nav-next', zk.get("chapter-next").func);

            chapt_flexbox.empty();
            for (let i = 1; i <= data.pages; ++i) {
                chapt_flexbox.append(aux.template("tt-thumbnail", {
                    mhash: this.mhash,
                    chash: data.chash,
                    image: i
                }));
            }

            if (data["readed"] && typeof data["readed"] === 'object') {
                data["readed"].forEach(function (item) {
                    $(`div.chapt-thumb[data-image='${item}']`).attr("data-readed", 1);
                });
            }
        });
    }

    showPage(id) {
        this.current.image_id = id;

        let image = new Image();
        image.src = `/p/${this.mhash}/${this.current.ch_chash}/${id}`;

        if (!$('body .manga-page').length) {
            $("body").append(aux.template("tt-page"));
            $('body .manga-page img').height($(document).height() - 10);
        }

        let im_elem = $('.manga-page img');
        im_elem.attr("src", `/t/${this.mhash}/${this.current.ch_chash}/${id}`);

        $("body div.manga-page-num").text(`${id} / ${$("div.chapt-thumb").length}`);

        $("body div.manga-page div.page-prev")
            .off('click').on('click', zk.get("page-prev-up").func);

        $("body div.manga-page div.page-next")
            .off('click').on('click', zk.get("page-next-down").func);

        image.onload = () => {
            im_elem.attr("src", image.src);

            if (im_elem.width() >= $(document).width()) {
                im_elem.height($(document).height() - 10);
            }

            $('.manga-page')
                .off("wheel", "img")
                .on("wheel", "img", (e) => {
                    this.wheelHandle(e, image);
                });

            if (cookie.get("dfsid")) {
                $(`div.chapt-thumb[data-image='${id}']`).attr("data-readed", 1);

                let all = $("div.chapt-flexbox div.chapt-thumb").length;
                let readed = $("div.chapt-flexbox div.chapt-thumb[data-readed]").length;

                if (all === readed) {
                    $(`div[data-chaptid=${this.current.ch_chash}] span`)
                        .attr("class", "view-readed fa fa-check").empty();
                    return;
                }

                $(`div[data-chaptid=${this.current.ch_chash}] span.viewer_chapts_reading`).text(`${readed} / ${all}`);
            }
        };

        im_elem.draggable({
            stop: function (event, ui) {
                let direct = ui.originalPosition.left > ui.position.left ? 'left' : 'right';
                let elem = $(this);
                let dwidth = $(document).width();

                if (direct && direct === "left" && ui.originalPosition.left > (ui.position.left + (dwidth / 3.5))) {
                    zk.get("page-next-down").func();
                    elem.animate({"left": (-1) * dwidth, opacity: "hide"}, "fast", "linear", function () {
                        elem.css({"left": `${(dwidth)}px`});
                        elem.animate({"left": 0, opacity: "show"}, "fast", "linear");
                    });

                } else if (direct && direct === "right" && ui.originalPosition.left < (ui.position.left - (dwidth / 3.5))) {
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
    }

    wheelHandle(evt, img) {
        let elem = $(evt.target);
        if (evt.originalEvent.deltaY > 0 && elem.height() >= 300) {
            let top = parseInt(elem.css("top"));
            let bottom = parseInt(elem.css("bottom"));

            if (top && top < 0) {
                elem.css("top", `${(top + 10)}px`);
            } else if (bottom && bottom < 0) {
                elem.css("top", `${(top - 10)}px`);
            }

            elem.height(elem.height() - 15);

        } else if (evt.originalEvent.deltaY < 0 && elem.height() <= (img.height * 2)) {
            elem.height(elem.height() + 15);
        }

        if (evt.originalEvent.deltaY !== 0) {
            if ((elem.width() + 100) <= $(document).width()) {

                if (this.animation_timeout_id !== null) {
                    clearTimeout(this.animation_timeout_id);
                }
                this.animation_timeout_id = setTimeout(function () {
                    elem.animate({"left": 0}, "fast", "linear");
                }, 100);

            }
            elem.css({"width": "auto"});
        }
    }

    coversNav() {
        let cover = $("div.cover");
        cover.append(aux.template("tt-covers", {text: `1 / ${this.covers}`}));
        let cover_nav = cover.find("div.cover__nav");

        let switch_cover = ((current) => {
            if (current > 0 && current <= this.covers) {
                let image = new Image();
                image.src = `/m/${this.mhash}/c/${current}`;

                image.onload = (() => {
                    cover.css("background-image", `url(${image.src})`);
                    cover_nav.children('div.cover__text').text(`${current} / ${this.covers}`);
                    cover.data("current", current);
                });
            }
        });

        cover_nav.on("click", "div.cover__prev", () => {
            switch_cover(parseInt(cover.data('current')) - 1);
        });

        cover_nav.on("click", "div.cover__next", () => {
            switch_cover(parseInt(cover.data('current')) + 1);
        });
    }

    run() {
        $("#article").on('click', 'div.chaptlist > div', (e) => {
            zk.bind("chapter-prev-left", "chapter-next-right", "chapter-prev", "chapter-next", "view-escape");
            this.showChapter(e.target.getAttribute("data-chaptid"));
        });

        if (this.covers > 1) {
            this.coversNav();
        }

        /* TODO: Optimize and refactor this!!! */
        /* TODO: This can be moved in to admin section?! */
        $("body > div.nav").on('click', 'span[data-action=update-manga]', () => {
            let jqxhr = $.post("/api", {"action": "update-manga", "mhash": this.mhash});

            jqxhr.done(function (data) {
                Notify.show(data.status === "ok" ? "Успешно" : "Ошибка", data.msg, 4);
            });

            jqxhr.fail(function (data) {
                Notify.show("Ошибка", data.responseJSON.msg, 4);
            });

        }).on('click', 'span[data-action=remove-manga]', () => {
            let body = $("body");
            body.append(aux.template('tt-popup', {
                "title": "Удаление манги!",
                "text": "Манга будет безвозвратно удалена из БД и файловой системы! <b>Продолжить?</b>"
            }));

            let popup = body.find(".popup .popup-centred");
            popup.on('click', "input[data-popup=cancel]", () => {
                body.find(".popup").remove();
                popup.off();

            }).on('click', "input[data-popup=execute]", () => {
                let jqxhr = $.post("/api", {"action": "remove-manga", "mhash": this.mhash});

                jqxhr.done((data) =>{
                    Notify.show(data.status === "ok" ? "Успешно" : "Ошибка", data.msg, 3);
                    if (data.status === "ok") {
                        setTimeout(() => {
                            window.location.href = "/";
                        }, 3000);
                    }
                });

                jqxhr.fail(function (data) {
                    Notify.show("Ошибка", data.responseJSON.msg, 4);
                });

                body.find(".popup").remove();
                popup.off();
            })

        });
    }
}

$(function () {
    let app = new MangaView();
    app.run();
});
