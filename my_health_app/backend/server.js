const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const port = process.env.PORT || 8000;

app.use(cors());
app.use(bodyParser.json());

// API endpoint
app.post('/api/predict', (req, res) => {
    const payload = JSON.stringify(req.body);
    
    // Spawn python child process
    const pythonProcess = spawn('python', ['predict_cli.py'], {
        cwd: __dirname
    });

    let dataOutput = '';
    let errorOutput = '';

    // Write JSON payload to stdin
    pythonProcess.stdin.write(payload);
    pythonProcess.stdin.end();

    pythonProcess.stdout.on('data', (data) => {
        dataOutput += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        errorOutput += data.toString();
    });

    pythonProcess.on('close', (code) => {
        if (code !== 0 && !dataOutput) {
            console.error(`Python process exited with code ${code}`);
            console.error(errorOutput);
            return res.status(500).json({ detail: `Python process error: ${errorOutput}` });
        }
        
        try {
            const result = JSON.parse(dataOutput);
            if (result.status === 'success') {
                return res.json({ status: "success", data: result.data });
            } else {
                return res.status(400).json({ detail: result.error || "Unknown error occurred in Python script." });
            }
        } catch (e) {
            console.error('Failed to parse Python output:', dataOutput);
            console.error('Python stderr:', errorOutput);
            return res.status(500).json({ detail: "Failed to parse prediction results." });
        }
    });
});

// Serve static frontend files
const frontendDir = path.join(__dirname, '../frontend/dist');
if (fs.existsSync(frontendDir)) {
    app.use(express.static(frontendDir));

    app.get('*', (req, res) => {
        const indexFile = path.join(frontendDir, 'index.html');
        if (fs.existsSync(indexFile)) {
            res.sendFile(indexFile);
        } else {
            res.status(404).send('<h1>Frontend not found</h1>');
        }
    });
}


app.listen(port, () => {
    console.log(`[INFO] Server running at http://localhost:${port}`);
});
