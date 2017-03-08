/**
 * Created by zatevaxin on 19.02.17.
 */

function AAProcesses() {
    this.processList = {};
    this.ws = new WebSocket("ws://{0}/wsapi".format(window.location.host));
}

AAProcesses.prototype.run = function () {
    let self = this;

    self.ws.onopen = ((evt) => {
        self.ws_onopen(self, evt);
    });

    self.ws.onclose = ((evt) => {
        self.ws_onclose(self, evt)
    });

    self.ws.onerror = ((err) => {
        self.ws_onerror(self, err)
    });

    self.ws.onmessage = ((evt) => {
        self.ws_onmessage(self, evt)
    });


    setInterval(self.processListUpdate, 2000, self);


};

AAProcesses.prototype.processListUpdate = function (self) {
    self.ws.send(JSON.stringify({"action": "process-list"}));
    self.redrawProcessList()
};

AAProcesses.prototype.redrawProcessList = function () {
    let self = this;

    let plist = [];

    let ps_replace = {
        "complete": "Задача выполнена",
        "runing": "Работает",
        "fail": "Исключение",
        "wait": "Ожидает",
    };

    let task_replace = {
        "download": "Загрузка"
    };

    for (let pid in self.processList) {
        if (!self.processList.hasOwnProperty(pid)) {
            continue;
        }
        let proc = self.processList[pid];

        let ps = ps_replace[proc.status] || proc.status;
        ps = proc.error ? "{1}: {0}".format(proc.error, ps) : ps;

        let ts = task_replace[proc.task] || proc.task;

        plist.push(`
      <tr class="process" data-pid="${pid}" data-status="${proc.status}">
        <td>
          <span class="work-name">${proc.name}</span>
          <progress max="${proc.all}" value="${proc.current}"></progress>
          <span class="pid">${pid}</span>
        </td>
        <td>
          <div class="status">${ps}</div>
          <span class="mission">${ts}</span>
        </td>
      </tr>
    `)
    }

    $("table.process-list").html(plist);

};

AAProcesses.prototype.ws_onopen = function (self, evt) {
    console.debug("ws_onopen", this);
};

AAProcesses.prototype.ws_onclose = function (self, evt) {
    console.debug("ws_onclose", this, evt);
};

AAProcesses.prototype.ws_onmessage = function (self, evt) {
    console.debug("ws_onmessage");

    if (!JSON.isjson(evt.data)) {
        console.debug(evt.data);
        return;
    }

    let jobj = JSON.parse(evt.data);
    console.table(jobj["data"]);
    self.processList = {};

    if (jobj.type == "plist") {
        for (let proc in jobj.data) {
            if (!jobj.data.hasOwnProperty(proc)) {
                continue;
            }

            self.processList[proc] = jobj.data[proc];
        }

    }


};

AAProcesses.prototype.ws_onerror = function (self, err) {
    console.debug("ws_onerror", this, err);
};


$(() => {
    let app = new AAProcesses();
    app.run();
});
