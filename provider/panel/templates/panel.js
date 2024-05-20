
// extract last folder
let baseUrl = window.location.href.split('/').slice(0, -1).join('/');

async function stopNodes() {
    $(`#stop_nodes_btn`).prop('disabled', true)
    $(`#start_nodes_btn`).prop('disabled', true);
    let startClosing = fetch(`${baseUrl}/compose/down`, {
        method: "POST", // *GET, POST, PUT, DELETE, etc.
    });

    for (let node = 0; node < nodes.length; node++) {
        $(`#yagna_status_${node}`).html("stopping...");
    }

    await startClosing;
    $(`#stop_nodes_btn`).prop('disabled', false)
    $(`#start_nodes_btn`).prop('disabled', false);

    await refreshNodes();

}

async function runYagnaCommand(no, command) {
    let runUp = fetch(`${baseUrl}/yagna/${no}/cli`, {
        method: "POST",
        body: command,
    });
    let response = await runUp;
    let resp = await response.text()
    console.log(`response: ${response.status} ${resp}`);
    $('#myModal').modal('toggle');
    $('#command_result').html(resp);
}

async function getProcessList(no) {
    console.log(`getProcessList(${no})`);
    let runUp = fetch(`${baseUrl}/yagna/${no}/proc`, {
        method: "GET"
    });
    let response = await runUp;
    let resp = await response.json()


    let html = "";
    for (let i = 0; i < resp.length; i++) {
        html += `<div>${resp[i]["command"]} (pid: ${resp[i]["pid"]}, cpu: ${resp[i]["cpu"]})`;
        html += `<button onclick="stopProcess(${no}, ${resp[i]["pid"]})">Stop</button>`;
        html += `<button onclick="killProcess(${no}, ${resp[i]["pid"]})">Kill</button>`;
        html += "</div>"
    }
    $(`#proc_list_${no}`).html(html);
    console.log(`response: ${response.status} ${resp}`);
}

async function getEnv(no) {
    console.log(`getEnvList(${no})`);
    let runUp = fetch(`${baseUrl}/yagna/${no}/env`, {
        method: "GET"
    });
    let response = await runUp;
    let resp = await response.json()

    let html = "";
    let subnet_name = "";
    for (let name in resp) {
        let value = resp[name];
        if (name === "SUBNET") {
            subnet_name = value;
        }
        html += `<div>${name}:${value}</div>`;
    }
    $(`#env_list_${no}`).html(html);
    $(`#subnet_name_${no}`).html(subnet_name);

    console.log(`response: ${response.status} ${resp}`);
}

async function startNode(no) {
    console.log(`startNode(${no})`);
    let runUp = fetch(`${baseUrl}/yagna/${no}/start`, {
        method: "POST"
    });
    let response = await runUp;
    let resp = await response.text()
    console.log(`response: ${response.status} ${resp}`);
}

async function stopNode(no) {
    console.log(`startNode(${no})`);
    let runUp = fetch(`${baseUrl}/yagna/${no}/stop`, {
        method: "POST"
    });
    let response = await runUp;
    let resp = await response.text()
    console.log(`response: ${response.status} ${resp}`);
}

async function restartNode(no) {
    console.log(`startNode(${no})`);
    let runUp = fetch(`${baseUrl}/yagna/${no}/restart`, {
        method: "POST"
    });
    let response = await runUp;
    let resp = await response.text()
    console.log(`response: ${response.status} ${resp}`);
}


async function killNode(no) {
    let runUp = fetch(`${baseUrl}/yagna/${no}/kill`, {
        method: "POST"
    });
    let response = await runUp;
    let resp = await response.text()
    console.log(`response: ${response.status} ${resp}`);
}

async function stopProcess(no, pid) {
    let runUp = fetch(`${baseUrl}/yagna/${no}/proc/${pid}/stop`, {
        method: "POST"
    });
    let response = await runUp;
    let resp = await response.text()
    console.log(`response: ${response.status} ${resp}`);
}

async function killProcess(no, pid) {
    let runUp = fetch(`${baseUrl}/yagna/${no}/proc/${pid}/kill`, {
        method: "POST"
    });
    let response = await runUp;
    let resp = await response.text()
    console.log(`response: ${response.status} ${resp}`);
}

async function startNodes() {
    $(`#stop_nodes_btn`).prop('disabled', true)
    $(`#start_nodes_btn`).prop('disabled', true);

    let runUp = fetch(`${baseUrl}/compose/up`, {
        method: "POST", // *GET, POST, PUT, DELETE, etc.
    });

    for (let node = 0; node < nodes.length; node++) {
        $(`#yagna_status_${node}`).html("starting...");
    }

    await runUp;
    $(`#stop_nodes_btn`).prop('disabled', false)
    $(`#start_nodes_btn`).prop('disabled', false);
    await refreshNodes(true);
}

