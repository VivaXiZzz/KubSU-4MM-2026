chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "sendData") {
        console.log("залутали заголовок", request.title);
    }
});
