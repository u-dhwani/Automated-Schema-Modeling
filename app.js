// const fs = require('fs');
// const express = require('express');
// const app = express();

// app.get('/', (req, res) => {
//     // Read the contents of 'mongodb_data.txt' file
//     fs.readFile('mongodb_data.txt', 'utf8', (err, data) => {
//         if (err) {
//             res.status(500).send('Error reading the file.');
//         } else {
//             // Render the HTML template with the file content wrapped in <pre> tags
//             res.send(`
//                 <!DOCTYPE html>
//                 <html>
//                 <head>
//                     <title>Relationship Result</title>
//                 </head>
//                 <body>
//                     <h1>Relationship Result</h1>
//                     <pre>${data}</pre>
//                 </body>
//                 </html>
//             `);
//         }
//     });
// });

// app.listen(3000, () => {
//     console.log('Server is running on port 3000');
// });

// const express = require('express');
// const MongoClient = require('mongodb').MongoClient;
// const app = express();
// const mongoURL = 'mongodb://localhost:27017/database9';

// app.get('/', async (req, res) => {
//     try {
//         const client = await MongoClient.connect(mongoURL, { useUnifiedTopology: true });
//         const db = client.db();
//         const collectionNames = await db.listCollections().toArray();
        
//         // Extract collection names
//         const formattedCollections = collectionNames.map(collection => collection.name).join('\n');
        
//         // Render the HTML template with the collection names wrapped in <pre> tags
//         res.send(`
//             <!DOCTYPE html>
//             <html>
//             <head>
//                 <title>MongoDB Collections</title>
//             </head>
//             <body>
//                 <h1>MongoDB Collections</h1>
//                 <pre>${formattedCollections}</pre>
//             </body>
//             </html>
//         `);
//         client.close();
//     } catch (error) {
//         console.error(error);
//         res.status(500).send('An error occurred while fetching collections.');
//     }
// });

// app.listen(3000, () => {
//     console.log('Server is running on port 3000');
// });

const express = require('express');
const MongoClient = require('mongodb').MongoClient;
const app = express();
const mongoURL = 'mongodb://localhost:27017/database9';

app.get('/', async (req, res) => {
    try {
        const client = await MongoClient.connect(mongoURL, { useUnifiedTopology: true });
        const db = client.db();

        // Fetch collection names
        const collectionNames = (await db.listCollections().toArray()).map(collection => collection.name);

        // Fetch documents from each collection
        const collectionData = await Promise.all(collectionNames.map(async (collectionName) => {
            const collection = db.collection(collectionName);
            const documents = await collection.find({}).toArray();
            return { collectionName, documents };
        }));

        // Format and render the HTML template
        const content = collectionData.map(collection => `
            <h2>${collection.collectionName}</h2>
            <pre>${JSON.stringify(collection.documents, null, 2)}</pre>
        `).join('\n');

        res.send(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>MongoDB Collections and Documents</title>
            </head>
            <body>
                <h1>MongoDB Collections and Documents</h1>
                ${content}
            </body>
            </html>
        `);

        client.close();
    } catch (error) {
        console.error(error);
        res.status(500).send('An error occurred while fetching collections and documents.');
    }
});

app.listen(3000, () => {
    console.log('Server is running on port 3000');
});
