//Funktion wird auf der Seite des Wahlomats ausgeführt um die Fragen/Thesen zu extrahieren
function fragen_von_wahlomat_extrahieren() {
    //Einlesen der liste aus Thesen welche sich in glob. var. auf der Seite befindet
    let fragen_raw = window.WOMT_aThesen;
    //Format umwandeln in eine Liste aus Objekten
    let fragen_transformed = fragen_raw.map((item, i) => ({
        titel: item[0][0],
        frage: item[0][1],
        statements: parteien_statements_für_frage(i)
    }));
    //'fragen_transformed' in JSON-String umwandeln und in die Zwischenablage kopieren
    copy(JSON.stringify(fragen_transformed));
}

function parteien_statements_für_frage(frage_index) {
    let statements = window.WOMT_aThesenParteienText[frage_index];
    let parteien_raw = window.WOMT_aParteien;
    let parteien_entscheidungen_raw = window.WOMT_aThesenParteien;
    let statements_mit_partei = parteien_raw.map((item, i) => ({
        partei: item[0][1],
        statement: statements[i][0],
        entscheidung: entscheidung_umwandeln(parteien_entscheidungen_raw[frage_index][i])
    }));
    return statements_mit_partei;
}

function entscheidung_umwandeln(entscheidung) {
    if (entscheidung === "0") { return "neutral" }
    else if (entscheidung === "1") { return "stimme zu" }
    else if (entscheidung === "-1") { return "stimme nicht zu" }
}

//Funktion wird auf der Seite des Wahlomats ausgeführt um die Fragen/Thesen zu extrahieren
function parteien_von_wahlomat_extrahieren() {
    //Einlesen der liste aus Thesen welche sich in glob. var. auf der Seite befindet
    let parteien_raw = window.WOMT_aParteien;
    let parteien_beschreibung_raw = window.WOMT_aParteienBeschreibung;
    //Format umwandeln in eine Liste aus Objekten
    let parteien_transformed = parteien_raw.map((item, i) => ({
        kuerzel: item[0][1],
        titel: item[0][0],
        beschreibung: parteien_beschreibung_raw[i][0]
    }));
    //'fragen_transformed' in JSON-String umwandeln und in die Zwischenablage kopieren
    copy(JSON.stringify(parteien_transformed));
}