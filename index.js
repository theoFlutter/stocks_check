let {PythonShell} = require('python-shell');
const express = require('express');
const http = require('http');
const fs = require('fs');
const path = require('path');
const nodeMailer = require('nodemailer');
require('dotenv').config();

const app = express();

const PORT = 8000;

app.use(express.static(path.join(__dirname)));

//Run stocks check python script
async function runStocksCheck() {

    PythonShell.run('stock_buy.py', null, function (err) {
        console.log(err);
    }).then((result) => {
        console.log('Python Run Completed');
    }).catch((err) => {
        console.log(err);
    });

};


//Send the email
async function sendEmail(){

    const transporter = nodeMailer.createTransport({
        service:'gmail',
        auth:{
            user: "theo.flutter@gmail.com",
            pass: process.env.PASSWORD,
        }
    });

    let html = await fs.createReadStream('./HK_MACD.html', 'utf8');

    transporter.sendMail({
        from: "theo.flutter@gmail.com",
        to: ["theolpy@gmail.com"],
        subject: "Stocks",
        attachments:[{filename: 'HK_MACD.html', path: './HK_MACD.html'}],
    });

    console.log("Email sent");
};



http.createServer((req, res)=>{

    res.writeHead(200, {"Content-Type": "text/html"});
    var readStream = fs.createReadStream('HK_MACD.html');
    readStream.pipe(res);

}).listen(PORT);




console.log(`Server is running on port ${PORT}`);

//sendEmail();
// runStocksCheck();

// app.get('/', (req, res) => {
//     res.send("Loading page...");
//     res.sendFile(path.join(__dirname, 'HK_MACD.html'));
// });

// server((req, res) => {

// });

// server.listen(PORT, (req, res)=>{
//     console.log(`Server is running on port ${PORT}`);
// })