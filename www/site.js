//=- AJAX

function createAjaxRequest() {
	if (window.XMLHttpRequest) {
		return new XMLHttpRequest();
	}
	try { return new ActiveXObject('MSXML3.XMLHTTP'); } catch(e) {}
	try { return new ActiveXObject('MSXML2.XMLHTTP.3.0'); } catch(e) {}
	try { return new ActiveXObject('Msxml2.XMLHTTP'); } catch(e) {}
	return new ActiveXObject("Microsoft.XMLHTTP");
}

function sendPostRequest(url, query, callback_function) {
	sendAjaxRequestHandler("POST", url, query, callback_function)
}

function sendGetRequest(url, query, callback_function) {
	sendAjaxRequestHandler("GET", url, query, callback_function)
}

function sendAjaxRequestHandler(type, url, query, callback_function) {
	var args = [""];
	for (var j=3; j<arguments.length; j+=1) {
		args.push(arguments[j]);
	}

	var ajax_request = createAjaxRequest();
	ajax_request.onreadystatechange = function () {
		if (ajax_request.readyState == 4 && ajax_request.status == 200) {
			args[0] = ajax_request.responseText;
			if (callback_function) {
				callback_function.apply(this, args);
			}
			ajax_request = null;
			args = null;
		} else if (args[1] == "500_check" && ajax_request.readyState == 4 && ajax_request.status == 500) {
			// Un po' hardcoded, ma per ora va bene così
			refreshOutput(" <span style='color:cyan; font-size:smaller;'>È stato riscontrato un errore sul server; gli amministratori sono stati automaticamente avvisati del problema e cercheremo di correggerlo il prima possibile,  grazie per la pazienza.</span><br><br>");
			callback_function.apply(this, args);
		}
	}
	ajax_request.open(type, url, true);
	ajax_request.setRequestHeader("Content-Encoding", "utf-8");
	ajax_request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
	ajax_request.send(query);
}


//=- REFRESH DINAMICO DEL SITO

var refresh_timeout = null;
var already_refresh = false;

function startRefreshInfos() {
	if (already_refresh) {
		return;
	}

	already_refresh = true;
	var who_counter = document.getElementById("who_counter");
	var last_refresh_id = document.getElementById("last_refresh_id");
	if (!who_counter && !last_refresh_id) {
		already_refresh = false;
		return;
	}

	query = "";
	if (who_counter) {
		query += "refresh_who_counter=1&"
	}
	if (last_refresh_id) {
		query += "last_refresh_id=" + $(last_refresh_id).text();
	}

	sendPostRequest("refresh_infos.html", query, afterRefreshInfos);
}

function afterRefreshInfos(response) {
	if (!response) {
		already_refresh = false;
		return;
	}

	try {
		var infos = eval("(" + response + ")");
	} catch (e) {
		//alert("Errore nel resfresh delle info: " + e.message)
		already_refresh = false;
		return;
	}

	var who_counter = document.getElementById("who_counter");
	if (who_counter) {
		if (infos && infos["who_counter"] != 0) {
			$(who_counter).text(" (" + infos["who_counter"] + ")");
		} else {
			$(who_counter).text("");
		}
	}

	// Refreshare il contenuto della pagina se ve n'è bisogno
/*	if (window.location.pathname == "/who.html") {
		
	}*/

	if (infos && infos["last_square_message"]) {
		addSquareMessage(infos["last_square_message"]);
	}

	already_refresh = false;
	refresh_timeout = setTimeout(function () { startRefreshInfos(); }, 2000);
}

function stopRefreshInfos() {
	already_refresh = false;
	clearTimeout(refresh_timeout);
	refresh_timeout = null;
}


var current_interval = null;
function refreshSecondsToShut() {
	var span_elements = document.getElementsByName("seconds_to_shutdown");
    for (i = 0; i < span_elements.length; i+= 1) {
        var span_element = span_elements[i];
		var seconds = $(span_element).text();
		if (seconds == 0) {
			clearInterval(current_interval);
			var message_span = document.getElementById("message_of_shutdown");
			if (message_span) {
				$(message_span).text("Shutdown del Mud eseguito... ORA!");
			} else {
                window.location.reload();
            }
		} else {
			$(span_element).text(seconds - 1);
		}
    }
}

//=- FAST LOGIN

function fastLogin() {
	$.post("login.html", {name:$("#name").val(), password:$("#password").val(), fast:1}, function(response) {
		if (response) {
			alert(response);
		} else {
			location.href = "players.html";
		}
	});
}

//=- HTML-DOM GENERICA

function changeSelectColor(select_element) {
	if (select_element.selectedIndex != -1) {
		var option_element = select_element.options[select_element.selectedIndex];
		select_element.style.backgroundColor = option_element.style.backgroundColor;
		select_element.style.color = option_element.style.color;
	}
}

