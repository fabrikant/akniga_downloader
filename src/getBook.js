import { checkArgs, newSubRootDir, addMeta, addCover, moveTracks } from "./utils/misc.js";
import { getResourceURL, getPageURLs } from "./utils/url.js";
import { getTrackDataArray } from "./utils/trackdata.js";
import { download } from "./utils/downloader.js";
import mp3split from "./mp3/split.js";
import { rmSync } from "fs";



async function getBook(pageURL, resourceKey) {

    if (pageURL.includes('/series/')) return await getSeries(pageURL, resourceKey);
    
    if (!await checkArgs(pageURL, resourceKey)) return false;

    const TEMP_DIR = newSubRootDir('temp');
    const BOOKS_DIR = newSubRootDir('audiobooks');

    console.log('Getting resource URL...');
    const resourceURL = await getResourceURL(pageURL, resourceKey)

    console.log('Getting tracks data...');
    const trackDataArray = await getTrackDataArray(pageURL);
    const album = trackDataArray[0].album;

    console.log(`Downloading "${album}"...`);
    await download(TEMP_DIR, resourceURL, {printURL: false});

    console.log('Splitting tracks...');
    await mp3split(TEMP_DIR + '/' + resourceURL.split('/').pop(), trackDataArray);

    console.log('Adding metadata...')
    await addMeta(TEMP_DIR + '/split', trackDataArray);

    console.log('Adding cover art...');
    await addCover(TEMP_DIR + '/split/meta', pageURL);

    console.log('Finishing...')
    await moveTracks(TEMP_DIR + '/split/meta/cover', BOOKS_DIR + '/' + album);
    rmSync(TEMP_DIR, {recursive: true});

    console.log(`Book "${album}" downloaded!\n`);
    return true;
}

async function getSeries(seriesURL, resourceKey) {

    const seriesName = decodeURI(seriesURL.split('/').pop());
    console.log(`Downloading series "${seriesName}"...`);

    console.log('Getting page URLs...\n');
    const pageURLs = await getPageURLs(seriesURL);

    for (const pageURL of pageURLs) 
        await getBook(pageURL, resourceKey);

    console.log(`Series "${seriesName}" downloaded!\n`)
    return true;
}

export default getBook;
