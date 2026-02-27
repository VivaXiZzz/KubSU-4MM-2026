/*function buildPayload(message) {
  return {
    url: message.url,
    title: message.title,
    content: message.content
  };
}*/

chrome.runtime.onMessage.addListener(async (message) => {
  console.log("собранные данные:", message);

  if (!message || message.type !== "view") {
    return;
  }
});