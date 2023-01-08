import { mkdirSync, readdirSync, renameSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { parse } from 'node-html-parser';

import mp3addMeta from '../mp3/meta.js';
import mp3addCover from '../mp3/cover.js';
import { isOK } from './url.js';
import { getHTTPBody } from './url.js';
import { download } from './downloader.js';



// ES modules don't have __filename and __dirname constants, 
// unlike CommonJS modules which do. This is an ES module which 
// is why i define these constansts here.
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);



async function checkArgs(pageURL, resourceKey) {
    
    if (!await isOK(pageURL)) {
        console.log(`${pageURL} couldn\'t be reached. Try accessing it through a browser.\n`);
        return false;
    }

    if (!resourceKey || resourceKey.startsWith('https')) {
        console.log('Audio resource key missing. \nAdd a resource key to books.txt file as the first line.\n');
        return false;
    }

    if (!parse(await getHTTPBody(pageURL)).querySelector('*[data-bid]')) {
        console.log(`${pageURL} has no required data. It's possibly a book fragment or paid book.\n`); 
        return false;
    }
    
    return true;
}

/**
 * Returns the root directory of the app as a string where the 
 * path delimeter has been normalized to a forward slash.
 * @returns Root directory as a string.
 */
function getRootDir() {
    let parts = __dirname.split(__dirname.includes('\\') ? '\\' : '/');
    parts.pop();
    parts.pop();
    return parts.join('/');
}

/**
 * Creates and returns a subroot directory. By subroot directory 
 * i mean a directory which is in the root directory of the app.
 * @param {String} dirName Name of new subroot directory.
 * @returns Directory path as a string.
 */
function newSubRootDir(dirName) {
    const subroot = getRootDir() + '/' + dirName;
    mkdirSync(subroot, {recursive: true});
    return subroot;
}

/**
 * Adds metadata to split tracks and 
 * copies them to /temp/split/meta folder.
 * @param {String} dir Where the tracks are (/temp/split).
 * @param {Array<Object>} trackDataArray 
 * @returns Promise which resolves to true once done.
 */
async function addMeta(dir, trackDataArray) {
    let i = 1;
    for (const td of trackDataArray) {
        const mData = {
            Album: td.series ? td.series : td.album, 
            Author: td.authors, 
            Artist: td.performers, 
            Title: td.title, 
            Track: td.series ? td.trackIndex : i,
            Comment: 'Downloaded with https://github.com/alexmalkki/akniga-downloader'
        };
        await mp3addMeta(`${dir}/${td.title}.mp3`, mData);
        i++;
    }
    return true;
}

/**
 * Adds cover art to downloaded tracks.
 * @param {String} dir Where the tracks are (temp/split/meta).
 * @param {String} pageURL URL of the audiobook page.
 * @returns 
 */
async function addCover(dir, pageURL) {
    
    const src = parse(await getHTTPBody(pageURL))
    .querySelector('.cover__wrapper--image img').getAttribute('src');

    const imgName = src.split('/').pop();
    const trackNames = readdirSync(dir);

    await download(dir, src, {silent: true});

    for (const tName of trackNames) {
        await mp3addCover(`${dir}/${tName}`, `${dir}/${imgName}`)
    }

    return true;
}

/**
 * Moves audio tracks to the /audiobooks folder from /temp.
 * If there is only one track to move, album name becomes its name.
 * @param {String} from /temp/split/meta/cover
 * @param {String} to /audiobooks/albumName or /audiobooks depending on amount of tracks.
 * @returns Promise which resolves to true once done.
 */
async function moveTracks(from, to) {

    const tracks = readdirSync(from);
    const isSingle = tracks.length > 1 ? false : true;

    if (!isSingle) {
        mkdirSync(to, {recursive: true});
        for (const track of tracks) 
            renameSync(from + '/' + track, to + '/' + track);
        return true;
    }

    const parts = to.split('/');
    const album = parts.pop();
    const toBase = parts.join('/');

    renameSync(from + '/' + tracks[0], toBase + '/' + album + '.mp3');
    return true;
}

export { 
    checkArgs,
    getRootDir, 
    newSubRootDir, 
    addMeta,
    addCover,
    moveTracks
};
