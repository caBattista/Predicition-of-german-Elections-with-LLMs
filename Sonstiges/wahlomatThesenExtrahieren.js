//Funktion wird auf der Seite des Wahlomats ausgeführt um die Fragen/Thesen zu extrahieren
function fragen_von_wahlomat_extrahieren(){
    //Einlesen der liste aus Thesen welche sich in glob. var. auf der Seite befindet
    let fragen_raw = window.WOMT_aThesen;
    //Format umwandeln in eine Liste aus Objekten
    let fragen_transformed = fragen_raw.map(item => ({
        titel: item[0][0],
        frage: item[0][1]
    }));
    //'fragen_transformed' in JSON-String umwandeln und in die Zwischenablage kopieren
    copy(JSON.stringify(fragen_transformed));
}