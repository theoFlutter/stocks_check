let {PythonShell} = require('python-shell');
const express = require('express');
const http = require('http');
const fs = require('fs');
const path = require('path');
const nodeMailer = require('nodemailer');
const axios = require('axios');
const cron = require('node-cron');
require('dotenv').config();

const app = express();
const server = http.createServer(app);

const PORT = 8000;
const today = new Date().getDate() + '-' + (new Date().getMonth()+1) + '-' + new Date().getFullYear();
const api_link = 'https://stocks-check.onrender.com';

app.use(express.static(path.join(__dirname)));

//Run stocks check python script



//Send the email
async function sendEmail(){

    const transporter = nodeMailer.createTransport({
        service:'gmail',
        auth:{
            user: "theo.flutter@gmail.com",
            pass: process.env.PASSWORD,
        }
    });

    transporter.sendMail({
        from: "theo.flutter@gmail.com",
        to: ["theolpy@gmail.com"],
        subject: `Stocks Check on ${today}`,
        html: `<h1>Please check the link </h1> 
                <br>
                <h2>${api_link}</h2>`
    });

    console.log("Email sent");
};

async function runStocksCheck() {

    PythonShell.run('stock_buy.py', null, function (err) {
        console.log(err);
    }).then((result) => {
        console.log('Python Run Completed');
    }).catch((err) => {
        console.log(err);
    }).then(()=>{
        sendEmail();
    });

};


//Run Schedule function
cron.schedule("*/10 * * * *", ()=>{
    axios.get(api_link+'/keepRun').then((res)=>{
        console.log("Keep running");
    });
})

cron.schedule("0 7 * * MON-FRI", async ()=>{
    runStocksCheck().then(()=>{
        sendEmail();
    });
});


//Routes
app.get('/keepRun', (req, res)=>{
    res.send("Keep running");
})

app.get('/', (req, res) => {
    res.writeHead(200, {"Content-Type": "text/html"});
    var readStream = fs.createReadStream('HK_MACD.html');
    readStream.pipe(res);
});


//Start the server
server.listen(PORT, (req, res)=>{
    console.log(`Server is running on port ${PORT}`);
})

