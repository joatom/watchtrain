import document from "document";
import { inbox } from "file-transfer";
import fs from "fs";
import { display } from "display";


let epochText = document.getElementById("epoch");
let batchText = document.getElementById("batch");
let epochAvg = document.getElementById("epoch_avg");

let metricImg = document.getElementById("metric_img");

let epochProg = document.getElementById("epoch_prog");
let batchProgT = document.getElementById("batch_prog_t");
let batchProgV = document.getElementById("batch_prog_v");

let lastEpochInfo = ""
let lastEpochTime = ""

let epochProgLength = 336
let batchProgTLength = 268
let batchProgVLength = 66



function emptyInbox(){
  console.log("cleanup");
  let fileName;
  while (fileName = inbox.nextFile()) {
    console.log(`/private/data/${fileName} cleaned`);
  }
  console.log("cleanup done");
}



function processAllFiles() {
  
  console.log("Companion recieved new file");
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
            lastEpochInfo = `Epoch: ${data.payload.epoch_iter}/${data.payload.epoch_total}`;
            epochText.text = lastEpochInfo + " " + lastEpochTime
            batchText.text = `Batch (${data.payload.task}): ${data.payload.batch_iter}/${data.payload.batch_total}`;
            epochProg.width = (epochProgLength / data.payload.epoch_total) * (data.payload.epoch_iter);
            if (data.payload.task == 'train'){
              batchProgV.width = 0
              batchProgT.width = (batchProgTLength / data.payload.batch_total) * (data.payload.batch_iter + 1)
            }
            else{
              batchProgT.width = batchProgTLength
              batchProgV.width = (batchProgVLength / data.payload.batch_total) * (data.payload.batch_iter + 1)
            }
            
            display.poke()
            break;
          case 'training_stats':
            console.log(`Received File: <${fileName}> ${data.training_id}`); 
            //epochAvg.text = `${data.payload.time}`;
            lastEpochTime = `(${data.payload.time})`;
            epochText.text = lastEpochInfo + " " + lastEpochTime
            display.poke()
            break;
        }
      }
      else {
        console.log(` Received File: <${fileName}>`);
        let action = fileName.split('_')[0]
          
        switch(action) {
          case "metric":
            console.error(`MI Received File: <${fileName}>`);
            metricImg.image  = `/private/data/${fileName}`; //metricImg.href
            display.poke()
            break;
        }
        
      }
      
    }
  }
}



/* init app */

epochText.text = "Waiting...";

// initially clean inbox
emptyInbox();

inbox.addEventListener("newfile", processAllFiles);
