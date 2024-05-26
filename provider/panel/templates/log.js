class LogEntry {
    constructor() {
        this.date = new Date();
        this.logLevelInt = 0;
        this.logLevel = "";
        this.module = "";
        this.content = "";
        this.shortContent = "";
        this.fileNo = 0;
        this.fileDisplayName = "";
    }
}


class AcceptLogFilter {
    constructor() {
        this.acceptedLogLevels = [];
        this.acceptedModules = [];
        this.contentSearchFields = [];
    }
}

class DenyLogFilter {
    constructor() {
        this.deniedModules = [];
        this.deniedLogLevels = [];
        this.deniedSearchFields = [];
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
        logLevel: logLevel.trim(),
        module: module.trim(),
        content: line.substring(endModule + 2).trim()
    };
}

/**
 * Convert log level string to integer.
 * @param {string} logLevel
 * @returns {number}
 */
function logLevelToInt(logLevel) {
    if (logLevel == "ERROR") return 5;
    if (logLevel == "WARN") return 4;
    if (logLevel == "INFO") return 3;
    if (logLevel == "DEBUG") return 2;
    if (logLevel == "TRACE") return 1;
    return 0;
}

/**
 * Convert log level integer to string.
 * @param {number} logLevelInt
 * @returns {string}
 */
function intToLogLevel(logLevelInt) {
    if (logLevelInt == 5) return "ERROR";
    if (logLevelInt == 4) return "WARN";
    if (logLevelInt == 3) return "INFO";
    if (logLevelInt == 2) return "DEBUG";
    if (logLevelInt == 1) return "TRACE";
    return "UNKNOWN";
}

function doSplit(logText) {
    let resp_split = logText.split("\n");
    /**
     * @type {LogEntry[]}
     */
    let spl = [];
    for (let i = 0; i < resp_split.length; i++) {
        let line = resp_split[i];
        let parsedLine = parseLine(line);
        if (parsedLine !== false) {
            let logEntry = new LogEntry();
            logEntry.date = parsedLine.date;
            logEntry.logLevel = parsedLine.logLevel;
            logEntry.module = parsedLine.module;
            logEntry.content = parsedLine.content;
            spl.push(logEntry)
        } else {
            if (spl.length >= 1) {
                spl[spl.length - 1].content += "\n" + line;
            }
        }
    }
    let max_len = 1000;
    for (let i = 0; i < spl.length; i++) {
        if (spl[i].content.length > max_len) {
            spl[i].shortContent = spl[i].content.substring(0, max_len) + "...";
        } else {
            spl[i].shortContent = spl[i].content;
        }
    }
    let timeStart = spl[0].date;
    let modules = {};
    for (let i = 0; i < spl.length; i++) {
        spl[i].logLevelInt = logLevelToInt(spl[i].logLevel);

        if (spl[i].module in modules) {
            modules[spl[i].module].count += 1;
            modules[spl[i].module].maxLevel = Math.max(modules[spl[i].module].maxLevel, spl[i].logLevelInt);
            modules[spl[i].module].lastOcc = spl[i].date;
        } else {
            modules[spl[i].module] = {};
            modules[spl[i].module].count = 1;
            modules[spl[i].module].firstOcc = spl[i].date;
            modules[spl[i].module].lastOcc = spl[i].date;
            modules[spl[i].module].maxLevel = spl[i].logLevelInt;
        }
    }
    for (let module in modules) {
        modules[module].logLevelStr = intToLogLevel(modules[module].maxLevel);
    }

    return [spl, modules];
}

class LogStorage {
    constructor() {
        // @type {LogFile[]}
        this.logFiles = [];
        // @type {AcceptLogFilter}
        this.displayFilter = null;
        // @type {DenyLogFilter}
        this.displayDenyFilter = null;
    }

    /**
     * @param {AcceptLogFilter} filter
     */
    setDisplayFilter(filter) {
        this.displayFilter = filter;
    }

    /**
     * @param {DenyLogFilter} filter
     */
    setDisplayDenyFilter(filter) {
        this.displayDenyFilter = filter;
    }

    addLogFile(logFile) {
        this.logFiles.push(logFile);
    }

    exportDisplayedToLog() {
        this.mergeEntries();
        let exported = "";
        for (let i = 0; i < this.mergedEntries.length; i++) {
            let obj = this.mergedEntries[i];
            if (this.displayFilter && !this.checkFilter(obj, this.displayFilter)) {
                continue;
            }
            if (this.displayDenyFilter && !this.checkNegativeFilter(obj, this.displayDenyFilter)) {
                continue;
            }
            exported += `[${obj.date.toISOString()} ${obj.logLevel} ${obj.module}] ${obj.content}\n`;
        }
        return exported;
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

        for (let logFileNo = 0; logFileNo < this.logFiles.length; logFileNo++) {
            let logFile = this.logFiles[logFileNo];
            for (let module in logFile.modules) {
                let obj = logFile.modules[module];
                modulesList += `<tr class="module-entry ${obj.logLevelStr}" >`;

                modulesList += `<td>${module}</td>`;
                modulesList += `<td>${obj.count}</td>`;
                modulesList += `<td>${obj.firstOcc / 1000}</td>`;
                modulesList += `<td>${obj.lastOcc / 1000}</td>`;
                modulesList += `<td>${obj.logLevelStr}</td>`;
                modulesList += '</tr>';
            }
        }
        modulesList += "</table>";
        return modulesList;
    }

