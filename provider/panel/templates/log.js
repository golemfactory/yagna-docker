class LogEntry {
    constructor() {
        this.id = null;
        this.type = null;
        this.message = null;
        this.timestamp = null;
    }
}

/**
 * Parse a line from a log file.
 * @param {string} line
 * @returns { {date: Date, logLevel: string, module: string, content: string}|boolean}
 */
function parseLine(line) {
    if (!line) {
        return false;
    }
    let start_date_idx = 1;
    if (line[0] != "[") {
        return false;
    }
    let end_date_idx = line.indexOf(" ");
    if (end_date_idx == -1) {
        return false;
    }
    let timestamp = Date.parse(line.substring(start_date_idx, end_date_idx));
    if (isNaN(timestamp)) {
        return false;
    }
    let date = new Date(timestamp);
    let endInfo = line.indexOf(" ", end_date_idx + 1);
    if (endInfo == -1) {
        return false;
    }
    let logLevel = line.substring(end_date_idx + 1, endInfo);
    let endModule = line.indexOf("]", endInfo + 1);
    if (endModule == -1) {
        return false;
    }
    let module = line.substring(endInfo + 1, endModule);

    return {
        date: date,
        logLevel: logLevel,
        module: module,
        content: line.substring(endModule + 2)
    };
}

function testParseLine() {
    let line = "[2021-06-15T17:10:00.000 IN";
    let parsedLine = parseLine(line);
    console.log(parsedLine);
}

function doSplit(logText) {
    let resp_split = logText.split("\n");
    let new_split = []
    for (let i = 0; i < resp_split.length; i++) {
        let line = resp_split[i];
        let parsedLine = parseLine(line);
        if (parsedLine !== false) {
            new_split.push(parsedLine);
        } else {
            if (new_split.length >= 1) {
                new_split[new_split.length - 1].content += "\n" + line;
            }
        }
    }
    let max_len = 100;
    for (let i = 0; i < new_split.length; i++) {
        if (new_split[i].content.length > max_len) {
            new_split[i].shortContent = new_split[i].content.substring(0, max_len) + "...";
        } else {
            new_split[i].shortContent = new_split[i].content;
        }
    }
    let timeStart = new_split[0].date;
    let modules = {};
    for (let i = 0; i < new_split.length; i++) {
        if (i == 0) {
            new_split[i].fromStart = 0.0;
            new_split[i].fromPrev = 0.0;
        } else {
            new_split[i].fromStart = new_split[i].date - timeStart;
            new_split[i].fromPrev = new_split[i].date - new_split[i - 1].date;
        }
        new_split[i].marginTop = Math.round(Math.sqrt(Math.min(Math.max(1, new_split[i].fromPrev), 1000)));
        if (new_split[i].logLevel == "ERROR") {
            new_split[i].logLevelInt = 5;
        }
        else if (new_split[i].logLevel == "WARN") {
            new_split[i].logLevelInt = 4;
        }
        else if (new_split[i].logLevel == "INFO") {
            new_split[i].logLevelInt = 3;
        }
        else if (new_split[i].logLevel == "DEBUG") {
            new_split[i].logLevelInt = 2;
        }
        else if (new_split[i].logLevel == "TRACE") {
            new_split[i].logLevelInt = 1;
        }
        else {
            new_split[i].logLevelInt = 0;
        }

        if (new_split[i].module in modules) {
            modules[new_split[i].module].count += 1;
            modules[new_split[i].module].maxLevel = Math.max(modules[new_split[i].module].maxLevel, new_split[i].logLevelInt);
            modules[new_split[i].module].lastOcc = new_split[i].fromStart;
        } else {
            modules[new_split[i].module] = {};
            modules[new_split[i].module].count = 1;
            modules[new_split[i].module].firstOcc = new_split[i].fromStart;
            modules[new_split[i].module].lastOcc = new_split[i].fromStart;
            modules[new_split[i].module].maxLevel = new_split[i].logLevelInt;
        }
    }
    for (let i in modules) {
        let logLevelStr = "";
        if (modules[i].maxLevel == 5) {
            logLevelStr = "ERROR";
        }
        else if (modules[i].maxLevel == 4) {
            logLevelStr = "WARN";
        }
        else if (modules[i].maxLevel == 3) {
            logLevelStr = "INFO";
        }
        else if (modules[i].maxLevel == 2) {
            logLevelStr = "DEBUG";
        }
        else if (modules[i].maxLevel == 1) {
            logLevelStr = "TRACE";
        }
        else {
            logLevelStr = "UNKNOWN";
        }
        modules[i].logLevelStr = logLevelStr;
    }

    return [new_split, modules];
}

class LogFile {
    constructor(logText) {
        let [new_split, modules] = doSplit(logText);
        this.logEntries = new_split;
        this.modules = modules;
    }

    renderModules() {
        let modulesList = `<table class="table table-striped">`;
        modulesList += `<tr class="module-entry">`;
        modulesList += `<th>Module</th>`;
        modulesList += `<th>Count</th>`;
        modulesList += `<th>First</th>`;
        modulesList += `<th>Last</th>`;
        modulesList += `<th>Max level</th>`;
        modulesList += '</tr>';
        for (let module in this.modules) {
            let obj = this.modules[module];
            modulesList += `<tr class="module-entry ${obj.logLevelStr}" >`;

            modulesList += `<td>${module}</td>`;
            modulesList += `<td>${obj.count}</td>`;
            modulesList += `<td>${obj.firstOcc / 1000}</td>`;
            modulesList += `<td>${obj.lastOcc / 1000}</td>`;
            modulesList += `<td>${obj.logLevelStr}</td>`;
            modulesList += '</tr>';
        }
        modulesList += "</table>";
        return modulesList;
    }

    renderLogEntries() {
        let html_split = "<div>";
        for (let i = 0; i < this.logEntries.length; i++) {
            let obj = this.logEntries[i];
            let content = obj.shortContent.replaceAll("\n", " ");
            html_split += `<div class="entry ${obj.logLevel}" style="margin-top: ${obj.marginTop}px">`;
            //html_split += `<div class="module">${obj.date.toISOString()}</div>`;
            html_split += `<div class="entry-time">${obj.fromStart / 1000}s</div>`;
            html_split += `<div class="module">${obj.module}</div>`;
            html_split += `<div class="content">${content}</div>`;
            html_split += '</div>';
        }
        html_split += "</div>";
        return html_split;
    }
}