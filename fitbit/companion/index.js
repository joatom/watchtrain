import { outbox } from "file-transfer";
// https://dev.fitbit.com/blog/2018-05-09-introducing-the-imagepicker-and-image-api/
import { Image } from "image";
import { device } from "peer";
import { settingsStorage } from "settings";

settingsStorage.setItem("screenWidth", device.screen.width);
settingsStorage.setItem("screenHeight", device.screen.height);

function sendDataToDevice(action, data, ext) {
  console.log(`COMP Sending ${action}.${ext}...`);
  switch(ext){
    case 'json':
      var enc = new TextEncoder();
      outbox.enqueue(`${action}.${ext}`, enc.encode(data));
      break;
    case 'jpg':
      var img = Image.from(data.image);
      
      // "image/vnd.fitbit.txi" or "image/jpeg"
      var buffer = img.export("image/vnd.fitbit.txi" , {
                                          background: "#FFFFFF",
                                          quality: 40
                                        });
      outbox.enqueue(`${action}.${ext}`, buffer);
      break;
  }
}



//setTimeout(sendFile, 2000);

const trainUri = "http://192.168.0.47:8555"
const wsUri = "ws://192.168.0.47:8555/ws/watchtrain/watch/123"; //
const websocket = new WebSocket(wsUri);

websocket.addEventListener("open", onOpen);
websocket.addEventListener("close", onClose);
websocket.addEventListener("message", onMessage);
websocket.addEventListener("error", onError);

function onOpen(evt) {
   console.log("CONNECTED");
   //websocket.send('msg');
}

function onClose(evt) {
   console.log("DISCONNECTED");
}

function onMessage(evt) {
  var data = JSON.parse(evt.data)
  var action = data.action
  
  switch(action){
    case 'training_progress':
      sendDataToDevice(action, evt.data,'json')
      break;
      
    case 'metric_image':
      //sendDataToDevice(action, data, 'jpg')
      
      Image.from(`data:image/png;charset=utf-8;base64, ${data.image}`)
      .then(image =>
        image.export("image/jpeg", {
          background: "#FFFFFF",
          quality: 40
        })
      )
      .then(buffer => outbox.enqueue(`${action}_${data.training_id}_${data.epoch}.jpg`, buffer))
      .then(fileTransfer => {
        console.error(`Enqueued ${fileTransfer.name}`);
      });
      
      break;
        
    /*case 'new_stats':
      console.error(`##### ${trainUri}/${data.training_id}/img/metrics`)
      fetch(`${trainUri}/${data.training_id}/img/metrics`).then(function (response) {
        return response.arrayBuffer();
      }).then(img => {
        sendDataToDevice(`metrics_${data.training_id}`, img,'png')
      }).catch(err => {
        console.error(`Failure: ${err}`);
      });
      
      break;
    */
  }
}

function onError(evt) {
   console.error(`ERROR: ${evt.data}`);
}
