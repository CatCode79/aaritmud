//=- GESTIONE DELLA RICEZIONE DELL'OUTPUT

var END_TAG = "<e>";  // (TD) ${END_TAG}

function connectToGame(player_code) {
	var use_comet = document.getElementById("use_comet");
	if (use_comet) {
		connetWithComet();
	} else {
		var output_iframe = document.getElementById("output_iframe");
		if (output_iframe) {
			connectoToIFrame(output_iframe);
		} else {
			connectWithAjax("?first=1");
		}
	}
}


//=- GESTIONE DELLA RICEZIONE DELL'OUTPUT TRAMITE COMET EMULATO

function connetWithComet() {
	var length = 0;
	var ajax_request = createAjaxRequest();
	ajax_request.onreadystatechange = function () {
		if (ajax_request.readyState >= 3 && typeof(ajax_request.responseText) != "unknown" && ajax_request.responseText) {
			var last_msg_pos = ajax_request.responseText.lastIndexOf(END_TAG)
			if (last_msg_pos != -1 && length != last_msg_pos + END_TAG.length) {
				var response = ajax_request.responseText.slice(length, last_msg_pos + END_TAG.length).replace(/<e>/g, "");
				if (response) {
					refreshOutput(response);
					length = last_msg_pos + END_TAG.length;
				}
			}
			if (ajax_request.readyState == 4) {
				refreshOutput("<br><br><span style='color:cyan; font-size:smaller;'>È stata persa la connessione al gioco, per riconnetterti <input type='submit' value='clicca qui' onclick='location.reload();'/></span><br><br>");
				ajax_request = null;
				length = null;
			}
		}
		return;
	}
	ajax_request.open("GET", "game_connection_comet.html", true);
	ajax_request.send(null);
}

function redirectToPlayers() {
	window.location.href = "players.html";
}

function refreshOutput(response) {
	var output_div = document.getElementById("output");
	$(output_div).append(response);
	doScroll(output_div);
}


//=- GESTIONE DELLA RICEZIONE DELL'OUTPUT TRAMITE IFRAME (IE COMBATIBILE)

function connectoToIFrame(output_iframe) {
	output_iframe.src = "game_connection_iframe.html";
	redirectOutput();
}

function redirectOutput() {
	var output_iframe = document.getElementById("output_iframe");
	if (output_iframe) {
		var iframe_document = output_iframe.contentDocument || output_iframe.contentWindow.document;
		if (iframe_document && iframe_document.body && iframe_document.body.innerHTML) {
			var output_div = document.getElementById("output");
			if (document.documentMode) {  // IE 8
				for (element=iframe_document.body.firstChild; element; element=element.nextSibling) {
					$(output_div).append(element.cloneNode(true));
				}
			} else {
				output_div.append(iframe_document.body.innerHTML);
			}
			// Incredibile ma... sotto internet explorer 7 non va se non
			// inserisco le istruzioni in un'altra funzione
			cleanIframeAndScroll(iframe_document, output_div);
		}
	}
	setTimeout("redirectOutput();", 50);
}

function cleanIframeAndScroll(iframe_document, output_div)
{
	iframe_document.body.innerHTML = "";
	$(iframe_document.body).text("");
	doScroll(output_div);
}


//=- GESTIONE DELLA RICEZIONE DELL'OUTPUT TRAMITE AJAX

var start_connection = null;
var average_time = 100;

function connectWithAjax(query) {
	var ajax_request = createAjaxRequest();
	ajax_request.onreadystatechange = function () {
		if (ajax_request.readyState == 4 && ajax_request.status == 200) {
			afterConnectWithAjax(ajax_request.responseText);
		}
	}
	ajax_request.open("GET", "game_connection_ajax.html" + query, true);
	ajax_request.send(null);
	start_connection = new Date();
}

function afterConnectWithAjax(response) {
	if (response) {
		if (response.indexOf("<title>AARIT: Personaggi</title>") != -1) {
			redirectToPlayers();
		} else if (response.startsWith("<?xml")) {
			refreshOutput("<br><br><span style='color:cyan; font-size:smaller;'>È stata persa la connessione al gioco, per riconnetterti <input type='submit' value='clicca qui' onclick='location.reload();'/></span><br><br>");
			return;
		}
		var output_div = document.getElementById("output");
		$(output_div).append(response);
		doScroll(output_div);
	}
	// Esegue la connessione ogni tot di tempo pari alla media del tempo che
	// ci mette a connettersi, in questa maniera per connessioni veloci
	// aggiorna più velocemente, con alcuni limiti fissi
	var end_connection = new Date();
	average_time = (end_connection.getTime() - start_connection.getTime() + average_time) / 2;
	if (average_time < 300)
		milliseconds = 300
	else if (average_time > 1000)
		milliseconds = 1000
	else
		milliseconds = average_time
	// Viene creato un numero random per evitare il controllo dello script
	// ciclico e per evitare eventuale caching della richiesta in IE
	try {
		setTimeout("connectWithAjax('?rnd=" + Math.random() + "');", milliseconds);
	}
	catch (e) {
		window.location.reload();
	}
}


//=- GESTIONE DELLO SCROLL

var scroll_is_active = true;

function toggleScroll() {
	var scroll_button = document.getElementById("scroll");
	if (scroll_is_active) {
		scroll_button.value = "Riattiva Scroll";
	} else {
		scroll_button.value = "Disattiva Scroll";
	}
	scroll_is_active = !scroll_is_active;
}

function reactivateScroll() {
	var scroll_button = document.getElementById("scroll");
	scroll_button.value = "Disattiva Scroll";
	scroll_is_active = true;
}

function doScroll(output_div) {
	if (scroll_is_active) {
		output_div.scrollTop = output_div.scrollHeight * 10;
	}
}


