import { outbox } from "file-transfer";
// https://dev.fitbit.com/blog/2018-05-09-introducing-the-imagepicker-and-image-api/
import { Image } from "image";

const trainUri = "http://192.168.0.47:8555"
const wsUri = "ws://192.168.0.47:8555/ws/watchtrain/watch/123"; //
const websocket = new WebSocket(wsUri);



function sendJsonToDevice(action, data) {
  console.log(`COMP Sending ${action}.json...`);
  var enc = new TextEncoder();
  outbox.enqueue(`${action}.json`, enc.encode(data));
}

function onOpen(evt) {
   console.log("CONNECTED");
}

function onClose(evt) {
   console.log("DISCONNECTED");
}

function onMessage(evt) {
  var data = JSON.parse(evt.data)
  var action = data.action
  
  switch(action){
    case 'training_progress':
      sendJsonToDevice(action, evt.data)
      break;
    
    case 'training_stats':
      sendJsonToDevice(action, evt.data)
      break;
      
    case 'metric_image':
      
      Image.from(`data:image/png;charset=utf-8;base64, ${data.image}`)
      .then(image =>
        image.export("image/jpeg", {
          background: "#FFFFFF",
          quality: 40
        })
      )
      .then(buffer => outbox.enqueue(`${action}_${data.training_id}_${data.epoch}.jpg`, buffer))
      .then(fileTransfer => {
        console.log(`Enqueued ${fileTransfer.name}`);
      });
      
      break;
        
  }
}

function onError(evt) {
   console.error(`ERROR: ${evt.data}`);
}


websocket.addEventListener("open", onOpen);
websocket.addEventListener("close", onClose);
websocket.addEventListener("message", onMessage);
websocket.addEventListener("error", onError);
