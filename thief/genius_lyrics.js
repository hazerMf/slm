import { getSong } from 'genius-lyrics-api';
import 'dotenv/config';

const options = {
    apiKey: process.env.genius_api,
    title: 'Posthumous Forgiveness',
    artist: 'Tame Impala',
    optimizeQuery: true
};

getSong(options)
    .then((song) => {
        if (song) {
            console.log("Found Song:", song.title);
            console.log("Lyrics URL:", song.url);
            console.log("Lyrics Text:", song.lyrics);
        }
    })
    .catch((err) => {
        if (err.response && err.response.status === 403) {
            console.error("Cloudflare blocked the scraper.");
        } else {
            console.error(err);
        }
    });

// API blocked, only provided song metadata