//=- GESTIONE DELL'INVIO DELL'INPUT

function putInput(input) {
	var input_content = document.getElementById("input_content");
	input_content.value = input || "";
	if (input_content.value.endsWith(" ")) {
		input_content.focus();
	} else {
		input_content.select();
	}
}

// input_to_send è un parametro opzionale e serve il più delle volte ad inviare input tramite click di un link
function sendInput(input_to_send) {
	var input_content = document.getElementById("input_content");
	if (input_to_send) {
		input_content.value = input_to_send;
	}
	input_content.value = trim(input_content.value);
	try {
		sendPostRequest("game_connection_ajax.html", "input_content=" + encodeURIComponent(input_content.value), null, "500_check");
	} catch (e) {
		alert("errore da riportare per favore agli amministratori del gioco: " + e);
	}
	saveInputOnHistory(input_content.value);
	var show_last_input = document.getElementById("show_last_input");
	if (show_last_input) {
		input_content.select();
	} else {
		input_content.value = "";
	}
	reactivateScroll();
}


//=- GESTIONE DELLO STORICO DEI COMANDI

var history_position = -1;
var history_inputs = [];

function getFromHistory(event, input_content) {
	event = event || window.event
	// (BB) sotto firefox non funziona più per chissà quale ragione, quindi bellamente esco
	if (!event) {
		return;
	}
	var key_code = event.keyCode || event.which;
	var refresh_history = false
	if (key_code == 38) {
		// up key
		if (history_position > 0) {
			if (input_content.value == history_inputs[history_position]) {
				history_position -= 1;
			}
		} else {
			history_position = 0;
		}
		refresh_history = true;
	} else if (key_code == 40) {
		// down key
		if (history_position < history_inputs.length-1) {
			if (input_content.value == history_inputs[history_position]) {
				history_position += 1;
			}
		} else {
			history_position = history_inputs.length-1;
		}
		if (history_inputs[history_position]) {
			input_content.value = history_inputs[history_position];
		}
		refresh_history = true
	}
	if (refresh_history) {
		if (history_inputs[history_position]) {
			input_content.value = history_inputs[history_position];
		}
	}
}

function saveInputOnHistory(input_to_save) {
	if (input_to_save && history_inputs.slice(-1) != input_to_save) {
		history_inputs.push(input_to_save);
		history_position = history_inputs.length - 1;
	}
}


//=- GESTIONE DELLE MACRO-TASTI

var capslock_key_pressed = false;

function checkMacro(event) {
	// Evita di controllare i tasti schiacciati assieme a quelli speciali
	if (key_code == 20) {
		if (capslock_key_pressed) {
			capslock_key_pressed = false;
		} else {
			capslock_key_pressed = true;
		}
	}
	if (event.ctrlKey || key_code == 17 || event.altKey || key_code == 18) {
		return true;
	}

	var key_code = event.keyCode || event.which;
	if (key_code == 13 || (key_code >= 65 && key_code <= 90)) {
		var input_content = document.getElementById("input_content");
		input_content.focus();
	} else {
		var pg_language = $("#pg_language").text();
	}

	// L'ESC (codice 27) è gestito dall' OS, ed è impossibile da disabilitare
	// quindi se il giocatore lo schiaccia la connessione del gioco viene chiusa
	var input_to_send = ""
	switch (key_code) {
	case 110:
		input_to_send = (pg_language == "it") ? "basso" : "down";
		break;
	case 106:
		input_to_send = (pg_language == "it") ? "alto" : "up";
		break;
	case 12:
	case 101:
		input_to_send = (pg_language == "it") ? "guarda" : "look";
		break;
	case 105:
		input_to_send = (pg_language == "it") ? "nordest" : "northeast";
		break;
	case 99:
		input_to_send = (pg_language == "it") ? "sudest" : "southeast";
		break;
	case 97:
		input_to_send = (pg_language == "it") ? "sudovest" : "southwest";
		break;
	case 103:
		input_to_send = (pg_language == "it") ? "nordovest" : "northwest";
		break;
	case 100:
		input_to_send = (pg_language == "it") ? "ovest" : "west";
		break;
	case 104:
		input_to_send = (pg_language == "it") ? "nord" : "north";
		break;
	case 102:
		input_to_send = (pg_language == "it") ? "est" : "east";
		break;
	case 98:
		input_to_send = (pg_language == "it") ? "sud" : "south";
		break;
	// Purtroppo riconosce il + e il - del tastierino numerico come lo stesso
	// tasto di quelli sulla tastiera e quindi l'up e il down è meglio non inserirli
	// http://unixpapa.com/js/key.html
	//case 107:
	//    input_to_send = (pg_language == "it") ? "basso" : "down";
	//    break;
	//case 109:
	//    input_to_send = (pg_language == "it") ? "alto" : "up";
	//    break;
	case 13:
		input_to_send = input_content.value;
		break
	default:
		return true;
		break;
	}

	sendInput(input_to_send);
	return false;
}


//=- GESTIONE DELLE TAB

function sendChannelMessage(message, name, personal) {
	var date = new Date();
	var date_str = ("0" + date.getHours()).substr(-2, 2) + ":" + ("0" + date.getMinutes()).substr(-2, 2) + ":" + ("0" + date.getSeconds()).substr(-2, 2);
	$("#channels").append("(" + name + " alle " + date_str + ") " + message + "<br>");

	if (!personal) {
		var title = $("#channels_title").text();
		var pos = title.indexOf("(");
		if (pos == -1) {
			$("#channels_title").text(title + " (1)");
		} else {
			var qty = parseInt(title.slice(pos+1, title.length-1));
			$("#channels_title").text(title.slice(0, pos) + " (" + (qty+1) + ")");
		}
	}
}