async function loadYagnaStatus(node, showChecking) {
    // call the function to load the data
    if (showChecking) {
        $(`#yagna_status_${node}`).html("checking...");
    }

    const response = await fetch(`${baseUrl}/yagna/${node}/isup`, {
        method: "GET", // *GET, POST, PUT, DELETE, etc.
    });
    let resp = await response.text();

    let res_json = JSON.parse(resp);
    if ('identity' in res_json) {
        $(`#yagna_status_${node}`).css('color', 'green');
        $(`#yagna_status_${node}`).html(res_json['identity']);
    } else {
        $(`#yagna_status_${node}`).css('color', 'red');
        $(`#yagna_status_${node}`).html(res_json['error']);
    }
    console.log(`response: ${response.status} ${response.statusText}`);
}

async function getComposeParams() {
    console.log(`getComposeParams()`);
    let runUp = fetch(`${baseUrl}/compose/params`, {
        method: "GET"
    });
    let response = await runUp;
    let resp = await response.json()

    let imageParams = resp['image'];
    let composeParams = resp['compose'];
    $('#image_yagna_version').val(imageParams['yagnaVersion']);

    // jquery check if enabled
    if ($('#subnet_name').prop('disabled')) {
        $('#subnet_name').val(composeParams['subnet']);
    }
    if ($('#provider_count').prop('disabled')) {
        $('#provider_count').val(composeParams['provCount']);
    }
    if ($('#provider_prefix').prop('disabled')) {
        $('#provider_prefix').val(composeParams['providerPrefix']);
    }

    $(`#main_view`).show();

}

function editParams() {
    $('#subnet_name').prop('disabled', false);
    $('#provider_count').prop('disabled', false);
    $('#provider_prefix').prop('disabled', false);
    $('#image_yagna_version').prop('disabled', false);
    $('#btn_edit_params').hide();
    $('#btn_save_params').show();
    $('#btn_cancel_params').show();
    $('#btn_reset_params').hide();
}

async function resetParams() {
    if (confirm("Are you sure you want to reset the parameters?")) {
        let runup = fetch(`${baseUrl}/compose/params/reset`, {
            method: "POST"
        });
        await runup;
        await refreshNodes();
    }

}

function cancelParams() {
    $('#subnet_name').prop('disabled', true);
    $('#provider_count').prop('disabled', true);
    $('#provider_prefix').prop('disabled', true);
    $('#image_yagna_version').prop('disabled', true);
    $('#btn_edit_params').show();
    $('#btn_save_params').hide();
    $('#btn_cancel_params').hide();
    $('#btn_reset_params').show();
    getComposeParams();
}

async function saveParams() {
    $('#subnet_name').prop('disabled', true);
    $('#provider_count').prop('disabled', true);
    $('#provider_prefix').prop('disabled', true);
    $('#image_yagna_version').prop('disabled', true);
    $('#btn_edit_params').show();
    $('#btn_save_params').hide();
    $('#btn_cancel_params').hide();
    $('#btn_reset_params').show();

    let subnet_name = $('#subnet_name').val();
    let provider_count = $('#provider_count').val();
    let provider_prefix = $('#provider_prefix').val();
    let yagna_version = $('#image_yagna_version').val();

    let runUp = fetch(`${baseUrl}/compose/params`, {
        method: "POST",
        body: JSON.stringify({
            "compose": {
                subnet: subnet_name,
                provCount: provider_count,
                providerPrefix: provider_prefix,
            },
            "image": {
                yagnaVersion: yagna_version
            }
        }),
    });

    await runUp;

    {
        let runUp = fetch(`${baseUrl}/compose/regenerate`, {
            method: "POST"
        });

        await runUp;
    }
}

async function refreshNodes(showChecking) {
    let futures = [];
    for (let i = 0; i < nodes.length; i++) {
        futures.push(loadYagnaStatus(nodes[i], showChecking));
        futures.push(getProcessList(nodes[i]))
        futures.push(getEnv(nodes[i]))
    }
    futures.push(getComposeParams());
    await Promise.all(futures);

}

document.addEventListener('DOMContentLoaded', async function () {
    console.log('DOM fully loaded and parsed');
    await refreshNodes(true);

    while (true) {
        try {
            await refreshNodes(false);
        } catch (e) {
            console.error(e);
        }
        await new Promise(r => setTimeout(r, 4000));
    }
});
