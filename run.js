const { exec } = require('child_process');

// Path to the Flash.exe file
const flashExePath = 'Flash.exe';

exec(`"${flashExePath}"`, (error, stdout, stderr) => {
    if (error) {
        console.error(`exec error: ${error}`);
        return;
    }
    if (stdout) console.log(`stdout: ${stdout}`);
    if (stderr) console.error(`stderr: ${stderr}`);
});
