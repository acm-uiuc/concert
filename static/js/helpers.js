/**
* Collection of helper functions used within the front end
*/

/**
* Define string.format function
*/
if (!String.prototype.format) {
  String.prototype.format = function() {
    var args = arguments;
    return this.replace(/{(\d+)}/g, function(match, number) { 
      return typeof args[number] != 'undefined'
        ? args[number]
        : match
      ;
    });
  };
}

/**
* Get the location of a thumbnail given the media mrl
*/
function getThumbnailPath(mrl) {
    var parts = mrl.split("/");
    var filePath =  parts[parts.length - 1];
    var prefix = filePath.split('.')[0];
    return "static/thumbnails/" + prefix + ".jpg";
}

/**
* Converts seconds into mm:ss format
*/
function formatSeconds(time) {
    var minutes = Math.floor(time / 60);
    var seconds = time - minutes * 60;
    return str_pad_left(minutes,'0',2) + ':' + str_pad_left(seconds,'0',2);
}

/**
* Adds padding to left side of a string
*/
function str_pad_left(string,pad,length) {
    return (new Array(length+1).join(pad)+string).slice(-length);
}

/**
* Deterimines whether a string is a url based on regexs
*/
function isURL(str) {
  var pattern = new RegExp('^(https?:\\/\\/)?'+ // protocol
  '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.?)+[a-z]{2,}|'+ // domain name
  '((\\d{1,3}\\.){3}\\d{1,3}))'+ // OR ip (v4) address
  '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*'+ // port and path
  '(\\?[;&a-z\\d%_.~+=-]*)?'+ // query string
  '(\\#[-a-z\\d_]*)?$','i'); // fragment locator
  return pattern.test(str);
}