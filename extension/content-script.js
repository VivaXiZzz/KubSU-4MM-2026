//const pagetitle = document.title
//console.log("Заголовок страницы:", pagetitle)

//chrome.runtime.sendMessage({action: "sendTitle", title: document.title})

window.addEventListener('load', () => {
    const data = {
        action: "sendData",
        title: window.document.title
        //headers: getAllHeaders(window)
    };
    browser.runtime.sendMessage(data);
});

//function getAllHeaders(window):{
    //const result = window.document.querySelectorAll('h1')
    //const result += window.document.querySelectorAll('h2')
//    return result
//}