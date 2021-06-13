import document from "document";
import { inbox } from "file-transfer";
import fs from "fs";

let epochText = document.getElementById("epoch");
let batchText = document.getElementById("batch");
let metricImg = document.getElementById("metric_img");
epochText.text = "Waiting...";


import { listDirSync } from "fs";
const listDir = listDirSync("/private/data");
do {
  const dirIter = listDir.next();
  if (dirIter.done) {
    break;
  }
  console.log(dirIter.value);
} while (true);


function emptyInbox(){
  console.log("cleanup");
  let fileName;
  while (fileName = inbox.nextFile()) {
    console.log(`/private/data/${fileName} cleaned`);
  }
  console.log("cleanup done");
}

// initially clean inbox
emptyInbox();

function processAllFiles() {
  
  console.log("DEV got new file");
  let fileName;
  while (fileName = inbox.nextFile()) {
    console.log(`/private/data/${fileName} is now available`);
    if (fileName) {
      let data = fs.readFileSync(fileName, "ascii"); //ascii
      
      if (fileName.split('.')[1] =="json") {
          data = JSON.parse(data)

        switch (data.action){
          case 'training_progress':
            console.log(`Received File: <${fileName}> ${data.training_id}`); 
            epochText.text = `Epoch: ${data.payload.epoch_iter}/${data.payload.epoch_total}`;
            batchText.text = `Batch (${data.payload.task}): ${data.payload.batch_iter}/${data.payload.batch_total}`;
            break;
          case 'new_stats':
            console.log(`inIF Received File: <${fileName}> ${data.training_id}`); 
            //metricImg.image  = `/private/data/metrics_${data.training_id}.png`;
            break;
        }
      }
      else {
        console.log(`DDDDD Received File: <${fileName}>`);
        let action = fileName.split('_')[0]
          
        switch(action) {
          case "metric":
            console.error(`MI Received File: <${fileName}>`);
            metricImg.image  = `/private/data/${fileName}`; //metricImg.href
            break;
        }
      }
      
    }
  }
}

inbox.addEventListener("newfile", processAllFiles);