// (TD) da cercare di riutilizzare al posto del doppio invio di testo
function alertTooltip(tooltip_id) {
	var tooltip_element = document.getElementById(tooltip_id);
	text = "";
	for (i in tooltip_element.childNodes) {
		node = tooltip_element.childNodes[i];
		if (node.nodeType == 3) {
			text += $(node).text();
		} else if (node.nodeType == 1) {
			if (node.tagName.toLowerCase() == "br") {
				text += "\n";
			} else {
				text += $(node).text();
			}
		}
	}
	window.alert(text);
}

function resetSpan(span_element) {
	var time = 3000;
	if (span_element.style.color == "red") {
		time = 5000;
	}
	setTimeout( function () { $(span_element).text(""); span_element=null; }, time);
}

function resizeBlocksInPairs(first_id, second_id) {
	var first_block = $("#" + first_id);
	var second_block = $("#" + second_id);
	var highest = Math.max(first_block.height(), second_block.height());

	var first_delta = highest - first_block.height();
	var second_delta = highest - second_block.height();
	first_block.height(highest+10);
	second_block.height(highest+10);

	var first_text = $("#" + first_id + " .block_text");
	var second_text = $("#" + second_id + " .block_text");
	first_text.height(first_text.height() + first_delta + 5);
	second_text.height(second_text.height() + second_delta + 5);
}

//=- WATERMARK

var WATERMARK_MSG = "Scrivi e premi invio";

function blurWatermark(id, message) {
	var watermark = document.getElementById(id);
	if (!watermark.value || watermark.value == WATERMARK_MSG) {
		watermark.style.color = "gray";
		watermark.style.fontStyle = "italic";
		if (message) {
			watermark.value = message;
		} else {
			watermark.value = WATERMARK_MSG;
		}
	}
}

function focusWatermark(id, message) {
	var watermark = document.getElementById(id);
	if (( message && watermark.value == WATERMARK_MSG)
	 || (!message && watermark.value == WATERMARK_MSG)) {
		watermark.style.color = "";
		watermark.style.fontStyle = "normal";
		watermark.value = "";
	}
}


//=- VARIE UTILITY

function log(message) {
	window.alert(message);
}

// returns true if the string is a valid email
String.prototype.isEmail = function (str) {
  if(isEmpty(str)) return false;
  var re = /^[^\s()<>@,;:\/]+@\w[\w\.-]+\.[a-z]{2,}$/i
  return re.test(str);
}

// returns true if the string only contains characters A-Z or a-z
String.prototype.isAlpha = function (str) {
  var re = /[^a-zA-Z]/g
  if (re.test(str)) return false;
  return true;
}

// returns true if the string only contains characters 0-9
String.prototype.isNumeric = function (str) {
  var re = /[\D]/g
  if (re.test(str)) return false;
  return true;
}

// returns true if the string only contains characters A-Z, a-z or 0-9
String.prototype.isAlphaNumeric = function (str) {
  var re = /[^a-zA-Z0-9]/g
  if (re.test(str)) return false;
  return true;
}

String.prototype.isLower = function (str) {
	for (i = 0; i < argument.length; i++) {
		c = argument.charCodeAt(i);
		if (c < 96 || c > 123) {
			return false;
		}
	}
	return true;
}

String.prototype.isUpper = function (str) {
	for (i = 0; i < argument.length; i++) {
		c = argument.charCodeAt(i);
		if (c < 64 || c > 91) {
			return false;
		}
	}
	return true;
}

String.prototype.startsWith = function (str) {
    return this.indexOf(str) == 0;
};

String.prototype.endsWith = function (str){
    return this.slice(-str.length) == str;
};

function leftTrim(string) {
	return string.replace(/^\s\s*/, '');
}

function rightTrim(string) {
	return string.replace(/\s\s*$/, '');
}

function trim(string) {
	return string.replace(/^\s\s*/, '').replace(/\s\s*$/, '');
}

function countdown(id) {
	var element = document.getElementById(id);
	var seconds = parseInt($(element).text());
	var suffix = false;
	if ($(element).text().lastIndexOf(" second") != -1) {
		suffix = true;
	}
	setTimeout(function () { doCountdown(element, seconds, suffix); }, 1000);

	function doCountdown(element, seconds, suffix) {
		seconds -= 1;
		if (seconds < 0) {
			return
		}
		if (suffix) {
			$(element).text(seconds + (seconds == 1 ? " secondo" : " secondi"));
		} else {
			$(element).text(seconds);
		}
		setTimeout(function () { doCountdown(element, seconds, suffix); }, 1000);
	}
}