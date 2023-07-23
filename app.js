let {PythonShell} = require('python-shell');
const fs = require('fs');
const path = require('path');
const nodeMailer = require('nodemailer');
const axios = require('axios');
const cron = require('node-cron');
require('dotenv').config();

const PORT = 8000;
const today = new Date().getDate() + '-' + (new Date().getMonth()+1) + '-' + new Date().getFullYear();



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
        to: ["theolpy@gmail.com", "cathylilingwai@gmail.com"],
        subject: `Stocks Check on ${today}`,
        html: `<h1>Please check the link </h1> 
                <br>
                <h2>${api_link}</h2>`
    });

    console.log("Email sent");
};

async function runStocksCheck() {

    let options = {
        scriptPath: path.join(__dirname+'/public'),
    }


    PythonShell.run('stock_buy.py', options, function (err) {
        console.log(err);
    }).then((result) => {
        console.log('Python Run Completed');
    }).catch((err) => {
        console.log(err);
    })
};

runStocksCheck();