    /**
     * @param {LogEntry} logEntry
     * @param {AcceptLogFilter} filter
     * @returns {boolean}
     */
    checkFilter(logEntry, filter) {
        if (filter.acceptedLogLevels.length > 0) {
            if (!filter.acceptedLogLevels.includes(logEntry.logLevel)) {
                return false;
            }
        }
        if (filter.acceptedModules.length > 0) {
            if (!filter.acceptedModules.includes(logEntry.module)) {
                return false;
            }
        }
        if (filter.contentSearchFields.length > 0) {
            for (let field of filter.contentSearchFields) {
                if (logEntry.content.toLowerCase().includes(field.toLowerCase())) {
                    return true;
                }
            }
            return false;
        }
        return true;
    }

    /**
     * @param {LogEntry} logEntry
     * @param {DenyLogFilter} filter
     */
    checkNegativeFilter(logEntry, filter) {
        if (filter.deniedModules.length > 0) {
            if (filter.deniedModules.includes(logEntry.module)) {
                return false;
            }
        }
        if (filter.deniedLogLevels.length > 0) {
            if (filter.deniedLogLevels.includes(logEntry.logLevel)) {
                return false;
            }
        }
        if (filter.deniedSearchFields.length > 0) {
            for (let deniedField of filter.deniedSearchFields) {
                if (logEntry.content.toLowerCase().includes(deniedField.toLowerCase())) {
                    return false;
                }
            }
        }
        return true;
    }

    mergeEntries() {
        //prepare indexes
        let logFileIdx = [];
        for (let logFileNo = 0; logFileNo < this.logFiles.length; logFileNo++) {
            logFileIdx.push(0);
        }
        let logFileIdxMax = [];
        for (let logFileNo = 0; logFileNo < this.logFiles.length; logFileNo++) {
            logFileIdxMax.push(this.logFiles[logFileNo].logEntries.length);
        }

        let mergedEntries = [];
        // TODO - this algorithm is not optimal - it should be done with priority queue to achieve O(n log n) complexity
        // TODO - for small number of log files it is not a problem
        while (true) {
            // find next entry

            let lowestNextDate = null;
            let nextEntryFileIdx = null;
            for (let logFileNo = 0; logFileNo < this.logFiles.length; logFileNo++) {
                let idx = logFileIdx[logFileNo];
                if (idx < logFileIdxMax[logFileNo]) {
                    let entry = this.logFiles[logFileNo].logEntries[idx];
                    if (lowestNextDate == null || entry.date < lowestNextDate) {
                        nextEntryFileIdx = logFileNo;
                        lowestNextDate = entry.date;
                    }
                }
            }
            if (nextEntryFileIdx == null) {
                break;
            }
            let mergedEntry = this.logFiles[nextEntryFileIdx].logEntries[logFileIdx[nextEntryFileIdx]];
            mergedEntry.fileNo = nextEntryFileIdx;
            mergedEntry.fileDisplayName = this.logFiles[nextEntryFileIdx].displayName;
            mergedEntries.push(mergedEntry);
            logFileIdx[nextEntryFileIdx] += 1;
        }
        this.mergedEntries = mergedEntries;
    }

    renderLogEntries() {
        this.mergeEntries();
        let mergedEntries = this.mergedEntries;

            let html_split = "<div>";

        for (let i = 0; i < mergedEntries.length; i++) {
            let obj = mergedEntries[i];
            let marginTop = 0;
            if (i > 0) {
                marginTop = Math.round(Math.sqrt(Math.min(Math.max(1, obj.date - mergedEntries[i - 1].date), 1000)));
            }
            if (this.displayFilter && !this.checkFilter(obj, this.displayFilter)) {
                continue;
            }
            if (this.displayDenyFilter && !this.checkNegativeFilter(obj, this.displayDenyFilter)) {
                continue;
            }
            let content = obj.shortContent.replaceAll("\n", " ");
            html_split += `<div id="entry-${obj.fileNo}-${i}" class="entry entry-${obj.fileNo} ${obj.logLevel}" style="margin-top: ${marginTop}px">`;
            //html_split += `<div class="module">${obj.date.toISOString()}</div>`;
            html_split += `<div class="entry-time">${(obj.date - mergedEntries[0].date) / 1000}s</div>`;
            html_split += `<div class="entry-file">${obj.fileDisplayName}</div>`;
            html_split += `<div class="module">${obj.module}</div>`;
            html_split += `<div class="content">${content}</div>`;
            html_split += '</div>';
        }
        html_split += "</div>";
        return html_split;
    }

}

class LogFile {
    /**
     * @param {string} logText
     * @param {string} displayName
     */

    constructor(logText, displayName) {
        let [spl, modules] = doSplit(logText);
        this.logEntries = spl;
        this.modules = modules;
        this.displayName = displayName;
    }
}